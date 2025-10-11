"""add_unified_models

Revision ID: add_unified_models
Revises: create_all_financial_modules
Create Date: 2025-01-25 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import DECIMAL

# revision identifiers, used by Alembic.
revision = 'add_unified_models'
down_revision = 'create_all_financial_modules'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add missing AP Payments table
    op.create_table('ap_payments',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False),
        sa.Column('vendor_id', UUID(as_uuid=True), nullable=False),
        sa.Column('payment_number', sa.String(50), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('amount', DECIMAL(15, 2), nullable=False),
        sa.Column('payment_method', sa.String(20), nullable=False),
        sa.Column('reference', sa.String(100)),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('created_by', sa.String()),
        sa.Column('updated_by', sa.String()),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_number')
    )

    # Add missing AR Invoices table
    op.create_table('ar_invoices',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_number', sa.String(50), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('subtotal', DECIMAL(15, 2), default=0),
        sa.Column('tax_amount', DECIMAL(15, 2), default=0),
        sa.Column('total_amount', DECIMAL(15, 2), nullable=False),
        sa.Column('paid_amount', DECIMAL(15, 2), default=0),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('created_by', sa.String()),
        sa.Column('updated_by', sa.String()),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_number')
    )

    # Add missing AR Payments table
    op.create_table('ar_payments',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', UUID(as_uuid=True), nullable=False),
        sa.Column('payment_number', sa.String(50), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('amount', DECIMAL(15, 2), nullable=False),
        sa.Column('payment_method', sa.String(20), nullable=False),
        sa.Column('reference', sa.String(100)),
        sa.Column('status', sa.String(20), default='completed'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('created_by', sa.String()),
        sa.Column('updated_by', sa.String()),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_number')
    )

    # Add missing line items tables
    op.create_table('ap_invoice_line_items',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('quantity', DECIMAL(10, 2), default=1),
        sa.Column('unit_price', DECIMAL(15, 2), nullable=False),
        sa.Column('amount', DECIMAL(15, 2), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['ap_invoices.id']),
        sa.ForeignKeyConstraint(['account_id'], ['chart_of_accounts.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('ar_invoice_line_items',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('quantity', DECIMAL(10, 2), default=1),
        sa.Column('unit_price', DECIMAL(15, 2), nullable=False),
        sa.Column('amount', DECIMAL(15, 2), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['ar_invoices.id']),
        sa.ForeignKeyConstraint(['account_id'], ['chart_of_accounts.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Add association tables
    op.create_table('ap_invoice_payments',
        sa.Column('invoice_id', UUID(as_uuid=True), nullable=False),
        sa.Column('payment_id', UUID(as_uuid=True), nullable=False),
        sa.Column('amount', DECIMAL(15, 2), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['ap_invoices.id']),
        sa.ForeignKeyConstraint(['payment_id'], ['ap_payments.id']),
        sa.PrimaryKeyConstraint('invoice_id', 'payment_id')
    )

    op.create_table('ar_invoice_payments',
        sa.Column('invoice_id', UUID(as_uuid=True), nullable=False),
        sa.Column('payment_id', UUID(as_uuid=True), nullable=False),
        sa.Column('amount', DECIMAL(15, 2), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['ar_invoices.id']),
        sa.ForeignKeyConstraint(['payment_id'], ['ar_payments.id']),
        sa.PrimaryKeyConstraint('invoice_id', 'payment_id')
    )

    # Add missing journal entry lines table
    op.create_table('journal_entry_lines',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('journal_entry_id', UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('debit_amount', DECIMAL(15, 2), default=0),
        sa.Column('credit_amount', DECIMAL(15, 2), default=0),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entries.id']),
        sa.ForeignKeyConstraint(['account_id'], ['chart_of_accounts.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Add missing employee-related tables
    op.create_table('departments',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False),
        sa.Column('department_code', sa.String(20), nullable=False),
        sa.Column('department_name', sa.String(255), nullable=False),
        sa.Column('manager_id', UUID(as_uuid=True)),
        sa.Column('cost_center', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('created_by', sa.String()),
        sa.Column('updated_by', sa.String()),
        sa.ForeignKeyConstraint(['manager_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('department_code')
    )

    # Update employees table to add department reference
    op.add_column('employees', sa.Column('department_id', UUID(as_uuid=True)))
    op.create_foreign_key('fk_employees_department', 'employees', 'departments', ['department_id'], ['id'])

    # Add payroll tables
    op.create_table('payroll_runs',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False),
        sa.Column('run_number', sa.String(50), nullable=False),
        sa.Column('pay_period_start', sa.Date(), nullable=False),
        sa.Column('pay_period_end', sa.Date(), nullable=False),
        sa.Column('pay_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('total_gross', DECIMAL(15, 2), default=0),
        sa.Column('total_deductions', DECIMAL(15, 2), default=0),
        sa.Column('total_net', DECIMAL(15, 2), default=0),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('created_by', sa.String()),
        sa.Column('updated_by', sa.String()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('run_number')
    )

    op.create_table('payroll_entries',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('payroll_run_id', UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', UUID(as_uuid=True), nullable=False),
        sa.Column('gross_pay', DECIMAL(15, 2), default=0),
        sa.Column('total_deductions', DECIMAL(15, 2), default=0),
        sa.Column('net_pay', DECIMAL(15, 2), default=0),
        sa.ForeignKeyConstraint(['payroll_run_id'], ['payroll_runs.id']),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Add leave requests table
    op.create_table('leave_requests',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', UUID(as_uuid=True), nullable=False),
        sa.Column('leave_type', sa.String(20), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('days_requested', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text()),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('created_by', sa.String()),
        sa.Column('updated_by', sa.String()),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('leave_requests')
    op.drop_table('payroll_entries')
    op.drop_table('payroll_runs')
    op.drop_constraint('fk_employees_department', 'employees', type_='foreignkey')
    op.drop_column('employees', 'department_id')
    op.drop_table('departments')
    op.drop_table('journal_entry_lines')
    op.drop_table('ar_invoice_payments')
    op.drop_table('ap_invoice_payments')
    op.drop_table('ar_invoice_line_items')
    op.drop_table('ap_invoice_line_items')
    op.drop_table('ar_payments')
    op.drop_table('ar_invoices')
    op.drop_table('ap_payments')