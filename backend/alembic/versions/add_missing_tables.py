"""add_missing_tables

Revision ID: add_missing_tables
Revises: create_all_financial_modules
Create Date: 2025-01-25 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import DECIMAL

# revision identifiers, used by Alembic.
revision = 'add_missing_tables'
down_revision = 'create_all_financial_modules'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Journal Entry Lines
    op.create_table('journal_entry_lines',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('journal_entry_id', sa.String(), nullable=False),
        sa.Column('account_id', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('debit_amount', DECIMAL(15, 2), default=0),
        sa.Column('credit_amount', DECIMAL(15, 2), default=0),
        sa.Column('line_number', sa.Integer()),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id']),
        sa.ForeignKeyConstraint(['account_id'], ['chart_of_accounts.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Trial Balance
    op.create_table('trial_balance',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('account_id', sa.String(), nullable=False),
        sa.Column('opening_balance', DECIMAL(15, 2), default=0),
        sa.Column('debit_total', DECIMAL(15, 2), default=0),
        sa.Column('credit_total', DECIMAL(15, 2), default=0),
        sa.Column('closing_balance', DECIMAL(15, 2), default=0),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['account_id'], ['chart_of_accounts.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # AP Payments
    op.create_table('ap_payments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('vendor_id', sa.String(), nullable=False),
        sa.Column('payment_number', sa.String(50), nullable=False),
        sa.Column('payment_date', sa.DateTime(), nullable=False),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('amount', DECIMAL(15, 2), nullable=False),
        sa.Column('reference', sa.String(100)),
        sa.Column('status', sa.String(20), default='completed'),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Credit Memos
    op.create_table('credit_memos',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('vendor_id', sa.String(), nullable=False),
        sa.Column('memo_number', sa.String(50), nullable=False),
        sa.Column('memo_date', sa.DateTime(), nullable=False),
        sa.Column('amount', DECIMAL(15, 2), nullable=False),
        sa.Column('reason', sa.Text()),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Form 1099
    op.create_table('form_1099',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('vendor_id', sa.String(), nullable=False),
        sa.Column('tax_year', sa.Integer(), nullable=False),
        sa.Column('total_payments', DECIMAL(15, 2), default=0),
        sa.Column('form_type', sa.String(20), default='1099-NEC'),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # AR Invoices
    op.create_table('ar_invoices',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('invoice_number', sa.String(50), nullable=False),
        sa.Column('invoice_date', sa.DateTime(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('subtotal', DECIMAL(15, 2), default=0),
        sa.Column('tax_amount', DECIMAL(15, 2), default=0),
        sa.Column('total_amount', DECIMAL(15, 2), default=0),
        sa.Column('paid_amount', DECIMAL(15, 2), default=0),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # AR Payments
    op.create_table('ar_payments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('payment_number', sa.String(50), nullable=False),
        sa.Column('payment_date', sa.DateTime(), nullable=False),
        sa.Column('payment_method', sa.String(50)),
        sa.Column('amount', DECIMAL(15, 2), nullable=False),
        sa.Column('reference', sa.String(100)),
        sa.Column('status', sa.String(20), default='completed'),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Collections
    op.create_table('collections',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('invoice_id', sa.String(), nullable=False),
        sa.Column('collection_date', sa.DateTime(), nullable=False),
        sa.Column('amount_collected', DECIMAL(15, 2), nullable=False),
        sa.Column('collection_method', sa.String(50)),
        sa.Column('notes', sa.Text()),
        sa.Column('status', sa.String(20), default='completed'),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.ForeignKeyConstraint(['invoice_id'], ['ar_invoices.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Cash Transactions
    op.create_table('cash_transactions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('bank_account_id', sa.String(), nullable=False),
        sa.Column('transaction_date', sa.DateTime(), nullable=False),
        sa.Column('transaction_type', sa.String(20), nullable=False),
        sa.Column('amount', DECIMAL(15, 2), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('reference', sa.String(100)),
        sa.Column('reconciled', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Bank Reconciliation
    op.create_table('bank_reconciliations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('bank_account_id', sa.String(), nullable=False),
        sa.Column('reconciliation_date', sa.DateTime(), nullable=False),
        sa.Column('statement_balance', DECIMAL(15, 2), nullable=False),
        sa.Column('book_balance', DECIMAL(15, 2), nullable=False),
        sa.Column('adjusted_balance', DECIMAL(15, 2), nullable=False),
        sa.Column('status', sa.String(20), default='in_progress'),
        sa.Column('created_by', sa.String()),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Budget Lines
    op.create_table('budget_lines',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('budget_plan_id', sa.String(), nullable=False),
        sa.Column('account_id', sa.String(), nullable=False),
        sa.Column('department', sa.String(100)),
        sa.Column('budgeted_amount', DECIMAL(15, 2), default=0),
        sa.Column('actual_amount', DECIMAL(15, 2), default=0),
        sa.Column('variance', DECIMAL(15, 2), default=0),
        sa.Column('notes', sa.Text()),
        sa.ForeignKeyConstraint(['budget_plan_id'], ['budget_plans.id']),
        sa.ForeignKeyConstraint(['account_id'], ['chart_of_accounts.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Tax Jurisdictions
    op.create_table('tax_jurisdictions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('jurisdiction_name', sa.String(255), nullable=False),
        sa.Column('jurisdiction_code', sa.String(20), nullable=False),
        sa.Column('jurisdiction_type', sa.String(50)),
        sa.Column('country', sa.String(100)),
        sa.Column('state_province', sa.String(100)),
        sa.Column('city', sa.String(100)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('jurisdiction_code')
    )

    # Tax Exemptions
    op.create_table('tax_exemptions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('exemption_name', sa.String(255), nullable=False),
        sa.Column('exemption_code', sa.String(50)),
        sa.Column('tax_type', sa.String(50)),
        sa.Column('exemption_percentage', DECIMAL(5, 2), default=100.0),
        sa.Column('effective_date', sa.DateTime(), nullable=False),
        sa.Column('expiry_date', sa.DateTime()),
        sa.Column('certificate_number', sa.String(100)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Tax Returns
    op.create_table('tax_returns',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('return_type', sa.String(50), nullable=False),
        sa.Column('tax_period', sa.String(50)),
        sa.Column('filing_date', sa.DateTime()),
        sa.Column('due_date', sa.DateTime(), nullable=False),
        sa.Column('total_tax_due', DECIMAL(15, 2), default=0),
        sa.Column('tax_paid', DECIMAL(15, 2), default=0),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('filed_by', sa.String()),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['filed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Payroll Tables
    op.create_table('pay_runs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('pay_period_start', sa.Date(), nullable=False),
        sa.Column('pay_period_end', sa.Date(), nullable=False),
        sa.Column('pay_date', sa.Date(), nullable=False),
        sa.Column('total_gross_pay', DECIMAL(15, 2), default=0),
        sa.Column('total_deductions', DECIMAL(15, 2), default=0),
        sa.Column('total_net_pay', DECIMAL(15, 2), default=0),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('processed_by', sa.String()),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['processed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('payslips',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('pay_run_id', sa.String(), nullable=False),
        sa.Column('employee_id', sa.String(), nullable=False),
        sa.Column('gross_pay', DECIMAL(15, 2), default=0),
        sa.Column('total_deductions', DECIMAL(15, 2), default=0),
        sa.Column('net_pay', DECIMAL(15, 2), default=0),
        sa.Column('hours_worked', DECIMAL(8, 2)),
        sa.Column('overtime_hours', DECIMAL(8, 2)),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['pay_run_id'], ['pay_runs.id']),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # HRM Tables
    op.create_table('leave_requests',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('employee_id', sa.String(), nullable=False),
        sa.Column('leave_type', sa.String(50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('days_requested', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text()),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('approved_by', sa.String()),
        sa.Column('approved_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('attendance',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('employee_id', sa.String(), nullable=False),
        sa.Column('attendance_date', sa.Date(), nullable=False),
        sa.Column('clock_in', sa.DateTime()),
        sa.Column('clock_out', sa.DateTime()),
        sa.Column('hours_worked', DECIMAL(8, 2)),
        sa.Column('overtime_hours', DECIMAL(8, 2)),
        sa.Column('status', sa.String(20), default='present'),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Inventory Tables
    op.create_table('inventory_locations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('location_code', sa.String(20), nullable=False),
        sa.Column('location_name', sa.String(255), nullable=False),
        sa.Column('address', sa.Text()),
        sa.Column('location_type', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('location_code')
    )

    op.create_table('inventory_transactions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('item_id', sa.String(), nullable=False),
        sa.Column('location_id', sa.String(), nullable=False),
        sa.Column('transaction_type', sa.String(20), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_cost', DECIMAL(15, 2)),
        sa.Column('total_value', DECIMAL(15, 2)),
        sa.Column('reference', sa.String(100)),
        sa.Column('notes', sa.Text()),
        sa.Column('transaction_date', sa.DateTime()),
        sa.Column('created_by', sa.String()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['item_id'], ['inventory_items.id']),
        sa.ForeignKeyConstraint(['location_id'], ['inventory_locations.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # AI/BI Tables
    op.create_table('ai_insights',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('insight_type', sa.String(100), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('confidence_score', DECIMAL(5, 2)),
        sa.Column('data_source', sa.String(100)),
        sa.Column('insight_data', sa.JSON()),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('ai_insights')
    op.drop_table('inventory_transactions')
    op.drop_table('inventory_locations')
    op.drop_table('attendance')
    op.drop_table('leave_requests')
    op.drop_table('payslips')
    op.drop_table('pay_runs')
    op.drop_table('tax_returns')
    op.drop_table('tax_exemptions')
    op.drop_table('tax_jurisdictions')
    op.drop_table('budget_lines')
    op.drop_table('bank_reconciliations')
    op.drop_table('cash_transactions')
    op.drop_table('collections')
    op.drop_table('ar_payments')
    op.drop_table('ar_invoices')
    op.drop_table('form_1099')
    op.drop_table('credit_memos')
    op.drop_table('ap_payments')
    op.drop_table('trial_balance')
    op.drop_table('journal_entry_lines')