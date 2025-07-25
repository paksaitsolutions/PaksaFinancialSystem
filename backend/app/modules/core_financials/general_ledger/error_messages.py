"""User-friendly error messages for GL module"""

GL_ERROR_MESSAGES = {
    # Account errors
    "ACCOUNT_CODE_EXISTS": "An account with this code already exists. Please choose a different code.",
    "ACCOUNT_NOT_FOUND": "The requested account could not be found.",
    "ACCOUNT_IN_USE": "This account cannot be deleted because it has transactions.",
    "INVALID_ACCOUNT_TYPE": "Please select a valid account type (Asset, Liability, Equity, Revenue, or Expense).",
    
    # Journal entry errors
    "ENTRY_NOT_FOUND": "The journal entry could not be found.",
    "ENTRY_NOT_BALANCED": "The journal entry is not balanced. Total debits must equal total credits.",
    "ENTRY_ALREADY_POSTED": "This journal entry has already been posted and cannot be modified.",
    "ENTRY_NOT_POSTED": "This journal entry must be posted before it can be reversed.",
    "ENTRY_ALREADY_REVERSED": "This journal entry has already been reversed.",
    
    # Posting errors
    "POSTING_FAILED": "Failed to post the journal entry. Please check the entry details and try again.",
    "UNPOSTING_FAILED": "Failed to unpost the journal entry. Please contact your administrator.",
    "REVERSAL_FAILED": "Failed to reverse the journal entry. Please check the entry status and try again.",
    
    # Period errors
    "PERIOD_CLOSED": "Cannot post entries to a closed period. Please select an open period.",
    "PERIOD_NOT_FOUND": "The specified accounting period could not be found.",
    "PERIOD_ALREADY_CLOSED": "This period has already been closed.",
    
    # Approval errors
    "APPROVAL_REQUIRED": "This operation requires approval before it can be completed.",
    "INSUFFICIENT_PERMISSIONS": "You do not have permission to perform this action.",
    "APPROVAL_FAILED": "The approval process failed. Please contact your administrator.",
    
    # Validation errors
    "REQUIRED_FIELD": "This field is required.",
    "INVALID_DATE": "Please enter a valid date.",
    "INVALID_AMOUNT": "Please enter a valid amount.",
    "NEGATIVE_AMOUNT": "Amount cannot be negative.",
    "ZERO_AMOUNT": "Amount cannot be zero.",
    
    # General errors
    "OPERATION_FAILED": "The operation could not be completed. Please try again.",
    "DATABASE_ERROR": "A database error occurred. Please contact support if the problem persists.",
    "PERMISSION_DENIED": "You do not have permission to access this resource.",
    "VALIDATION_ERROR": "Please correct the highlighted errors and try again."
}

def get_user_friendly_message(error_code: str, default_message: str = None) -> str:
    """Get user-friendly error message by code"""
    return GL_ERROR_MESSAGES.get(error_code, default_message or "An unexpected error occurred.")

def format_validation_errors(errors: list) -> str:
    """Format multiple validation errors into user-friendly message"""
    if not errors:
        return ""
    
    if len(errors) == 1:
        return errors[0]
    
    return f"Please correct the following errors:\n• " + "\n• ".join(errors)