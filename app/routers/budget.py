from fastapi import APIRouter, HTTPException, status
from app.models.budget import BudgetRequest, BudgetResponse

router = APIRouter(prefix="/api/budget", tags=["Budget"])


@router.post("/generate", response_model=BudgetResponse)
async def generate_budget(budget_request: BudgetRequest):
    """
    Generate a structured budget based on income and expenses.
    """
    try:
        # Placeholder for calling the budgeting service
        budget_response = {
            "summary": {
                "total_income": 5000.0,
                "total_expenses": 3000.0,
                "net_savings": 2000.0,
                "savings_rate": 40.0
            },
            "details": {
                "rent": 1200.0,
                "groceries": 400.0,
                "salary": 5000.0
            },
            "message": "You are saving 40% of your income. Good job!"
        }
        return BudgetResponse(**budget_response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating budget: {str(e)}"
        )
