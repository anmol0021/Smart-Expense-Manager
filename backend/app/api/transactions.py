from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session as DatabaseSession

from app.api.dependencies import get_current_user, get_db
from app.models import TransactionType, User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransactionSort,
    TransactionUpdate,
)
from app.services.transactions import (
    TransactionError,
    create_transaction,
    delete_transaction,
    get_transaction,
    list_transactions,
    update_transaction,
)

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create(
    payload: TransactionCreate,
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TransactionResponse:
    try:
        return create_transaction(database_session, user, payload)
    except TransactionError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.get("", response_model=TransactionListResponse)
def list_all(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    transaction_type: TransactionType | None = Query(default=None, alias="type"),
    category_id: UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    search: str | None = Query(default=None, max_length=255),
    sort: TransactionSort = TransactionSort.NEWEST,
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TransactionListResponse:
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must not be after end date")
    return list_transactions(
        database_session,
        user,
        page=page,
        page_size=page_size,
        transaction_type=transaction_type.value if transaction_type else None,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
        search=search,
        sort=sort,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_one(
    transaction_id: UUID,
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TransactionResponse:
    transaction = get_transaction(database_session, user, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction was not found")
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update(
    transaction_id: UUID,
    payload: TransactionUpdate,
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> TransactionResponse:
    try:
        transaction = update_transaction(database_session, user, transaction_id, payload)
    except TransactionError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction was not found")
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    transaction_id: UUID,
    database_session: DatabaseSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Response:
    if not delete_transaction(database_session, user, transaction_id):
        raise HTTPException(status_code=404, detail="Transaction was not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
