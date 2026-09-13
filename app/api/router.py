from fastapi import APIRouter

from app.features.dashboard.router import router as dashboard_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(dashboard_router)


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
