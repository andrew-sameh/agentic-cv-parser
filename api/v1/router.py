from fastapi import APIRouter
from api.v1.endpoints import health, candidate , agent


router = APIRouter()
router.include_router(agent.router, prefix="/agent", tags=["Agent"])
router.include_router(candidate.router, prefix="/candidates", tags=["Candidate"])
router.include_router(health.router, prefix="/health", tags=["Health"])
