"""Add database indexes for improved performance

Revision ID: 20240101_add_indexes
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20240101_add_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create indexes for common lookup patterns
    
    # User indexes
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_is_active'), 'users', ['is_active'])
    
    # General Ledger indexes
    op.create_index(op.f('ix_gl_account_code'), 'gl_account', ['code'], unique=True)
    op.create_index(op.f('ix_gl_account_parent_id'), 'gl_account', ['parent_id'])
    op.create_index(op.f('ix_gl_account_account_type'), 'gl_account', ['account_type'])
    
    op.create_index(op.f('ix_journal_entry_entry_date'), 'journal_entry', ['entry_date'])
    op.create_index(op.f('ix_journal_entry_posting_date'), 'journal_entry', ['posting_date'])
    op.create_index(op.f('ix_journal_entry_status'), 'journal_entry', ['status'])
    
    op.create_index(op.f('ix_journal_line_journal_id'), 'journal_line', ['journal_id'])
    op.create_index(op.f('ix_journal_line_account_id'), 'journal_line', ['account_id'])
    
    # Accounts Payable indexes
    op.create_index(op.f('ix_vendor_name'), 'vendor', ['name'])
    op.create_index(op.f('ix_vendor_tax_id'), 'vendor', ['tax_id'])
    
    op.create_index(op.f('ix_ap_invoice_vendor_id'), 'ap_invoice', ['vendor_id'])
    op.create_index(op.f('ix_ap_invoice_invoice_date'), 'ap_invoice', ['invoice_date'])
    op.create_index(op.f('ix_ap_invoice_due_date'), 'ap_invoice', ['due_date'])
    op.create_index(op.f('ix_ap_invoice_status'), 'ap_invoice', ['status'])
    
    # Accounts Receivable indexes
    op.create_index(op.f('ix_customer_name'), 'customer', ['name'])
    op.create_index(op.f('ix_customer_tax_id'), 'customer', ['tax_id'])
    
    op.create_index(op.f('ix_ar_invoice_customer_id'), 'ar_invoice', ['customer_id'])
    op.create_index(op.f('ix_ar_invoice_invoice_date'), 'ar_invoice', ['invoice_date'])
    op.create_index(op.f('ix_ar_invoice_due_date'), 'ar_invoice', ['due_date'])
    op.create_index(op.f('ix_ar_invoice_status'), 'ar_invoice', ['status'])
    
    # Payroll indexes
    op.create_index(op.f('ix_employee_employee_id'), 'employee', ['employee_id'], unique=True)
    op.create_index(op.f('ix_employee_email'), 'employee', ['email'])
    op.create_index(op.f('ix_employee_status'), 'employee', ['status'])
    
    op.create_index(op.f('ix_payroll_run_pay_period_id'), 'payroll_run', ['pay_period_id'])
    op.create_index(op.f('ix_payroll_run_status'), 'payroll_run', ['status'])
    
    # Common indexes for all tables with soft delete
    op.create_index(op.f('ix_users_deleted_at'), 'users', ['deleted_at'])
    op.create_index(op.f('ix_gl_account_deleted_at'), 'gl_account', ['deleted_at'])
    op.create_index(op.f('ix_journal_entry_deleted_at'), 'journal_entry', ['deleted_at'])
    op.create_index(op.f('ix_vendor_deleted_at'), 'vendor', ['deleted_at'])
    op.create_index(op.f('ix_customer_deleted_at'), 'customer', ['deleted_at'])
    op.create_index(op.f('ix_employee_deleted_at'), 'employee', ['deleted_at'])


def downgrade() -> None:
    # Drop all indexes created in upgrade
    
    # User indexes
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_is_active'), table_name='users')
    
    # General Ledger indexes
    op.drop_index(op.f('ix_gl_account_code'), table_name='gl_account')
    op.drop_index(op.f('ix_gl_account_parent_id'), table_name='gl_account')
    op.drop_index(op.f('ix_gl_account_account_type'), table_name='gl_account')
    
    op.drop_index(op.f('ix_journal_entry_entry_date'), table_name='journal_entry')
    op.drop_index(op.f('ix_journal_entry_posting_date'), table_name='journal_entry')
    op.drop_index(op.f('ix_journal_entry_status'), table_name='journal_entry')
    
    op.drop_index(op.f('ix_journal_line_journal_id'), table_name='journal_line')
    op.drop_index(op.f('ix_journal_line_account_id'), table_name='journal_line')
    
    # Accounts Payable indexes
    op.drop_index(op.f('ix_vendor_name'), table_name='vendor')
    op.drop_index(op.f('ix_vendor_tax_id'), table_name='vendor')
    
    op.drop_index(op.f('ix_ap_invoice_vendor_id'), table_name='ap_invoice')
    op.drop_index(op.f('ix_ap_invoice_invoice_date'), table_name='ap_invoice')
    op.drop_index(op.f('ix_ap_invoice_due_date'), table_name='ap_invoice')
    op.drop_index(op.f('ix_ap_invoice_status'), table_name='ap_invoice')
    
    # Accounts Receivable indexes
    op.drop_index(op.f('ix_customer_name'), table_name='customer')
    op.drop_index(op.f('ix_customer_tax_id'), table_name='customer')
    
    op.drop_index(op.f('ix_ar_invoice_customer_id'), table_name='ar_invoice')
    op.drop_index(op.f('ix_ar_invoice_invoice_date'), table_name='ar_invoice')
    op.drop_index(op.f('ix_ar_invoice_due_date'), table_name='ar_invoice')
    op.drop_index(op.f('ix_ar_invoice_status'), table_name='ar_invoice')
    
    # Payroll indexes
    op.drop_index(op.f('ix_employee_employee_id'), table_name='employee')
    op.drop_index(op.f('ix_employee_email'), table_name='employee')
    op.drop_index(op.f('ix_employee_status'), table_name='employee')
    
    op.drop_index(op.f('ix_payroll_run_pay_period_id'), table_name='payroll_run')
    op.drop_index(op.f('ix_payroll_run_status'), table_name='payroll_run')
    
    # Common indexes for all tables with soft delete
    op.drop_index(op.f('ix_users_deleted_at'), table_name='users')
    op.drop_index(op.f('ix_gl_account_deleted_at'), table_name='gl_account')
    op.drop_index(op.f('ix_journal_entry_deleted_at'), table_name='journal_entry')
    op.drop_index(op.f('ix_vendor_deleted_at'), table_name='vendor')
    op.drop_index(op.f('ix_customer_deleted_at'), table_name='customer')
    op.drop_index(op.f('ix_employee_deleted_at'), table_name='employee')