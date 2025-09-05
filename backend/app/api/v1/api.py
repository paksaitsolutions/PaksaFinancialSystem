from fastapi import APIRouter
from .endpoints import gl
from ..endpoints.budget import router as budget_router

api_router = APIRouter()

# Include GL router
api_router.include_router(gl.router, prefix="/gl", tags=["General Ledger"])

# Include Budget router
api_router.include_router(budget_router, prefix="/budget", tags=["Budget"])
