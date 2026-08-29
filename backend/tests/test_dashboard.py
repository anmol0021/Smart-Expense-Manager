from collections.abc import Generator
from datetime import date
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.db.base import Base
from app.main import app
from app.models import Category, CategoryType

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, _connection_record):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


Base.metadata.create_all(engine)
with DatabaseSession(engine) as database_session:
    database_session.add_all(
        [
            Category(
                id=UUID("00000000-0000-0000-0000-000000000101"),
                name="Food",
                type=CategoryType.EXPENSE,
            ),
            Category(
                id=UUID("00000000-0000-0000-0000-000000000001"),
                name="Salary",
                type=CategoryType.INCOME,
            ),
        ]
    )
    database_session.commit()


def override_get_db() -> Generator[DatabaseSession, None, None]:
    with DatabaseSession(engine) as database_session:
        yield database_session


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)
month = date.today().replace(day=1)


def authenticate(email: str) -> None:
    payload = {"name": "Dashboard User", "email": email, "password": "StrongPassword123!"}
    client.post("/api/v1/auth/register", json=payload)
    client.post("/api/v1/auth/login", json=payload)


def test_dashboard_aggregates_month_and_trend() -> None:
    authenticate("dashboard@example.com")
    transaction_date = month.replace(day=15).isoformat()
    for transaction_type, category_id, amount in (
        ("INCOME", "00000000-0000-0000-0000-000000000001", "1000.00"),
        ("EXPENSE", "00000000-0000-0000-0000-000000000101", "400.00"),
    ):
        response = client.post(
            "/api/v1/transactions",
            json={
                "type": transaction_type,
                "amount": amount,
                "category_id": category_id,
                "transaction_date": transaction_date,
            },
        )
        assert response.status_code == 201

    month_query = month.isoformat()
    summary = client.get(f"/api/v1/dashboard/summary?month={month_query}")
    assert summary.status_code == 200
    assert summary.json()["total_income"] == "1000.00"
    assert summary.json()["total_expenses"] == "400.00"
    assert summary.json()["balance"] == "600.00"
    assert summary.json()["savings_rate"] == "60.00"

    breakdown = client.get(f"/api/v1/dashboard/category-breakdown?month={month_query}")
    assert breakdown.json()["categories"][0]["category_name"] == "Food"
    assert breakdown.json()["categories"][0]["amount"] == "400.00"

    trend = client.get(f"/api/v1/dashboard/monthly-trend?month={month_query}&months=3")
    assert trend.status_code == 200
    assert len(trend.json()["months"]) == 3
    assert trend.json()["months"][-1]["amount"] == "400.00"


def test_zero_income_returns_null_savings_rate() -> None:
    authenticate("empty-dashboard@example.com")
    response = client.get(f"/api/v1/dashboard/summary?month={month.isoformat()}")

    assert response.status_code == 200
    assert response.json()["total_income"] == "0.00"
    assert response.json()["savings_rate"] is None


def test_active_categories_are_database_backed() -> None:
    authenticate("categories@example.com")
    response = client.get("/api/v1/categories?type=EXPENSE")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Food"
    assert response.json()[0]["type"] == "EXPENSE"
