import os
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine,URL, Column, Integer, String, Text, ForeignKey, Date
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import SQLAlchemyError

#Database setup
#DATABASE_URL=URL.create("sqlite",host="localhost",database="chat_history.db")
DATABASE_URL="sqlite:///financialjournal.db"
engine = create_engine(DATABASE_URL,connect_args={"check_same_thread": False})
SessionLocal=sessionmaker(bind=engine, autoflush=False,autocommit=False)

#SQLAlchemy ORM model
Base= declarative_base()


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    username= Column(String,unique=True, index=True)
    first_name= Column(String)
    last_name= Column(String)
    image=Column(String)
    hashed_password= Column(String)

class FinanceJournal(Base):
    __tablename__ = "finance_journal" 
    
    id = Column(Integer,primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    journal_note= Column(String)
    ai_extracted_income= Column(String)
    ai_extracted_expenses= Column(String)
    ai_financial_advice= Column(String)
    ai_budget_summary= Column(String)
    
        
    user= relationship("User")

  
        
#Create Tables
Base.metadata.create_all(bind=engine)

#OAuth2 for authentication
oauth2_scheme =OAuth2PasswordBearer(tokenUrl="Login")

#pydantic models
class CreateUser(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    image: str| None

class UserJournalNote(BaseModel):
    username: str
    password: str
    message: str


class RetrieveJournalNote(BaseModel):
    journal_id: str
    user_id: str 
    
        
class JournalNote(BaseModel):
    message: str    
    
 
