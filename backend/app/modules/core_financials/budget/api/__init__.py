from fastapi import APIRouter
from .endpoints import router

budget_router = APIRouter()
budget_router.include_router(router, prefix="/budget", tags=["budget"])

__all__ = ["budget_router"]