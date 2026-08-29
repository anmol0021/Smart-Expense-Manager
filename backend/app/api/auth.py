from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session as DatabaseSession

from app.api.dependencies import get_current_user, get_db
from app.core.config import get_settings
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from app.services.auth import authenticate_user, create_session, register_user, revoke_session

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest, database_session: DatabaseSession = Depends(get_db)
) -> UserResponse:
    try:
        user = register_user(database_session, payload)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return UserResponse.model_validate(user)


@router.post("/login", response_model=UserResponse)
def login(
    payload: LoginRequest,
    response: Response,
    database_session: DatabaseSession = Depends(get_db),
) -> UserResponse:
    user = authenticate_user(database_session, payload)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    raw_token = create_session(database_session, user, settings)
    response.set_cookie(
        key=settings.session_cookie_name,
        value=raw_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.session_lifetime_hours * 60 * 60,
    )
    return UserResponse.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    session_token: str | None = Cookie(default=None, alias=settings.session_cookie_name),
    database_session: DatabaseSession = Depends(get_db),
) -> None:
    if session_token:
        revoke_session(database_session, session_token)
    response.delete_cookie(key=settings.session_cookie_name)


@router.get("/me", response_model=UserResponse)
def current_user(user=Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(user)
