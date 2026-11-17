from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from swafy_api.api.dependencies import get_current_user
from swafy_api.core.security import InvalidTokenError, decode_user_token
from swafy_api.db import get_db
from swafy_api.models import RefreshToken, User
from swafy_api.schemas.auth import AuthResponse, LoginRequest, RefreshRequest, RegisterRequest
from swafy_api.services.auth import authenticate_user, build_auth_response, register_citizen

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    if db.scalar(select(User.id).where(User.email == payload.email)) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )
    try:
        user = register_citizen(
            db,
            display_name=payload.display_name,
            email=payload.email,
            password=payload.password,
        )
        response = build_auth_response(db, user)
        db.commit()
        db.refresh(user)
        return response
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from exc
    except Exception:
        db.rollback()
        raise


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = authenticate_user(db, str(payload.email), payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    response = build_auth_response(db, user)
    db.commit()
    return response


@router.post("/refresh", response_model=AuthResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        claims = decode_user_token(payload.refresh_token, expected_type="refresh")
        token_id = UUID(claims["jti"])
        user_id = UUID(claims["sub"])
    except (InvalidTokenError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from None

    now = datetime.now(UTC)
    stored_token = db.scalar(
        select(RefreshToken).where(RefreshToken.jti == token_id).with_for_update()
    )
    if (
        stored_token is None
        or stored_token.user_id != user_id
        or stored_token.revoked_at is not None
        or stored_token.expires_at <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from None

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive or unavailable"
        )

    stored_token.revoked_at = now
    response = build_auth_response(db, user)
    db.commit()
    return response


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def logout(
    payload: RefreshRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    # Logout is intentionally idempotent: an unknown/already-revoked token still returns 204.
    try:
        claims = decode_user_token(payload.refresh_token, expected_type="refresh")
        token_id = UUID(claims["jti"])
        token_user_id = UUID(claims["sub"])
        if token_user_id == current_user.id:
            stored_token = db.scalar(
                select(RefreshToken).where(RefreshToken.jti == token_id).with_for_update()
            )
            if (
                stored_token is not None
                and stored_token.user_id == current_user.id
                and stored_token.revoked_at is None
            ):
                stored_token.revoked_at = datetime.now(UTC)
                db.commit()
    except (InvalidTokenError, ValueError, KeyError):
        db.rollback()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
