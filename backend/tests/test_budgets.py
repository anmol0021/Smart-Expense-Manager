from collections.abc import Generator
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.db.base import Base
from app.main import app
from app.models import Category, CategoryType
from app.schemas.budget import BudgetStatus
from app.services.budgets import classify_budget

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, _connection_record):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


Base.metadata.create_all(engine)
with DatabaseSession(engine) as database_session:
    database_session.add(
        Category(
            id=UUID("00000000-0000-0000-0000-000000000101"), name="Food", type=CategoryType.EXPENSE
        )
    )
    database_session.commit()


def override_get_db() -> Generator[DatabaseSession, None, None]:
    with DatabaseSession(engine) as database_session:
        yield database_session


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def authenticate() -> None:
    payload = {
        "name": "Budget Test User",
        "email": "budget-test@example.com",
        "password": "StrongPassword123!",
    }
    client.post("/api/v1/auth/register", json=payload)
    client.post("/api/v1/auth/login", json=payload)


def test_budget_status_boundaries() -> None:
    assert classify_budget(Decimal("69.99")) == BudgetStatus.NORMAL
    assert classify_budget(Decimal("70")) == BudgetStatus.WARNING
    assert classify_budget(Decimal("89.99")) == BudgetStatus.WARNING
    assert classify_budget(Decimal("90")) == BudgetStatus.CRITICAL
    assert classify_budget(Decimal("99.99")) == BudgetStatus.CRITICAL
    assert classify_budget(Decimal("100")) == BudgetStatus.EXCEEDED


def test_budget_crud_and_utilization() -> None:
    authenticate()
    response = client.post(
        "/api/v1/budgets",
        json={
            "category_id": "00000000-0000-0000-0000-000000000101",
            "month": "2026-08-01",
            "amount": "1000.00",
        },
    )
    assert response.status_code == 201
    budget_id = response.json()["id"]
    expense_response = client.post(
        "/api/v1/transactions",
        json={
            "type": "EXPENSE",
            "amount": "750.00",
            "category_id": "00000000-0000-0000-0000-000000000101",
            "description": "Budget test expense",
            "transaction_date": "2026-08-15",
        },
    )
    assert expense_response.status_code == 201
    status_response = client.get(f"/api/v1/budgets/{budget_id}")
    assert status_response.json()["spent"] == "750.00"
    assert status_response.json()["remaining"] == "250.00"
    assert status_response.json()["utilization"] == "75.00"
    assert status_response.json()["status"] == "WARNING"

    duplicate = client.post(
        "/api/v1/budgets",
        json={
            "category_id": "00000000-0000-0000-0000-000000000101",
            "month": "2026-08-01",
            "amount": "1200.00",
        },
    )
    assert duplicate.status_code == 409

    invalid_month = client.post(
        "/api/v1/budgets",
        json={
            "category_id": "00000000-0000-0000-0000-000000000101",
            "month": "2026-08-02",
            "amount": "1000.00",
        },
    )
    assert invalid_month.status_code == 422

    delete_response = client.delete(f"/api/v1/budgets/{budget_id}")
    assert delete_response.status_code == 204


def test_zero_budget_is_rejected() -> None:
    authenticate()
    response = client.post(
        "/api/v1/budgets",
        json={
            "category_id": "00000000-0000-0000-0000-000000000101",
            "month": date(2026, 9, 1).isoformat(),
            "amount": "0.00",
        },
    )
    assert response.status_code == 422
