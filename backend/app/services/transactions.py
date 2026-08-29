from datetime import date
from math import ceil
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session as DatabaseSession

from app.models import Category, Transaction, User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransactionSort,
    TransactionUpdate,
)


class TransactionError(ValueError):
    pass


def _get_category(database_session: DatabaseSession, category_id: UUID) -> Category:
    category = database_session.get(Category, category_id)
    if category is None or not category.is_active:
        raise TransactionError("Category was not found")
    return category


def _validate_category_type(category: Category, transaction_type: str) -> None:
    if category.type.value != transaction_type:
        raise TransactionError("Category type must match transaction type")


def create_transaction(
    database_session: DatabaseSession, user: User, payload: TransactionCreate
) -> Transaction:
    category = _get_category(database_session, payload.category_id)
    _validate_category_type(category, payload.type.value)
    transaction = Transaction(user_id=user.id, **payload.model_dump())
    database_session.add(transaction)
    database_session.commit()
    database_session.refresh(transaction)
    return transaction


def get_transaction(
    database_session: DatabaseSession, user: User, transaction_id: UUID
) -> Transaction | None:
    return database_session.scalar(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == user.id)
    )


def list_transactions(
    database_session: DatabaseSession,
    user: User,
    *,
    page: int,
    page_size: int,
    transaction_type: str | None,
    category_id: UUID | None,
    start_date: date | None,
    end_date: date | None,
    search: str | None,
    sort: TransactionSort,
) -> TransactionListResponse:
    filters = [Transaction.user_id == user.id]
    if transaction_type is not None:
        filters.append(Transaction.type == transaction_type)
    if category_id is not None:
        filters.append(Transaction.category_id == category_id)
    if start_date is not None:
        filters.append(Transaction.transaction_date >= start_date)
    if end_date is not None:
        filters.append(Transaction.transaction_date <= end_date)
    if search:
        filters.append(Transaction.description.ilike(f"%{search}%"))

    ordering = {
        TransactionSort.NEWEST: (
            Transaction.transaction_date.desc(),
            Transaction.created_at.desc(),
        ),
        TransactionSort.OLDEST: (Transaction.transaction_date.asc(), Transaction.created_at.asc()),
        TransactionSort.HIGHEST_AMOUNT: (Transaction.amount.desc(), Transaction.created_at.desc()),
        TransactionSort.LOWEST_AMOUNT: (Transaction.amount.asc(), Transaction.created_at.asc()),
    }[sort]
    query: Select[tuple[Transaction]] = (
        select(Transaction)
        .where(*filters)
        .order_by(*ordering)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = list(database_session.scalars(query))
    total = (
        database_session.scalar(select(func.count()).select_from(Transaction).where(*filters)) or 0
    )
    return TransactionListResponse(
        items=[TransactionResponse.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=ceil(total / page_size) if total else 0,
    )


def update_transaction(
    database_session: DatabaseSession,
    user: User,
    transaction_id: UUID,
    payload: TransactionUpdate,
) -> Transaction | None:
    transaction = get_transaction(database_session, user, transaction_id)
    if transaction is None:
        return None

    values = payload.model_dump(exclude_unset=True)
    category_id = values.get("category_id", transaction.category_id)
    transaction_type = values.get("type", transaction.type)
    category = _get_category(database_session, category_id)
    _validate_category_type(category, transaction_type.value)
    for field, value in values.items():
        setattr(transaction, field, value)

    database_session.commit()
    database_session.refresh(transaction)
    return transaction


def delete_transaction(database_session: DatabaseSession, user: User, transaction_id: UUID) -> bool:
    transaction = get_transaction(database_session, user, transaction_id)
    if transaction is None:
        return False
    database_session.delete(transaction)
    database_session.commit()
    return True
