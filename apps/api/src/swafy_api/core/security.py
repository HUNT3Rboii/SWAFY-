from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from pwdlib import PasswordHash

from swafy_api.config import Settings, get_settings

_password_hash = PasswordHash.recommended()


class InvalidTokenError(Exception):
    """Raised when a JWT is invalid or is used for the wrong purpose."""


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _password_hash.verify(password, password_hash)
    except Exception:
        # Malformed/legacy hashes must fail authentication, not crash the route.
        return False


def create_user_token(
    *,
    user_id: UUID,
    token_type: str,
    jti: UUID,
    expires_delta: timedelta,
    settings: Settings | None = None,
) -> tuple[str, datetime]:
    settings = settings or get_settings()
    now = datetime.now(UTC)
    expires_at = now + expires_delta
    payload = {
        "sub": str(user_id),
        "token_type": token_type,
        "jti": str(jti),
        "iat": now,
        "exp": expires_at,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    token = jwt.encode(
        payload, settings.jwt_secret.get_secret_value(), algorithm=settings.jwt_algorithm
    )
    return token, expires_at


def decode_user_token(token: str, *, expected_type: str, settings: Settings | None = None) -> dict:
    settings = settings or get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["sub", "token_type", "jti", "iat", "exp", "iss", "aud"]},
        )
        if payload.get("token_type") != expected_type:
            raise InvalidTokenError("Wrong token type")
        UUID(payload["sub"])
        UUID(payload["jti"])
        return payload
    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError) as exc:
        raise InvalidTokenError("Invalid or expired token") from exc


def new_refresh_jti() -> UUID:
    return uuid4()


def constant_time_secret_match(provided: str, expected: str) -> bool:
    return secrets.compare_digest(provided.encode("utf-8"), expected.encode("utf-8"))
