import os
import io
import bcrypt
import re
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse,StreamingResponse
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from fastapi.middleware.cors import CORSMiddleware
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnableParallel, RunnableLambda
import pandas as pd
from dotenv import load_dotenv
from .models.model import *

# Load environment variables
load_dotenv(override=True)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq API
llm = ChatGroq(api_key=GROQ_API_KEY,
               model="llama-3.3-70b-versatile",
               temperature=0.2,
               max_retries=2)


# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define prompts
# Prompt to summarize key points from financial notes
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an expert financial Analyst."),
        ("human", "Give financial insight into  the following financial notes:\n\n{user_input}" \
         "Extract financial income from the insight"
         "List financial expenses from the insight"
         "List financial concerns about the financial insight")
    ]
)

income_prompt = ChatPromptTemplate.from_template(
    
    "Extract the income details from the following input: {user_input}"
)

expenses_prompt = ChatPromptTemplate.from_template(
    
    "List the different expense categories and their estimated amounts from this input: {user_input}"
)
concerns_prompt = ChatPromptTemplate.from_template(
    
    "Identify the financial concerns mentioned in this input: {user_input}"
)

#Runnable function to be use in parallel
def analyze_income(user_input):
    "Analyze user incomes"
    return income_prompt.format_prompt(user_input=user_input)

def analyze_expenses(user_input):
    "Analyze user expenses"
    return expenses_prompt.format_prompt(user_input=user_input)

def analyze_concerns(user_input):
    "Analyze user concerns"
    return concerns_prompt.format_prompt(user_input=user_input)

def financial_advice(concerns):
    """Generates financial advice based on concerns"""
    advice_prompt = f"Provide financial advice based on these concerns:\n {concerns}"
    return llm.invoke(advice_prompt).content

def budget_summary(income, expenses):
    """Generates structured budget summary"""
    summary_prompt = f"Create a structured budget with Income:\n {income}\n **Expenses:**\n {expenses}."
    return llm.invoke(summary_prompt).content

def format_output(user_input):
    format_prompt = ("Format this input to be injected into a webpage"
    "do not include any additional response but just the formatted input: "
    f"{user_input}")
    return llm.invoke(format_prompt).content

# Runnable chains for income, expenses and concerns 
income_branch_chain = (
    RunnableLambda(lambda x: analyze_income(x)) | llm | StrOutputParser()
)

expenses_branch_chain = (
    RunnableLambda(lambda x: analyze_expenses(x)) | llm | StrOutputParser()
)

concerns_branch_chain = (
    RunnableLambda(lambda x: analyze_concerns(x)) | llm | StrOutputParser()
)


# Combined parallel chain
chain = (
    prompt_template
    | llm
    | StrOutputParser()
    | RunnableParallel(branches={
        "income": income_branch_chain, 
        "expenses": expenses_branch_chain,
        "concerns": concerns_branch_chain
        

    })
    | RunnableLambda(lambda x: {"advice": financial_advice(x["branches"]["concerns"]), **x})
    | RunnableLambda(lambda x: {"summary": budget_summary(x["branches"]["income"], x["branches"]["expenses"]), **x})
    | RunnableLambda(lambda x: {"formatted_advice": format_output(x["advice"]), **x})
    | RunnableLambda(lambda x: {"formatted_summary": format_output(x["summary"]), **x})

)
#Function to convert income and expenses details into spreedsheets
def generate_budget_spreadsheet(income: str, expenses: str):
    """Generates an Excel spreadsheet from extracted budget details."""
    
    # Extract Income Details
    income_lines = income.split("\n")[1:]  # Skip the header line
    income_data = [line.split(": ") for line in income_lines if ": " in line]
    
    # Extract Expense Details
    expenses_lines = expenses.split("\n")[1:]  # Skip the header line
    expenses_data = [line.split(": ") for line in expenses_lines if ": " in line]

    # Create DataFrames
    df_income = pd.DataFrame(income_data, columns=["Source", "Amount"])
    df_expenses = pd.DataFrame(expenses_data, columns=["Category", "Amount"])
    
    # Convert Amounts to Numeric Values (Handle Ranges)
    
    def clean_amount(value):
        value = value.replace(",", "").strip()  # Remove commas and trim spaces
        # Extract all numeric values using regex
        numbers = re.findall(r'\d+', value)  # Finds all numbers in the string
        if not numbers:
            return 0  # Default to 0 if no numbers are found
        
        # Convert extracted numbers to integers
        numbers = list(map(int, numbers))
        if len(numbers) == 1:
            return numbers[0]  # Single value, return as-is
        if len(numbers) > 1:
            return sum(numbers) // len(numbers)  # If range or multiple values, return average
        return 0  # Fallback in case of unexpected input

    df_income["Amount"] = df_income["Amount"].apply(clean_amount)
    df_expenses["Amount"] = df_expenses["Amount"].apply(clean_amount)
    
    # Calculate Summary
    total_income = df_income["Amount"].sum()
    total_expenses = df_expenses["Amount"].sum()
    savings = total_income - total_expenses
    
    # Create Excel File
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_income.to_excel(writer, sheet_name="Income", index=False)
        df_expenses.to_excel(writer, sheet_name="Expenses", index=False)
        
        # Summary Sheet
        wb = writer.book
        ws = wb.create_sheet(title="Summary")
        ws.append(["Total Income", total_income])
        ws.append(["Total Expenses", total_expenses])
        ws.append(["Savings", savings])
    
    output.seek(0)  # Move to start for streaming
    
    return output  # Return file-like object


