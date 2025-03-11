from pydantic import BaseModel, Field


class AdviceRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user.")
    prompt: str = Field(..., description="User's financial query or concern.")


class AdviceResponse(BaseModel):
    advice: str = Field(...,
                        description="Generated financial advice based on the prompt.")
    suggestions: list = Field(...,
                              description="List of actionable suggestions or tips.")
