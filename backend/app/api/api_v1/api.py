"""
Main API router that includes all endpoint routers.
"""

def setup_routers(router):
    """
    Set up all API routers.
    This function is called from api_v1/__init__.py after the router is initialized.
    """
    # Import only the modules that are currently available
    try:
        # Core financial modules
        from app.modules.core_financials.accounts_payable.api import router as ap_router
        router.include_router(ap_router, prefix="/ap", tags=["Accounts Payable"])
    except ImportError as e:
        print(f"Warning: Could not import accounts_payable module: {e}")

    try:
        # Authentication module
        from app.modules.cross_cutting.auth.router import router as auth_router
        router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    except ImportError as e:
        print(f"Warning: Could not import auth module: {e}")

    # Health check endpoint
    @router.get("/health")
    async def health_check():
        return {"status": "healthy", "message": "Paksa Financial System API is running"}
    
    return router