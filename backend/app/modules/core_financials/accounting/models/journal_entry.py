# Import unified JournalEntry models to avoid duplicates
from app.models import JournalEntry, JournalEntryLine
from enum import Enum

# Keep enums for backward compatibility
class JournalEntryStatus(str, Enum):
    """Status of a journal entry."""
    DRAFT = 'draft'
    POSTED = 'posted'
    VOIDED = 'voided'
    REVERSED = 'reversed'

class JournalEntryType(str, Enum):
    """Types of journal entries."""
    STANDARD = 'standard'
    ADJUSTING = 'adjusting'
    CLOSING = 'closing'
    REVERSING = 'reversing'
    RECURRING = 'recurring'
    OPENING = 'opening'

# Re-export for backward compatibility
__all__ = ['JournalEntry', 'JournalEntryLine', 'JournalEntryStatus', 'JournalEntryType']
