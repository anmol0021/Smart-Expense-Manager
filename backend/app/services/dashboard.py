from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session as DatabaseSession

from app.models import Category, Transaction, TransactionType, User
from app.schemas.dashboard import (
    CategorySpending,
    DashboardBudgetStatus,
    DashboardCategoryBreakdown,
    DashboardSummary,
    DashboardTrend,
    MonthlyExpense,
)
from app.services.budgets import list_budgets

MONEY = Decimal("0.01")


def month_start(value: date) -> date:
    return date(value.year, value.month, 1)


def month_end(value: date) -> date:
    return date(value.year, value.month, monthrange(value.year, value.month)[1])


def shift_month(value: date, offset: int) -> date:
    month_index = value.year * 12 + value.month - 1 + offset
    return date(month_index // 12, month_index % 12 + 1, 1)


def decimal_amount(value: object) -> Decimal:
    return Decimal(str(value or 0)).quantize(MONEY)


def summary(database_session: DatabaseSession, user: User, month: date) -> DashboardSummary:
    month = month_start(month)
    income = database_session.scalar(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.INCOME,
            Transaction.transaction_date.between(month, month_end(month)),
        )
    )
    expenses = database_session.scalar(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.transaction_date.between(month, month_end(month)),
        )
    )
    total_income = decimal_amount(income)
    total_expenses = decimal_amount(expenses)
    balance = (total_income - total_expenses).quantize(MONEY)
    savings_rate = (
        ((balance / total_income) * Decimal("100")).quantize(MONEY) if total_income else None
    )
    return DashboardSummary(
        month=month,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        savings_rate=savings_rate,
    )


def category_breakdown(
    database_session: DatabaseSession, user: User, month: date
) -> DashboardCategoryBreakdown:
    month = month_start(month)
    rows = database_session.execute(
        select(Category.id, Category.name, func.sum(Transaction.amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.transaction_date.between(month, month_end(month)),
        )
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Transaction.amount).desc())
    )
    return DashboardCategoryBreakdown(
        month=month,
        categories=[
            CategorySpending(
                category_id=category_id,
                category_name=category_name,
                amount=decimal_amount(amount),
            )
            for category_id, category_name, amount in rows
        ],
    )


def monthly_trend(
    database_session: DatabaseSession, user: User, end_month: date, months: int = 6
) -> DashboardTrend:
    end_month = month_start(end_month)
    start_month = shift_month(end_month, -(months - 1))
    transactions = database_session.scalars(
        select(Transaction).where(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.transaction_date.between(start_month, month_end(end_month)),
        )
    )
    totals = {shift_month(start_month, offset): Decimal("0.00") for offset in range(months)}
    for transaction in transactions:
        key = month_start(transaction.transaction_date)
        totals[key] = totals.get(key, Decimal("0.00")) + transaction.amount
    return DashboardTrend(
        start_month=start_month,
        end_month=end_month,
        months=[
            MonthlyExpense(month=month, amount=amount.quantize(MONEY))
            for month, amount in totals.items()
        ],
    )


def budget_status(
    database_session: DatabaseSession, user: User, month: date
) -> DashboardBudgetStatus:
    month = month_start(month)
    return DashboardBudgetStatus(month=month, budgets=list_budgets(database_session, user, month))
