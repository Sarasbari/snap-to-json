from fastapi import APIRouter
from app.api.v1.extract import router as extract_router
from app.api.v1.history import router as history_router

router = APIRouter()
router.include_router(extract_router)
router.include_router(history_router)
