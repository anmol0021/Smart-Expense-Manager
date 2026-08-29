from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DatabaseSession

from app.db.base import Base
from app.models import Budget, Category, CategoryType, Transaction, TransactionType, User


@pytest.fixture
def database_session():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with DatabaseSession(engine) as session:
        yield session
    engine.dispose()


def create_user_and_category(database_session: DatabaseSession) -> tuple[User, Category]:
    user = User(name="Test User", email=f"{uuid4()}@example.com", password_hash="hash")
    category = Category(name="Food", type=CategoryType.EXPENSE)
    database_session.add_all([user, category])
    database_session.commit()
    return user, category


def test_transaction_amount_is_decimal(database_session: DatabaseSession) -> None:
    user, category = create_user_and_category(database_session)
    transaction = Transaction(
        user_id=user.id,
        category_id=category.id,
        type=TransactionType.EXPENSE,
        amount=Decimal("100.50"),
        transaction_date=date(2026, 8, 28),
    )

    database_session.add(transaction)
    database_session.commit()
    database_session.refresh(transaction)

    assert transaction.amount == Decimal("100.50")


def test_negative_transaction_amount_is_rejected(database_session: DatabaseSession) -> None:
    user, category = create_user_and_category(database_session)
    database_session.add(
        Transaction(
            user_id=user.id,
            category_id=category.id,
            type=TransactionType.EXPENSE,
            amount=Decimal("-1.00"),
            transaction_date=date(2026, 8, 28),
        )
    )

    with pytest.raises(IntegrityError):
        database_session.commit()


def test_duplicate_budget_for_user_category_month_is_rejected(
    database_session: DatabaseSession,
) -> None:
    user, category = create_user_and_category(database_session)
    month = date(2026, 8, 1)
    database_session.add_all(
        [
            Budget(
                user_id=user.id, category_id=category.id, month=month, amount=Decimal("1000.00")
            ),
            Budget(
                user_id=user.id, category_id=category.id, month=month, amount=Decimal("1200.00")
            ),
        ]
    )

    with pytest.raises(IntegrityError):
        database_session.commit()
