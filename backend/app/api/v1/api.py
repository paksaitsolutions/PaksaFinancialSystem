from fastapi import APIRouter
from .endpoints import gl
from ..endpoints.budget import router as budget_router
from .endpoints.hrm_policies import router as hrm_policies_router
from .endpoints.auth_mock import router as auth_router

api_router = APIRouter()

# Include Auth router
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include GL router
api_router.include_router(gl.router, prefix="/gl", tags=["General Ledger"])

# Include Budget router
api_router.include_router(budget_router, prefix="/budget", tags=["Budget"])

# Include HRM Policies router
api_router.include_router(hrm_policies_router, prefix="/hrm/policies", tags=["HRM Policies"])

# Include Collections router
from .endpoints.collections import router as collections_router
api_router.include_router(collections_router, prefix="/ar/collections", tags=["Collections"])
