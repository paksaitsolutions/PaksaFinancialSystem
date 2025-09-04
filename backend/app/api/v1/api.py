from fastapi import APIRouter
from .endpoints import gl

api_router = APIRouter()

# Include GL router
api_router.include_router(gl.router, prefix="/gl", tags=["General Ledger"])

# You can include other routers here as needed
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
