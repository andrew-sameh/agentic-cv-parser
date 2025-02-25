from fastapi import APIRouter
from api.v1.endpoints import health, candidate 


router = APIRouter()
# router.include_router(research.router, prefix="/research", tags=["Research"])
router.include_router(health.router, prefix="/health", tags=["Health"])
router.include_router(candidate.router, prefix="/candidates", tags=["Candidate"])