@app.post("/advice")
def get_anonymous_advice(request:JournalNote):
    #Provide advice for random users 
    result= chain.invoke({'user_input':request.message})
    advice= result["formatted_advice"]
    summary= result["formatted_summary"]
    
    return JSONResponse({
        "Financial Advice": advice,
        "Budget Summary": summary,
                
    })
    
@app.post("/download-budget")
def get_anonymous_budget(request:JournalNote):
    #Provide advice for random users 
    result= chain.invoke({'user_input':request.message})
            
    #Generate Excel file 
    excel_file=generate_budget_spreadsheet(income=result["branches"]["income"],
                                                  expenses=result["branches"]["expenses"])
    #for fastapi direct response link
    return StreamingResponse(excel_file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=budget.xlsx"})
    
    
def get_user(password:str,username:str):
    db= SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"user_id":user.id,"username":user.username}

    


#function to store extracted income, expenses, message
def store_advice_message(
    user_id: int, 
    journal_note: str, 
    income: str| None,
    expenses: str|None,
    advice: str|None,
    budget: str|None
    ):
    db = SessionLocal()
    try:
        if not advice.strip():  # Ensure ai advice message is not empty
            print("Warning: Attempted to store an empty Advice message.")
            return  # Exit function without storing
        
        # Create and add new chat entry
        _entry = FinanceJournal(user_id=user_id, journal_note=journal_note, 
                                ai_financial_advice=advice, ai_extracted_income=income,
                                ai_extracted_expenses=expenses, ai_budget_summary=budget)
        db.add(_entry)
        db.commit()
        db.refresh(_entry)  # Ensure the object is fully committed
        
        return _entry.id

          
    except Exception as e:
        db.rollback()  # Rollback transaction if there's an error
        print(f"Error storing advice message: {e}")
    
    finally:
        db.close()  # Ensure session is always closed.
        

@app.post("/user-advice")
def user_get_advice(request:UserJournalNote):
    #get user details
    _user = get_user(password=request.password, username=request.username)
    #Provide user with advice base on the finiancial journal note
    result= chain.invoke({'user_input':request.message})
    income=result["branches"]["income"] #income extracted from user finance journal
    expenses=result["branches"]["expenses"] #expenses extracted from user finance journal
    advice= result["advice"] # advice given
    summary= result["summary"] #budget summary
    
    #Save output results for downloadable excel spreadsheet 
    _save = store_advice_message(user_id=_user['user_id'], journal_note=request.message,income=income,
                                 expenses=expenses,advice=advice,budget=summary)
    return JSONResponse({
        "Financial Advice": advice,
        "Budget Summary": summary,
        "Financial history Id":_save
                
    })
    

#Retrieve previous conversation
def retrieve_advice_income_expenses(user_id: int, journal_id: str):
    db = SessionLocal()
    try:
        # Check if the user has previous advice
        query = db.query(FinanceJournal).filter(
            FinanceJournal.user_id == user_id,
            FinanceJournal.id == journal_id
        ).first()

        # Return empty response if no messages found
        if not query:
            return {"response": ""}

        # Format and return history
        return {
            "income":query.ai_extracted_income,
            "expenses":query.ai_extracted_expenses
        }
    
    finally:
        db.close()  # Ensure the session is closed    

@app.post("/create-budget-with-advice")
def create_user_budget_with_advice(request:RetrieveJournalNote):
    #Get user income and expenses from Financial advice
    details= retrieve_advice_income_expenses(user_id=request.user_id,journal_id=request.journal_id)
    
    #Generate Excel file 
    excel_file=generate_budget_spreadsheet(
        income=details["income"],
        expenses=details["expenses"]
        )
    #for fastapi direct response link
    return StreamingResponse(excel_file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=budget.xlsx"})
    
    
@app.post("/get-all-finance-record/advice")
def retrieve_user_financial_record(user_id):
    #Get all user income financial journal
    db = SessionLocal()
    try:
        # Check if the user has previous advice
        query = db.query(FinanceJournal).filter(
            FinanceJournal.user_id == user_id,
        ).all()

        # Return empty response if no messages found
        if not query:
            return {"response": ""}

        # Format and return history
        
        return query
        
    
    finally:
        db.close()  # Ensure the session is closed
    
        
#Function to create new user
@app.post("/register")
def register_user(request:CreateUser):
    db = SessionLocal()
    hash_password = bcrypt.hashpw(request.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    db_user = db.query(User).filter(User.username== request.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(username=request.username, hashed_password=hash_password, image=request.image,
                    first_name=request.first_name,last_name=request.last_name)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    
    return {"message": "User registered successfully"}

#function to authenticate user
@app.post("/login")
def login_user(form_data:OAuth2PasswordRequestForm =Depends()):
    #get user from database
    db = SessionLocal()
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not bcrypt.checkpw(form_data.password.encode("utf-8"), user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token_payload = {
        "username": user.username,
        "image": user.first_name,
        "user_id": user.id
        #"exp": datetime.datetime() + datetime.timedelta(hours=1)  # Token expires in 1 hour
    }
    #jwt can be use to manage data validity here
    
    return {"response": token_payload}