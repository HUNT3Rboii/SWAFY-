from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", operation_id="healthCheck", summary="Check API health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
