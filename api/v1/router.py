from fastapi import APIRouter
from api.v1.endpoints import health, research


router = APIRouter()
router.include_router(research.router, prefix="/research", tags=["Research"])
router.include_router(health.router, prefix="/health", tags=["Health"])
