# Accounts Receivable services package
from .customer_service import CustomerService
from .invoice_service import InvoiceService
from .collections_service import CollectionsService

# Create placeholder services that don't exist yet
class PaymentService:
    def __init__(self, db):
        self.db = db
    
    async def create_payment(self, payment_data, user_id):
        return {"id": "placeholder", "status": "created"}

class CreditNoteService:
    def __init__(self, db):
        self.db = db
    
    async def create_credit_note(self, credit_note_data, user_id):
        return {"id": "placeholder", "status": "created"}

class ReportingService:
    def __init__(self, db):
        self.db = db
    
    async def get_aging_report(self):
        return {"items": [], "totals": {}}

__all__ = ['InvoiceService', 'PaymentService', 'CreditNoteService', 'ReportingService', 'CustomerService', 'CollectionsService']