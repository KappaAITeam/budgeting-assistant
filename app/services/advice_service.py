from app.models.advice import AdviceRequest, AdviceResponse


def generate_advice(advice_request: AdviceRequest) -> AdviceResponse:
    """
    Generate financial advice based on user input.
    Placeholder for the actual advice generation logic.
    """
    # Placeholder response for now
    advice_response = {
        "advice": "Consider setting aside 20% of your monthly income for savings.",
        "suggestions": [
            "Track your daily expenses to identify saving opportunities.",
            "Automate your savings to ensure consistency.",
            "Diversify your investments to minimize risk."
        ]
    }
    return AdviceResponse(**advice_response)
