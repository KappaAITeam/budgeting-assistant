from fastapi import FastAPI
from app.routers import budget, advice
from app.utils.voice_input import get_voice_input

app = FastAPI(
    title="Budgeting and Financial Advice API",
    description="An API to generate structured budgets and financial advice using Langchain.",
    version="1.0.0"
)

# Register routers
app.include_router(budget.router)
app.include_router(advice.router)


@app.get("/", tags=["Root"])
async def root():
    """
    Welcome message for the API.
    """
    return {"message": "Welcome to the Budgeting and Financial Advice API!"}


@app.get("/voice-input", tags=["Voice Input"])
async def capture_voice():
    """
    Capture and transcribe voice input.
    """
    voice_text = get_voice_input()
    return {"transcribed_text": voice_text}
