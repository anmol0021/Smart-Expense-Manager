import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DatabaseSession

from app.core.config import Settings
from app.models import Session, User
from app.schemas.auth import LoginRequest, RegisterRequest

password_hasher = PasswordHasher()


def register_user(database_session: DatabaseSession, payload: RegisterRequest) -> User:
    email = str(payload.email).lower()
    if database_session.scalar(select(User).where(User.email == email)) is not None:
        raise ValueError("Email is already registered")

    user = User(
        name=payload.name,
        email=email,
        password_hash=password_hasher.hash(payload.password),
    )
    database_session.add(user)
    try:
        database_session.commit()
    except IntegrityError as error:
        database_session.rollback()
        raise ValueError("Email is already registered") from error
    database_session.refresh(user)
    return user


def authenticate_user(database_session: DatabaseSession, payload: LoginRequest) -> User | None:
    user = database_session.scalar(select(User).where(User.email == str(payload.email).lower()))
    if user is None:
        return None
    try:
        password_hasher.verify(user.password_hash, payload.password)
    except VerifyMismatchError:
        return None
    return user


def create_session(database_session: DatabaseSession, user: User, settings: Settings) -> str:
    raw_token = secrets.token_urlsafe(32)
    auth_session = Session(
        user_id=user.id,
        token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=settings.session_lifetime_hours),
    )
    database_session.add(auth_session)
    database_session.commit()
    return raw_token


def revoke_session(database_session: DatabaseSession, raw_token: str) -> None:
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    auth_session = database_session.scalar(select(Session).where(Session.token_hash == token_hash))
    if auth_session is not None and auth_session.revoked_at is None:
        auth_session.revoked_at = datetime.now(timezone.utc)
        database_session.commit()
