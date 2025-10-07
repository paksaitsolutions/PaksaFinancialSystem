"""
Application exceptions.
"""

class ValidationError(Exception):
    """Validation error exception."""
    pass

class BusinessLogicError(Exception):
    """Business logic error exception."""
    pass

class DataIntegrityError(Exception):
    """Data integrity error exception."""
    pass

class NotFoundException(Exception):
    """Not found error exception."""
    pass

class ValidationException(Exception):
    """Validation exception."""
    pass

class BusinessRuleException(Exception):
    """Business rule exception."""
    pass