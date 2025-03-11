from app.models.budget import BudgetRequest, BudgetResponse


def generate_budget(budget_request: BudgetRequest) -> BudgetResponse:
    """
    Generate a structured budget from the given request.
    Placeholder for the actual budget generation logic.
    """
    # Placeholder response for now
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
