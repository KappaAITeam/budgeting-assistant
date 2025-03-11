from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class Expense(BaseModel):
    category: str = Field(...,
                          description="Category of the expense (e.g., rent, groceries).")
    amount: float = Field(..., description="Expense amount.")


class Income(BaseModel):
    source: str = Field(...,
                        description="Income source (e.g., salary, investments).")
    amount: float = Field(..., description="Income amount.")


class BudgetRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the user.")
    incomes: List[Income] = Field(..., description="List of income sources.")
    expenses: List[Expense] = Field(..., description="List of expenses.")
    financial_goals: Optional[List[str]] = Field(
        None, description="Financial goals or concerns.")


class BudgetSummary(BaseModel):
    total_income: float = Field(..., description="Total calculated income.")
    total_expenses: float = Field(...,
                                  description="Total calculated expenses.")
    net_savings: float = Field(..., description="Net savings after expenses.")
    savings_rate: float = Field(..., description="Percentage of income saved.")


class BudgetResponse(BaseModel):
    summary: BudgetSummary = Field(..., description="Summary of the budget.")
    details: Dict[str, float] = Field(
        ..., description="Detailed breakdown of income and expenses.")
    message: str = Field(...,
                         description="Additional financial insights or advice.")
