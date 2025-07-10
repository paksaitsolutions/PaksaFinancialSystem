from fastapi import APIRouter
from .endpoints import purchase_requisitions

# Create the main API router for the Procurement module
api_router = APIRouter()

# Include the purchase requisitions endpoints under the /requisitions path
api_router.include_router(
    purchase_requisitions.router,
    prefix="/requisitions",
    tags=["purchase-requisitions"]
)

# Add more endpoints here as they are implemented
# Example:
# api_router.include_router(
#     purchase_orders.router,
#     prefix="/purchase-orders",
#     tags=["purchase-orders"]
# )
