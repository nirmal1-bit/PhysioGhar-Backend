from fastapi import APIRouter

from app.features.auth.router import router as auth_router
from app.features.booking.router import router as booking_router
from app.features.dashboard.router import router as dashboard_router
from app.features.patient.router import router as patient_router
from app.features.profile.router import router as profile_router
from app.features.schedule.router import router as schedule_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(booking_router)
api_router.include_router(dashboard_router)
api_router.include_router(profile_router)
api_router.include_router(patient_router)
api_router.include_router(schedule_router)


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
