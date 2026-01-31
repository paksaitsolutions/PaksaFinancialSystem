"""Add database indexes for performance optimization

Revision ID: optimize_indexes_001
Revises: 
Create Date: 2025-01-30

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'optimize_indexes_001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Add indexes for frequently queried columns"""
    
    # Foreign key indexes
    op.create_index('idx_journal_entry_debit_account', 'journal_entries', ['debit_account_id'])
    op.create_index('idx_journal_entry_credit_account', 'journal_entries', ['credit_account_id'])
    op.create_index('idx_audit_log_company', 'audit_logs', ['company_id'])
    op.create_index('idx_audit_log_user', 'audit_logs', ['created_by'])
    op.create_index('idx_bill_vendor', 'bills', ['vendor_id'])
    op.create_index('idx_payment_bill', 'payments', ['bill_id'])
    op.create_index('idx_invoice_customer', 'invoices', ['customer_id'])
    op.create_index('idx_transaction_bank_account', 'transactions', ['bank_account_id'])
    
    # Date field indexes for common queries
    op.create_index('idx_journal_entry_date', 'journal_entries', ['entry_date'])
    op.create_index('idx_bill_date', 'bills', ['bill_date'])
    op.create_index('idx_bill_due_date', 'bills', ['due_date'])
    op.create_index('idx_invoice_date', 'invoices', ['invoice_date'])
    op.create_index('idx_invoice_due_date', 'invoices', ['due_date'])
    op.create_index('idx_payment_date', 'payments', ['payment_date'])
    op.create_index('idx_transaction_date', 'transactions', ['transaction_date'])
    op.create_index('idx_payroll_run_date', 'payroll_runs', ['pay_date'])
    
    # Status field indexes for filtering
    op.create_index('idx_bill_status', 'bills', ['status'])
    op.create_index('idx_invoice_status', 'invoices', ['status'])
    op.create_index('idx_payment_status', 'payments', ['status'])
    op.create_index('idx_transaction_status', 'transactions', ['status'])
    op.create_index('idx_payroll_run_status', 'payroll_runs', ['status'])
    
    # Composite indexes for common query patterns
    op.create_index('idx_bill_company_status', 'bills', ['company_id', 'status'])
    op.create_index('idx_invoice_company_status', 'invoices', ['company_id', 'status'])
    op.create_index('idx_journal_entry_company_date', 'journal_entries', ['company_id', 'entry_date'])
    op.create_index('idx_audit_log_company_date', 'audit_logs', ['company_id', 'created_at'])

def downgrade():
    """Remove indexes"""
    
    # Drop composite indexes
    op.drop_index('idx_audit_log_company_date')
    op.drop_index('idx_journal_entry_company_date')
    op.drop_index('idx_invoice_company_status')
    op.drop_index('idx_bill_company_status')
    
    # Drop status indexes
    op.drop_index('idx_payroll_run_status')
    op.drop_index('idx_transaction_status')
    op.drop_index('idx_payment_status')
    op.drop_index('idx_invoice_status')
    op.drop_index('idx_bill_status')
    
    # Drop date indexes
    op.drop_index('idx_payroll_run_date')
    op.drop_index('idx_transaction_date')
    op.drop_index('idx_payment_date')
    op.drop_index('idx_invoice_due_date')
    op.drop_index('idx_invoice_date')
    op.drop_index('idx_bill_due_date')
    op.drop_index('idx_bill_date')
    op.drop_index('idx_journal_entry_date')
    
    # Drop foreign key indexes
    op.drop_index('idx_transaction_bank_account')
    op.drop_index('idx_invoice_customer')
    op.drop_index('idx_payment_bill')
    op.drop_index('idx_bill_vendor')
    op.drop_index('idx_audit_log_user')
    op.drop_index('idx_audit_log_company')
    op.drop_index('idx_journal_entry_credit_account')
    op.drop_index('idx_journal_entry_debit_account')
