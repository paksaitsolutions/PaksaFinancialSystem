"""
Payroll service exceptions.
"""

class PayrollBaseException(Exception):
    """Base exception for payroll operations."""
    pass

class PayrollRunNotFoundError(PayrollBaseException):
    """Raised when a payroll run is not found."""
    pass

class PayrollProcessingError(PayrollBaseException):
    """Raised when there's an error processing payroll."""
    pass

class EmployeeNotFoundError(PayrollBaseException):
    """Raised when an employee is not found."""
    pass

class PayPeriodError(PayrollBaseException):
    """Raised when there's an error with pay period operations."""
    pass

class PayslipNotFoundError(PayrollBaseException):
    """Raised when a payslip is not found."""
    pass

class EmailError(PayrollBaseException):
    """Raised when there's an error sending email."""
    pass