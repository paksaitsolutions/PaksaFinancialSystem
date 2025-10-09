"""Create payroll tables

Revision ID: 20250124_04_create_payroll_tables
Revises: 20250124_03_create_tax_tables
Create Date: 2025-01-24 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20250124_04_create_payroll_tables'
down_revision = '20250124_03_create_tax_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Create payroll_employees table
    op.create_table('payroll_employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', sa.String(length=50), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('job_title', sa.String(length=100), nullable=False),
        sa.Column('employment_type', sa.String(length=20), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('base_salary', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('pay_frequency', sa.String(length=20), nullable=True),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('tax_exemptions', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_payroll_employees_employee_id'), 'payroll_employees', ['employee_id'], unique=False)
    op.create_index(op.f('ix_payroll_employees_email'), 'payroll_employees', ['email'], unique=False)

    # Create pay_runs table
    op.create_table('pay_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('run_number', sa.String(length=50), nullable=False),
        sa.Column('pay_period_start', sa.Date(), nullable=False),
        sa.Column('pay_period_end', sa.Date(), nullable=False),
        sa.Column('pay_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('total_gross_pay', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('total_deductions', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('total_net_pay', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('total_taxes', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('run_number')
    )
    op.create_index(op.f('ix_pay_runs_run_number'), 'pay_runs', ['run_number'], unique=False)

    # Create pay_run_employees table
    op.create_table('pay_run_employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pay_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('gross_pay', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('total_deductions', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('total_taxes', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('net_pay', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('regular_hours', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('overtime_hours', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('is_processed', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['payroll_employees.id'], ),
        sa.ForeignKeyConstraint(['pay_run_id'], ['pay_runs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create payslips table
    op.create_table('payslips',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payslip_number', sa.String(length=50), nullable=False),
        sa.Column('pay_run_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pay_period_start', sa.Date(), nullable=False),
        sa.Column('pay_period_end', sa.Date(), nullable=False),
        sa.Column('pay_date', sa.Date(), nullable=False),
        sa.Column('base_salary', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('overtime_pay', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('bonus', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('commission', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('allowances', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('gross_pay', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('federal_tax', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('state_tax', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('social_security', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('medicare', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('health_insurance', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('retirement_401k', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('other_deductions', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('total_deductions', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('net_pay', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('regular_hours', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('overtime_hours', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('is_paid', sa.Boolean(), nullable=True),
        sa.Column('paid_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['payroll_employees.id'], ),
        sa.ForeignKeyConstraint(['pay_run_id'], ['pay_runs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payslip_number')
    )
    op.create_index(op.f('ix_payslips_payslip_number'), 'payslips', ['payslip_number'], unique=False)

    # Create payroll_items table
    op.create_table('payroll_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('item_type', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('is_taxable', sa.Boolean(), nullable=True),
        sa.Column('is_pre_tax', sa.Boolean(), nullable=True),
        sa.Column('calculation_method', sa.String(length=20), nullable=True),
        sa.Column('default_amount', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('percentage', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('expense_account', sa.String(length=20), nullable=True),
        sa.Column('liability_account', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_payroll_items_name'), 'payroll_items', ['name'], unique=False)
    op.create_index(op.f('ix_payroll_items_code'), 'payroll_items', ['code'], unique=False)

    # Create employee_payroll_items table
    op.create_table('employee_payroll_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payroll_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('percentage', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['payroll_employees.id'], ),
        sa.ForeignKeyConstraint(['payroll_item_id'], ['payroll_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('employee_payroll_items')
    op.drop_index(op.f('ix_payroll_items_code'), table_name='payroll_items')
    op.drop_index(op.f('ix_payroll_items_name'), table_name='payroll_items')
    op.drop_table('payroll_items')
    op.drop_index(op.f('ix_payslips_payslip_number'), table_name='payslips')
    op.drop_table('payslips')
    op.drop_table('pay_run_employees')
    op.drop_index(op.f('ix_pay_runs_run_number'), table_name='pay_runs')
    op.drop_table('pay_runs')
    op.drop_index(op.f('ix_payroll_employees_email'), table_name='payroll_employees')
    op.drop_index(op.f('ix_payroll_employees_employee_id'), table_name='payroll_employees')
    op.drop_table('payroll_employees')