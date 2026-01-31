"""
Cross-module workflow integration service
"""
from sqlalchemy.orm import Session
from uuid import UUID

from app.models import APInvoice, ARInvoice, PayrollRun, Employee, JournalEntry
from app.services.base import BaseService
from app.services.payroll_gl_service import PayrollGLService
from app.services.tax_service import TaxService


class WorkflowService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db, JournalEntry)
        self.tax_service = TaxService(db)
        self.payroll_gl_service = PayrollGLService(db)
    
    def process_ap_invoice_workflow(self, invoice: APInvoice) -> dict:
        
        # Step 1: Calculate taxes
        tax_amount = self.tax_service.calculate_tax_for_ap_invoice(invoice)
        
        # Step 2: Update invoice status
        invoice.status = 'sent'
        
        # Step 3: Create GL entry (handled by existing AP service)
        
        return {
            "invoice_id": str(invoice.id),
            "tax_calculated": float(tax_amount),
            "total_amount": float(invoice.total_amount),
            "status": invoice.status,
            "workflow_completed": True
        }
    
    def process_payroll_workflow(self, payroll_run: PayrollRun) -> dict:
        
        # Step 1: Process payroll run
        payroll_run.status = 'approved'
        
        # Step 2: Post to GL
        journal_entry = self.payroll_gl_service.post_payroll_to_gl(payroll_run)
        
        # Step 3: Update employee records
        for entry in payroll_run.entries:
            employee = self.db.query(Employee).filter(Employee.id == entry.employee_id).first()
            if employee:
                # Update any employee-specific data if needed
                pass
        
        return {
            "payroll_run_id": str(payroll_run.id),
            "journal_entry_id": str(journal_entry.id),
            "total_processed": float(payroll_run.total_gross),
            "status": payroll_run.status,
            "workflow_completed": True
        }
    
    def get_workflow_status(self, entity_type: str, entity_id: UUID) -> dict:
        
        if entity_type == "ap_invoice":
            invoice = self.db.query(APInvoice).filter(APInvoice.id == entity_id).first()
            if not invoice:
                return {"error": "Invoice not found"}
            
            # Check if GL entry exists
            gl_entry = self.db.query(JournalEntry).filter(
                JournalEntry.source_module == "AP",
                JournalEntry.reference == invoice.invoice_number
            ).first()
            
            return {
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "status": invoice.status,
                "tax_calculated": invoice.tax_amount > 0,
                "gl_posted": gl_entry is not None,
                "workflow_complete": invoice.status == 'paid' and gl_entry is not None
            }
        
        elif entity_type == "payroll_run":
            payroll = self.db.query(PayrollRun).filter(PayrollRun.id == entity_id).first()
            if not payroll:
                return {"error": "Payroll run not found"}
            
            gl_entry = self.db.query(JournalEntry).filter(
                JournalEntry.source_module == "PAYROLL",
                JournalEntry.reference == payroll.run_number
            ).first()
            
            return {
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "status": payroll.status,
                "gl_posted": gl_entry is not None,
                "workflow_complete": payroll.status == 'paid' and gl_entry is not None
            }
        
        return {"error": "Unsupported entity type"}