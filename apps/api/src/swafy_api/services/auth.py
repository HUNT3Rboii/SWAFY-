from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from swafy_api.config import Settings, get_settings
from swafy_api.core.security import (
    create_user_token,
    hash_password,
    new_refresh_jti,
    verify_password,
)
from swafy_api.models import RefreshToken, User, UserRole
from swafy_api.schemas.auth import AuthResponse, AuthTokensResponse, UserResponse


def build_auth_response(db: Session, user: User, settings: Settings | None = None) -> AuthResponse:
    settings = settings or get_settings()
    access_jti = new_refresh_jti()
    refresh_jti = new_refresh_jti()
    access_token, _ = create_user_token(
        user_id=user.id,
        token_type="access",
        jti=access_jti,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        settings=settings,
    )
    refresh_token, refresh_expires_at = create_user_token(
        user_id=user.id,
        token_type="refresh",
        jti=refresh_jti,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        settings=settings,
    )
    db.add(RefreshToken(jti=refresh_jti, user_id=user.id, expires_at=refresh_expires_at))
    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=AuthTokensResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=settings.access_token_expire_minutes * 60,
        ),
    )


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not user.is_active or not verify_password(password, user.password_hash):
        return None
    return user


def register_citizen(db: Session, *, display_name: str, email: str, password: str) -> User:
    user = User(
        display_name=display_name,
        email=email,
        password_hash=hash_password(password),
        role=UserRole.CITIZEN,
    )
    db.add(user)
    db.flush()
    return user
