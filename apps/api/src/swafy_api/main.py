from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from swafy_api.api.routes import auth, health
from swafy_api.config import get_settings

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("swafy.api")

app = FastAPI(
    title="SWAFY API",
    version="1.0.0",
    description=(
        "SWAFY civic reporting backend. The frozen v1 contract is docs/contracts/openapi.yaml."
    ),
)

if settings.allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or f"req_{uuid4().hex}"
    request.state.request_id = request_id[:128]
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


def _error_code(status_code: int) -> str:
    return {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        413: "PAYLOAD_TOO_LARGE",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
    }.get(status_code, "INTERNAL_ERROR" if status_code >= 500 else "BAD_REQUEST")


def _error_payload(request: Request, code: str, message: str, details=None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "request_id": getattr(request.state, "request_id", f"req_{uuid4().hex}"),
        }
    }


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(request, _error_code(exc.status_code), message),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(part) for part in error.get("loc", ())),
            "issue": error.get("msg", "Invalid value"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=_error_payload(request, "VALIDATION_ERROR", "Request validation failed", details),
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled API error request_id=%s", getattr(request.state, "request_id", "unknown")
    )
    return JSONResponse(
        status_code=500,
        content=_error_payload(request, "INTERNAL_ERROR", "An unexpected error occurred"),
    )


api_v1_router = APIRouter()
api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", include_in_schema=False)
def root_health() -> dict[str, str]:
    """Compatibility probe used by the local stack; public contract is /api/v1/health."""
    return {"status": "ok"}
