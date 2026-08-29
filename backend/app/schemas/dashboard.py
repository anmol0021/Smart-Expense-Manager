from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.schemas.budget import BudgetResponse


class DashboardSummary(BaseModel):
    month: date
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal
    savings_rate: Decimal | None


class CategorySpending(BaseModel):
    category_id: UUID
    category_name: str
    amount: Decimal


class MonthlyExpense(BaseModel):
    month: date
    amount: Decimal


class DashboardCategoryBreakdown(BaseModel):
    month: date
    categories: list[CategorySpending]


class DashboardTrend(BaseModel):
    start_month: date
    end_month: date
    months: list[MonthlyExpense]


class DashboardBudgetStatus(BaseModel):
    month: date
    budgets: list[BudgetResponse]
