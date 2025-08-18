"""
Main API router that includes all endpoint routers.
"""
from fastapi import APIRouter

from app.api.endpoints import (
    login, users, utils, gl_accounts, gl_journals, gl_reports, gl_recurring
)
from app.api.v1.endpoints import financial_statements

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(gl_accounts.router, prefix="/gl/accounts", tags=["gl-accounts"])
api_router.include_router(gl_journals.router, prefix="/gl/journals", tags=["gl-journals"])
api_router.include_router(gl_reports.router, prefix="/gl/reports", tags=["gl-reports"])
api_router.include_router(gl_recurring.router, prefix="/gl/recurring", tags=["gl-recurring"])
api_router.include_router(financial_statements.router, prefix="/financial-statements", tags=["financial-statements"])
