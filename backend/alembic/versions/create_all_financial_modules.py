"""create_all_financial_modules

Revision ID: create_all_financial_modules
Revises: 660b0d22ded4
Create Date: 2025-01-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import DECIMAL

# revision identifiers, used by Alembic.
revision = 'create_all_financial_modules'
down_revision = '660b0d22ded4'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Companies table
    op.create_table('companies',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Reference Data Tables
    op.create_table('countries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(3), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('currencies',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(3), nullable=False),
        sa.Column('symbol', sa.String(10)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )

    # General Ledger Tables
    op.create_table('chart_of_accounts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('account_code', sa.String(20), nullable=False),
        sa.Column('account_name', sa.String(255), nullable=False),
        sa.Column('account_type', sa.String(50), nullable=False),
        sa.Column('parent_id', sa.String()),
        sa.Column('balance', DECIMAL(15, 2), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['chart_of_accounts.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_code')
    )

    op.create_table('journal_entries',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('entry_number', sa.String(50), nullable=False),
        sa.Column('entry_date', sa.DateTime(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('reference', sa.String(100)),
        sa.Column('total_debit', DECIMAL(15, 2), default=0),
        sa.Column('total_credit', DECIMAL(15, 2), default=0),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('created_by', sa.String()),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Accounts Payable Tables
    op.create_table('vendors',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('vendor_code', sa.String(20), nullable=False),
        sa.Column('vendor_name', sa.String(255), nullable=False),
        sa.Column('contact_person', sa.String(255)),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('address', sa.Text()),
        sa.Column('tax_id', sa.String(50)),
        sa.Column('payment_terms', sa.String(50)),
        sa.Column('credit_limit', DECIMAL(15, 2), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vendor_code')
    )

    op.create_table('ap_invoices',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('vendor_id', sa.String(), nullable=False),
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
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Accounts Receivable Tables
    op.create_table('customers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('customer_code', sa.String(20), nullable=False),
        sa.Column('customer_name', sa.String(255), nullable=False),
        sa.Column('contact_person', sa.String(255)),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('address', sa.Text()),
        sa.Column('credit_limit', DECIMAL(15, 2), default=0),
        sa.Column('payment_terms', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('customer_code')
    )

    # Cash Management Tables
    op.create_table('bank_accounts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('account_name', sa.String(255), nullable=False),
        sa.Column('account_number', sa.String(50), nullable=False),
        sa.Column('bank_name', sa.String(255), nullable=False),
        sa.Column('routing_number', sa.String(50)),
        sa.Column('account_type', sa.String(50)),
        sa.Column('currency', sa.String(3), default='USD'),
        sa.Column('current_balance', DECIMAL(15, 2), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Budget Tables
    op.create_table('budget_plans',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('plan_name', sa.String(255), nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('total_budget', DECIMAL(15, 2), default=0),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('created_by', sa.String()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Tax Tables
    op.create_table('tax_rates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('tax_name', sa.String(255), nullable=False),
        sa.Column('tax_code', sa.String(20), nullable=False),
        sa.Column('rate_percentage', DECIMAL(5, 4), nullable=False),
        sa.Column('tax_type', sa.String(50)),
        sa.Column('jurisdiction', sa.String(100)),
        sa.Column('effective_date', sa.DateTime(), nullable=False),
        sa.Column('expiry_date', sa.DateTime()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tax_code')
    )

    # Employee/Payroll Tables
    op.create_table('employees',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('employee_number', sa.String(20), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('address', sa.Text()),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('termination_date', sa.Date()),
        sa.Column('job_title', sa.String(255)),
        sa.Column('department', sa.String(100)),
        sa.Column('salary', DECIMAL(15, 2)),
        sa.Column('hourly_rate', DECIMAL(10, 2)),
        sa.Column('employment_type', sa.String(50)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_number')
    )

    # Inventory Tables
    op.create_table('inventory_items',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('item_code', sa.String(50), nullable=False),
        sa.Column('item_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('category', sa.String(100)),
        sa.Column('unit_of_measure', sa.String(20)),
        sa.Column('cost_price', DECIMAL(15, 2)),
        sa.Column('selling_price', DECIMAL(15, 2)),
        sa.Column('reorder_level', sa.Integer(), default=0),
        sa.Column('maximum_level', sa.Integer()),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_code')
    )

    # Fixed Assets Tables
    op.create_table('fixed_assets',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('asset_number', sa.String(50), nullable=False),
        sa.Column('asset_name', sa.String(255), nullable=False),
        sa.Column('asset_category', sa.String(100)),
        sa.Column('purchase_date', sa.DateTime(), nullable=False),
        sa.Column('purchase_cost', DECIMAL(15, 2), nullable=False),
        sa.Column('accumulated_depreciation', DECIMAL(15, 2), default=0),
        sa.Column('current_value', DECIMAL(15, 2)),
        sa.Column('depreciation_method', sa.String(50)),
        sa.Column('useful_life_years', sa.Integer()),
        sa.Column('salvage_value', DECIMAL(15, 2)),
        sa.Column('location', sa.String(255)),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_number')
    )

def downgrade() -> None:
    op.drop_table('fixed_assets')
    op.drop_table('inventory_items')
    op.drop_table('employees')
    op.drop_table('tax_rates')
    op.drop_table('budget_plans')
    op.drop_table('bank_accounts')
    op.drop_table('customers')
    op.drop_table('ap_invoices')
    op.drop_table('vendors')
    op.drop_table('journal_entries')
    op.drop_table('chart_of_accounts')
    op.drop_table('currencies')
    op.drop_table('countries')
    op.drop_table('companies')