from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session as DatabaseSession

from app.api.dependencies import get_current_user, get_db
from app.models import User
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate
from app.services.budgets import (
    BudgetError,
    create_budget,
    delete_budget,
    get_budget,
    list_budgets,
    to_response,
    update_budget,
)

router = APIRouter(prefix="/api/v1/budgets", tags=["budgets"])


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create(
    payload: BudgetCreate,
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> BudgetResponse:
    try:
        return create_budget(database_session, user, payload)
    except BudgetError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("", response_model=list[BudgetResponse])
def list_all(
    month: date | None = Query(default=None),
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[BudgetResponse]:
    if month is not None and month.day != 1:
        raise HTTPException(status_code=422, detail="Month must be the first day of the month")
    return list_budgets(database_session, user, month)


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_one(
    budget_id: UUID,
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> BudgetResponse:
    budget = get_budget(database_session, user, budget_id)
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget was not found")
    return to_response(database_session, budget)


@router.patch("/{budget_id}", response_model=BudgetResponse)
def update(
    budget_id: UUID,
    payload: BudgetUpdate,
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> BudgetResponse:
    try:
        budget = update_budget(database_session, user, budget_id, payload)
    except BudgetError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget was not found")
    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    budget_id: UUID,
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    if not delete_budget(database_session, user, budget_id):
        raise HTTPException(status_code=404, detail="Budget was not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
