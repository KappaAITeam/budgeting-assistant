from fastapi import APIRouter, HTTPException, status
from app.models.advice import AdviceRequest, AdviceResponse

router = APIRouter(prefix="/api/advice", tags=["Advice"])


@router.post("/generate", response_model=AdviceResponse)
async def generate_advice(advice_request: AdviceRequest):
    """
    Generate financial advice based on user input.
    """
    try:
        # Placeholder for calling the advice service
        advice_response = {
            "advice": "Consider setting aside 20% of your monthly income for savings.",
            "suggestions": [
                "Track your daily expenses to identify saving opportunities.",
                "Automate your savings to ensure consistency.",
                "Diversify your investments to minimize risk."
            ]
        }
        return AdviceResponse(**advice_response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating advice: {str(e)}"
        )
