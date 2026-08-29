from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_db
from app.db.base import Base
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, _connection_record):
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


Base.metadata.create_all(engine)


def override_get_db() -> Generator[DatabaseSession, None, None]:
    with DatabaseSession(engine) as database_session:
        yield database_session


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def registration_payload() -> dict[str, str]:
    return {
        "name": "Auth Test User",
        "email": "auth-test@example.com",
        "password": "StrongPassword123!",
    }


def test_register_login_me_and_logout() -> None:
    payload = registration_payload()
    register_response = client.post("/api/v1/auth/register", json=payload)

    assert register_response.status_code == 201
    assert register_response.json()["email"] == payload["email"]
    assert "password" not in register_response.json()
    assert "password_hash" not in register_response.json()

    login_response = client.post("/api/v1/auth/login", json=payload)
    assert login_response.status_code == 200
    assert "password_hash" not in login_response.json()
    assert client.cookies.get("smart_expense_session")

    me_response = client.get("/api/v1/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["email"] == payload["email"]

    logout_response = client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401


def test_duplicate_email_is_rejected() -> None:
    response = client.post("/api/v1/auth/register", json=registration_payload())

    assert response.status_code == 409
    assert response.json()["error"] == {
        "code": "CONFLICT",
        "message": "Email is already registered",
    }


def test_invalid_credentials_are_rejected() -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={**registration_payload(), "password": "WrongPassword123!"},
    )

    assert response.status_code == 401
    assert response.json()["error"] == {
        "code": "UNAUTHORIZED",
        "message": "Invalid email or password",
    }


def test_password_policy_is_validated() -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={**registration_payload(), "email": "weak@example.com", "password": "password"},
    )

    assert response.status_code == 422
