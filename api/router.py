from fastapi import APIRouter
from api.v1 import router as routerV1


router = APIRouter()
router.include_router(routerV1.router, prefix="/v1")
