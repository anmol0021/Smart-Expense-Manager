import hashlib
from collections.abc import Generator
from datetime import datetime, timezone

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DatabaseSession

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models import Session, User


def get_db() -> Generator[DatabaseSession, None, None]:
    database_session = SessionLocal()
    try:
        yield database_session
    finally:
        database_session.close()


def get_current_user(
    session_token: str | None = Cookie(default=None, alias=get_settings().session_cookie_name),
    database_session: DatabaseSession = Depends(get_db),
) -> User:
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    token_hash = hashlib.sha256(session_token.encode("utf-8")).hexdigest()
    auth_session = database_session.scalar(
        select(Session).where(
            Session.token_hash == token_hash,
            Session.revoked_at.is_(None),
            Session.expires_at > datetime.now(timezone.utc),
        )
    )
    if auth_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    user = database_session.get(User, auth_session.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    return user
