"""
Production database constraints and integrity checks.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseConstraints:
    """Production database constraints manager."""
    
    @staticmethod
    async def create_foreign_key_constraints(db: AsyncSession):
        """Create all missing foreign key constraints."""
        constraints = [
            # GL Module Constraints
            "ALTER TABLE gl_journal_entry ADD CONSTRAINT fk_journal_entry_tenant FOREIGN KEY (tenant_id) REFERENCES tenant(id)",
            "ALTER TABLE gl_journal_entry_line ADD CONSTRAINT fk_journal_line_entry FOREIGN KEY (journal_entry_id) REFERENCES gl_journal_entry(id)",
            "ALTER TABLE gl_journal_entry_line ADD CONSTRAINT fk_journal_line_account FOREIGN KEY (account_id) REFERENCES gl_account(id)",
            
            # AP Module Constraints
            "ALTER TABLE ap_vendor ADD CONSTRAINT fk_vendor_tenant FOREIGN KEY (tenant_id) REFERENCES tenant(id)",
            "ALTER TABLE ap_bill ADD CONSTRAINT fk_bill_vendor FOREIGN KEY (vendor_id) REFERENCES ap_vendor(id)",
            "ALTER TABLE ap_bill_line_item ADD CONSTRAINT fk_bill_line_bill FOREIGN KEY (bill_id) REFERENCES ap_bill(id)",
            "ALTER TABLE ap_payment ADD CONSTRAINT fk_payment_vendor FOREIGN KEY (vendor_id) REFERENCES ap_vendor(id)",
            
            # AR Module Constraints
            "ALTER TABLE ar_customer ADD CONSTRAINT fk_customer_tenant FOREIGN KEY (tenant_id) REFERENCES tenant(id)",
            "ALTER TABLE ar_invoice ADD CONSTRAINT fk_invoice_customer FOREIGN KEY (customer_id) REFERENCES ar_customer(id)",
            "ALTER TABLE ar_invoice_line_item ADD CONSTRAINT fk_invoice_line_invoice FOREIGN KEY (invoice_id) REFERENCES ar_invoice(id)",
            "ALTER TABLE ar_payment ADD CONSTRAINT fk_ar_payment_customer FOREIGN KEY (customer_id) REFERENCES ar_customer(id)",
            
            # Budget Module Constraints
            "ALTER TABLE budget ADD CONSTRAINT fk_budget_tenant FOREIGN KEY (tenant_id) REFERENCES tenant(id)",
            "ALTER TABLE budget_line_item ADD CONSTRAINT fk_budget_line_budget FOREIGN KEY (budget_id) REFERENCES budget(id)",
            "ALTER TABLE budget_line_item ADD CONSTRAINT fk_budget_line_account FOREIGN KEY (account_id) REFERENCES gl_account(id)",
            
            # Cash Management Constraints
            "ALTER TABLE bank_account ADD CONSTRAINT fk_bank_account_tenant FOREIGN KEY (tenant_id) REFERENCES tenant(id)",
            "ALTER TABLE bank_transaction ADD CONSTRAINT fk_bank_transaction_account FOREIGN KEY (bank_account_id) REFERENCES bank_account(id)",
            "ALTER TABLE bank_reconciliation ADD CONSTRAINT fk_reconciliation_account FOREIGN KEY (bank_account_id) REFERENCES bank_account(id)",
            
            # HRM Module Constraints
            "ALTER TABLE employee ADD CONSTRAINT fk_employee_tenant FOREIGN KEY (tenant_id) REFERENCES tenant(id)",
            "ALTER TABLE leave_request ADD CONSTRAINT fk_leave_employee FOREIGN KEY (employee_id) REFERENCES employee(id)",
            "ALTER TABLE attendance_record ADD CONSTRAINT fk_attendance_employee FOREIGN KEY (employee_id) REFERENCES employee(id)",
            "ALTER TABLE performance_review ADD CONSTRAINT fk_performance_employee FOREIGN KEY (employee_id) REFERENCES employee(id)",
            
            # Inventory Module Constraints
            "ALTER TABLE inventory_item ADD CONSTRAINT fk_item_category FOREIGN KEY (category_id) REFERENCES inventory_category(id)",
            "ALTER TABLE inventory_item ADD CONSTRAINT fk_item_location FOREIGN KEY (default_location_id) REFERENCES inventory_location(id)",
            "ALTER TABLE inventory_transaction ADD CONSTRAINT fk_transaction_item FOREIGN KEY (item_id) REFERENCES inventory_item(id)",
            "ALTER TABLE inventory_transaction ADD CONSTRAINT fk_transaction_location FOREIGN KEY (location_id) REFERENCES inventory_location(id)"
        ]
        
        for constraint in constraints:
            try:
                await db.execute(text(constraint))
                logger.info(f"Created constraint: {constraint[:50]}...")
            except Exception as e:
                logger.warning(f"Constraint creation failed (may already exist): {e}")
        
        await db.commit()
    
    @staticmethod
    async def create_check_constraints(db: AsyncSession):
        """Create business rule check constraints."""
        check_constraints = [
            # Financial amount constraints
            "ALTER TABLE gl_journal_entry_line ADD CONSTRAINT chk_amount_not_zero CHECK (amount != 0)",
            "ALTER TABLE ap_bill ADD CONSTRAINT chk_bill_amount_positive CHECK (total_amount > 0)",
            "ALTER TABLE ar_invoice ADD CONSTRAINT chk_invoice_amount_positive CHECK (total_amount > 0)",
            "ALTER TABLE budget_line_item ADD CONSTRAINT chk_budget_amount_positive CHECK (budgeted_amount >= 0)",
            
            # Date constraints
            "ALTER TABLE ap_bill ADD CONSTRAINT chk_bill_dates CHECK (due_date >= bill_date)",
            "ALTER TABLE ar_invoice ADD CONSTRAINT chk_invoice_dates CHECK (due_date >= invoice_date)",
            "ALTER TABLE employee ADD CONSTRAINT chk_hire_date CHECK (hire_date <= CURRENT_DATE)",
            "ALTER TABLE leave_request ADD CONSTRAINT chk_leave_dates CHECK (end_date >= start_date)",
            
            # Status constraints
            "ALTER TABLE ap_bill ADD CONSTRAINT chk_bill_status CHECK (status IN ('draft', 'pending', 'approved', 'paid', 'cancelled'))",
            "ALTER TABLE ar_invoice ADD CONSTRAINT chk_invoice_status CHECK (status IN ('draft', 'sent', 'paid', 'overdue', 'cancelled'))",
            "ALTER TABLE budget ADD CONSTRAINT chk_budget_status CHECK (status IN ('draft', 'active', 'closed'))",
            
            # Inventory constraints
            "ALTER TABLE inventory_item ADD CONSTRAINT chk_quantity_non_negative CHECK (quantity_on_hand >= 0)",
            "ALTER TABLE inventory_item ADD CONSTRAINT chk_reorder_point_non_negative CHECK (reorder_point >= 0)",
            
            # Employee constraints
            "ALTER TABLE employee ADD CONSTRAINT chk_salary_positive CHECK (salary > 0)",
            "ALTER TABLE performance_review ADD CONSTRAINT chk_rating_range CHECK (overall_rating >= 1 AND overall_rating <= 5)"
        ]
        
        for constraint in check_constraints:
            try:
                await db.execute(text(constraint))
                logger.info(f"Created check constraint: {constraint[:50]}...")
            except Exception as e:
                logger.warning(f"Check constraint creation failed: {e}")
        
        await db.commit()
    
    @staticmethod
    async def create_indexes(db: AsyncSession):
        """Create performance-critical indexes."""
        indexes = [
            # Tenant isolation indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gl_journal_entry_tenant ON gl_journal_entry(tenant_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ap_vendor_tenant ON ap_vendor(tenant_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ar_customer_tenant ON ar_customer(tenant_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_employee_tenant ON employee(tenant_id)",
            
            # Date-based queries
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_journal_entry_date ON gl_journal_entry(entry_date)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ap_bill_date ON ap_bill(bill_date)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ar_invoice_date ON ar_invoice(invoice_date)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bank_transaction_date ON bank_transaction(transaction_date)",
            
            # Status-based queries
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ap_bill_status ON ap_bill(status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ar_invoice_status ON ar_invoice(status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_budget_status ON budget(status)",
            
            # Amount-based queries
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_journal_line_amount ON gl_journal_entry_line(amount)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ap_bill_amount ON ap_bill(total_amount)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ar_invoice_amount ON ar_invoice(total_amount)",
            
            # Search indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vendor_name ON ap_vendor USING gin(to_tsvector('english', vendor_name))",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customer_name ON ar_customer USING gin(to_tsvector('english', customer_name))",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_employee_name ON employee USING gin(to_tsvector('english', first_name || ' ' || last_name))",
            
            # Composite indexes for common queries
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_journal_tenant_date ON gl_journal_entry(tenant_id, entry_date)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bill_vendor_status ON ap_bill(vendor_id, status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_invoice_customer_status ON ar_invoice(customer_id, status)"
        ]
        
        for index in indexes:
            try:
                await db.execute(text(index))
                logger.info(f"Created index: {index[:50]}...")
            except Exception as e:
                logger.warning(f"Index creation failed: {e}")
        
        await db.commit()
    
    @staticmethod
    async def create_unique_constraints(db: AsyncSession):
        """Create unique constraints for data integrity."""
        unique_constraints = [
            # Business unique constraints
            "ALTER TABLE gl_account ADD CONSTRAINT uk_account_code_tenant UNIQUE (account_code, tenant_id)",
            "ALTER TABLE ap_vendor ADD CONSTRAINT uk_vendor_code_tenant UNIQUE (vendor_code, tenant_id)",
            "ALTER TABLE ar_customer ADD CONSTRAINT uk_customer_code_tenant UNIQUE (customer_code, tenant_id)",
            "ALTER TABLE employee ADD CONSTRAINT uk_employee_id_tenant UNIQUE (employee_id, tenant_id)",
            "ALTER TABLE inventory_item ADD CONSTRAINT uk_item_sku UNIQUE (sku)",
            "ALTER TABLE bank_account ADD CONSTRAINT uk_account_number UNIQUE (account_number)",
            
            # Email uniqueness
            "ALTER TABLE ap_vendor ADD CONSTRAINT uk_vendor_email UNIQUE (email)",
            "ALTER TABLE ar_customer ADD CONSTRAINT uk_customer_email UNIQUE (email)",
            "ALTER TABLE employee ADD CONSTRAINT uk_employee_email UNIQUE (email)"
        ]
        
        for constraint in unique_constraints:
            try:
                await db.execute(text(constraint))
                logger.info(f"Created unique constraint: {constraint[:50]}...")
            except Exception as e:
                logger.warning(f"Unique constraint creation failed: {e}")
        
        await db.commit()
    
    @staticmethod
    async def validate_data_integrity(db: AsyncSession) -> List[Dict[str, Any]]:
        """Validate data integrity across the system."""
        integrity_checks = []
        
        # Check for orphaned records
        orphan_checks = [
            {
                'name': 'Orphaned Journal Lines',
                'query': """
                    SELECT COUNT(*) FROM gl_journal_entry_line jel 
                    LEFT JOIN gl_journal_entry je ON jel.journal_entry_id = je.id 
                    WHERE je.id IS NULL
                """
            },
            {
                'name': 'Orphaned Bill Line Items',
                'query': """
                    SELECT COUNT(*) FROM ap_bill_line_item bli 
                    LEFT JOIN ap_bill b ON bli.bill_id = b.id 
                    WHERE b.id IS NULL
                """
            },
            {
                'name': 'Invalid Account References',
                'query': """
                    SELECT COUNT(*) FROM gl_journal_entry_line jel 
                    LEFT JOIN gl_account acc ON jel.account_id = acc.id 
                    WHERE acc.id IS NULL
                """
            }
        ]
        
        for check in orphan_checks:
            try:
                result = await db.execute(text(check['query']))
                count = result.scalar()
                integrity_checks.append({
                    'check': check['name'],
                    'status': 'PASS' if count == 0 else 'FAIL',
                    'issues_found': count
                })
            except Exception as e:
                integrity_checks.append({
                    'check': check['name'],
                    'status': 'ERROR',
                    'error': str(e)
                })
        
        return integrity_checks