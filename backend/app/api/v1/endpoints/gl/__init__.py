from fastapi import APIRouter

router = APIRouter(prefix="/gl", tags=["General Ledger"])

# Import and include routers individually to avoid circular imports
try:
    from .accounts import router as accounts_router
    router.include_router(accounts_router, prefix="/accounts", tags=["GL Accounts"])
except ImportError:
    pass

try:
    from .journal_entries import router as journal_entries_router
    router.include_router(journal_entries_router, prefix="/journal-entries", tags=["Journal Entries"])
except ImportError:
    pass

try:
    from .trial_balance import router as trial_balance_router
    router.include_router(trial_balance_router, prefix="/reports", tags=["Reports"])
except ImportError:
    pass

try:
    from .recurring_journals import router as recurring_journals_router
    router.include_router(recurring_journals_router, prefix="/recurring-journals", tags=["Recurring Journals"])
except ImportError:
    pass
