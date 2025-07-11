from fastapi import APIRouter
from . import accounts, journal_entries, trial_balance, recurring_journals

router = APIRouter(prefix="/gl", tags=["General Ledger"])

# Include all GL sub-routers
router.include_router(accounts.router, prefix="/accounts", tags=["GL Accounts"])
router.include_router(journal_entries.router, prefix="/journal-entries", tags=["Journal Entries"])
router.include_router(trial_balance.router, prefix="/reports", tags=["Reports"])
router.include_router(recurring_journals.router, prefix="/recurring-journals", tags=["Recurring Journals"])
