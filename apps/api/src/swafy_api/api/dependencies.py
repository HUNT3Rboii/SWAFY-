from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from swafy_api.config import get_settings
from swafy_api.core.security import InvalidTokenError, constant_time_secret_match, decode_user_token
from swafy_api.db import get_db
from swafy_api.models import User, UserRole

_user_bearer = HTTPBearer(
    auto_error=False,
    scheme_name="BearerAuth",
    bearerFormat="JWT",
    description="Citizen or municipal_admin access token.",
)
_worker_bearer = HTTPBearer(
    auto_error=False,
    scheme_name="WorkerServiceAuth",
    description="Dedicated internal vision-worker service token; not a user JWT.",
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_user_bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required"
        )
    try:
        claims = decode_user_token(credentials.credentials, expected_type="access")
        user_id = UUID(claims["sub"])
    except (InvalidTokenError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        ) from None
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive or unavailable"
        )
    return user


def require_roles(*allowed_roles: UserRole) -> Callable:
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return role_dependency


def verify_worker_token(provided_token: str, expected_token: str) -> bool:
    return bool(expected_token) and constant_time_secret_match(provided_token, expected_token)


def require_worker_service(
    credentials: HTTPAuthorizationCredentials | None = Depends(_worker_bearer),
) -> None:
    expected = get_settings().worker_service_token.get_secret_value()
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Worker service token is required"
        )
    if not verify_worker_token(credentials.credentials, expected):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid worker service token"
        )
