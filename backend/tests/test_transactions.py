from collections.abc import Generator
from datetime import date, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.db.base import Base
from app.main import app
from app.models import Category, CategoryType

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


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


def authenticate() -> None:
    payload = {
        "name": "Transaction Test User",
        "email": "transaction-test@example.com",
        "password": "StrongPassword123!",
    }
    client.post("/api/v1/auth/register", json=payload)
    client.post("/api/v1/auth/login", json=payload)


def test_transaction_crud_and_filters() -> None:
    authenticate()
    today = date.today().isoformat()
    create_response = client.post(
        "/api/v1/transactions",
        json={
            "type": "EXPENSE",
            "amount": "100.50",
            "category_id": "00000000-0000-0000-0000-000000000101",
            "description": "Amazon order",
            "transaction_date": today,
        },
    )

    assert create_response.status_code == 201
    transaction_id = create_response.json()["id"]
    assert create_response.json()["amount"] == "100.50"

    list_response = client.get("/api/v1/transactions?search=amazon&type=EXPENSE")
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    update_response = client.patch(
        f"/api/v1/transactions/{transaction_id}",
        json={"description": "Updated order"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated order"

    delete_response = client.delete(f"/api/v1/transactions/{transaction_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/transactions/{transaction_id}").status_code == 404


def test_transaction_validation_and_ownership() -> None:
    authenticate()
    future_date = (date.today() + timedelta(days=1)).isoformat()
    invalid_response = client.post(
        "/api/v1/transactions",
        json={
            "type": "EXPENSE",
            "amount": "0",
            "category_id": "00000000-0000-0000-0000-000000000101",
            "transaction_date": future_date,
        },
    )
    assert invalid_response.status_code == 422
    assert invalid_response.json()["error"]["code"] == "VALIDATION_ERROR"

    mismatch_response = client.post(
        "/api/v1/transactions",
        json={
            "type": "EXPENSE",
            "amount": "10.00",
            "category_id": "00000000-0000-0000-0000-000000000001",
            "transaction_date": date.today().isoformat(),
        },
    )
    assert mismatch_response.status_code == 400
    assert mismatch_response.json()["error"]["code"] == "REQUEST_ERROR"


def test_page_size_is_bounded() -> None:
    authenticate()
    response = client.get("/api/v1/transactions?page_size=101")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
