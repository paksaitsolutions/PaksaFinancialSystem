class AccountsPayableException(Exception):
    """Base exception for the Accounts Payable module."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class VendorNotFoundException(AccountsPayableException):
    """Raised when a vendor is not found."""
    def __init__(self, vendor_id: str):
        super().__init__(f"Vendor with ID '{vendor_id}' not found.")

class BillNotFoundException(AccountsPayableException):
    """Raised when a bill is not found."""
    def __init__(self, bill_id: str):
        super().__init__(f"Bill with ID '{bill_id}' not found.")

class PaymentNotFoundException(AccountsPayableException):
    """Raised when a payment is not found."""
    def __init__(self, payment_id: str):
        super().__init__(f"Payment with ID '{payment_id}' not found.")

class InvalidBillOperationException(AccountsPayableException):
    """Raised for invalid operations on a bill (e.g., editing a paid bill)."""
    pass

class InvalidPaymentOperationException(AccountsPayableException):
    """Raised for invalid payment operations (e.g., allocating more than the payment amount)."""
    pass
