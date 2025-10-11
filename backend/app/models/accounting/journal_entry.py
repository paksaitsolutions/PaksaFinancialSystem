# Import unified JournalEntry models to avoid duplicates
from app.models import JournalEntry, JournalEntryLine

# Re-export for backward compatibility
__all__ = ['JournalEntry', 'JournalEntryLine']