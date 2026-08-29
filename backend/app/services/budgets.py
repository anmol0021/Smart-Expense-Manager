from calendar import monthrange
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session as DatabaseSession

from app.models import Budget, Category, CategoryType, Transaction, TransactionType, User
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetStatus, BudgetUpdate

MONEY = Decimal("0.01")


class BudgetError(ValueError):
    pass


def classify_budget(utilization: Decimal) -> BudgetStatus:
    if utilization >= Decimal("100"):
        return BudgetStatus.EXCEEDED
    if utilization >= Decimal("90"):
        return BudgetStatus.CRITICAL
    if utilization >= Decimal("70"):
        return BudgetStatus.WARNING
    return BudgetStatus.NORMAL


def _get_expense_category(database_session: DatabaseSession, category_id: UUID) -> Category:
    category = database_session.get(Category, category_id)
    if category is None or not category.is_active or category.type != CategoryType.EXPENSE:
        raise BudgetError("Budget category was not found")
    return category


def _month_end(month: date) -> date:
    return date(month.year, month.month, monthrange(month.year, month.month)[1])


def _spent_for_budget(database_session: DatabaseSession, budget: Budget) -> Decimal:
    spent = database_session.scalar(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == budget.user_id,
            Transaction.category_id == budget.category_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.transaction_date >= budget.month,
            Transaction.transaction_date <= _month_end(budget.month),
        )
    )
    return Decimal(str(spent or 0)).quantize(MONEY)


def to_response(database_session: DatabaseSession, budget: Budget) -> BudgetResponse:
    spent = _spent_for_budget(database_session, budget)
    remaining = (budget.amount - spent).quantize(MONEY)
    utilization = ((spent / budget.amount) * Decimal("100")).quantize(MONEY, rounding=ROUND_HALF_UP)
    return BudgetResponse(
        id=budget.id,
        user_id=budget.user_id,
        category_id=budget.category_id,
        month=budget.month,
        amount=budget.amount,
        spent=spent,
        remaining=remaining,
        utilization=utilization,
        status=classify_budget(utilization),
    )


def create_budget(
    database_session: DatabaseSession, user: User, payload: BudgetCreate
) -> BudgetResponse:
    _get_expense_category(database_session, payload.category_id)
    if database_session.scalar(
        select(Budget).where(
            Budget.user_id == user.id,
            Budget.category_id == payload.category_id,
            Budget.month == payload.month,
        )
    ):
        raise BudgetError("A budget already exists for this category and month")
    budget = Budget(user_id=user.id, **payload.model_dump())
    database_session.add(budget)
    database_session.commit()
    database_session.refresh(budget)
    return to_response(database_session, budget)


def list_budgets(
    database_session: DatabaseSession, user: User, month: date | None = None
) -> list[BudgetResponse]:
    query = select(Budget).where(Budget.user_id == user.id).order_by(Budget.month.desc())
    if month is not None:
        query = query.where(Budget.month == month)
    return [to_response(database_session, budget) for budget in database_session.scalars(query)]


def get_budget(database_session: DatabaseSession, user: User, budget_id: UUID) -> Budget | None:
    return database_session.scalar(
        select(Budget).where(Budget.id == budget_id, Budget.user_id == user.id)
    )


def update_budget(
    database_session: DatabaseSession,
    user: User,
    budget_id: UUID,
    payload: BudgetUpdate,
) -> BudgetResponse | None:
    budget = get_budget(database_session, user, budget_id)
    if budget is None:
        return None
    values = payload.model_dump(exclude_unset=True)
    category_id = values.get("category_id", budget.category_id)
    month = values.get("month", budget.month)
    _get_expense_category(database_session, category_id)
    duplicate = database_session.scalar(
        select(Budget).where(
            Budget.user_id == user.id,
            Budget.category_id == category_id,
            Budget.month == month,
            Budget.id != budget.id,
        )
    )
    if duplicate:
        raise BudgetError("A budget already exists for this category and month")
    for field, value in values.items():
        setattr(budget, field, value)
    database_session.commit()
    database_session.refresh(budget)
    return to_response(database_session, budget)


def delete_budget(database_session: DatabaseSession, user: User, budget_id: UUID) -> bool:
    budget = get_budget(database_session, user, budget_id)
    if budget is None:
        return False
    database_session.delete(budget)
    database_session.commit()
    return True
