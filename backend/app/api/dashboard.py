from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DatabaseSession

from app.api.dependencies import get_current_user, get_db
from app.models import User
from app.schemas.dashboard import (
    DashboardBudgetStatus,
    DashboardCategoryBreakdown,
    DashboardSummary,
    DashboardTrend,
)
from app.services.dashboard import budget_status, category_breakdown, monthly_trend, summary

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


def selected_month(month: date | None) -> date:
    return month or date.today().replace(day=1)


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    month: date | None = Query(default=None),
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DashboardSummary:
    return summary(database_session, user, selected_month(month))


@router.get("/category-breakdown", response_model=DashboardCategoryBreakdown)
def get_category_breakdown(
    month: date | None = Query(default=None),
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DashboardCategoryBreakdown:
    return category_breakdown(database_session, user, selected_month(month))


@router.get("/monthly-trend", response_model=DashboardTrend)
def get_monthly_trend(
    month: date | None = Query(default=None),
    months: int = Query(default=6, ge=1, le=24),
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DashboardTrend:
    return monthly_trend(database_session, user, selected_month(month), months)


@router.get("/budget-status", response_model=DashboardBudgetStatus)
def get_budget_status(
    month: date | None = Query(default=None),
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DashboardBudgetStatus:
    return budget_status(database_session, user, selected_month(month))
