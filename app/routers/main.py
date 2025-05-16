from fastapi import APIRouter
from app.authorization_service.main import router as auth_router
from app.surveillance_service.surveillance import router as surveillance_router
from app.security_dashboard_service.main import router as security_router
from app.vehicle_detector.main import router as vehicle_router
from app.logger_service.main import router as logger_router

# Create main router
router = APIRouter()

# Include all service routers
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(surveillance_router, prefix="/surveillance", tags=["Surveillance"])
router.include_router(security_router, prefix="/security", tags=["Security"])
router.include_router(vehicle_router, prefix="/vehicle", tags=["Vehicle Detection"])
router.include_router(logger_router, prefix="/logger", tags=["Logging"])