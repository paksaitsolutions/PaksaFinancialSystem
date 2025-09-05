"""Create HRM tables

Revision ID: hrm_001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'hrm_001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create hrm_employees table
    op.create_table('hrm_employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', sa.String(length=50), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('middle_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=50), nullable=False),
        sa.Column('job_title', sa.String(length=100), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('employment_type', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(length=1), nullable=True),
        sa.Column('marital_status', sa.String(length=20), nullable=True),
        sa.Column('national_id', sa.String(length=50), nullable=True),
        sa.Column('address_line1', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('base_salary', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('payment_frequency', sa.String(length=20), nullable=False),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('account_number', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hrm_employees_id'), 'hrm_employees', ['id'], unique=False)
    op.create_index(op.f('ix_hrm_employees_tenant_id'), 'hrm_employees', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_hrm_employees_employee_id'), 'hrm_employees', ['employee_id'], unique=True)
    op.create_index(op.f('ix_hrm_employees_email'), 'hrm_employees', ['email'], unique=True)

    # Create hrm_leave_requests table
    op.create_table('hrm_leave_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('leave_type', sa.String(length=50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('days_requested', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['hrm_employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hrm_leave_requests_id'), 'hrm_leave_requests', ['id'], unique=False)

    # Create hrm_leave_balances table
    op.create_table('hrm_leave_balances',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('leave_type', sa.String(length=50), nullable=False),
        sa.Column('total_days', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('used_days', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('remaining_days', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('year', sa.String(length=4), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['hrm_employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hrm_leave_balances_id'), 'hrm_leave_balances', ['id'], unique=False)

    # Create hrm_leave_policies table
    op.create_table('hrm_leave_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('leave_type', sa.String(length=50), nullable=False),
        sa.Column('days_per_year', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('carry_forward_days', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hrm_leave_policies_id'), 'hrm_leave_policies', ['id'], unique=False)
    op.create_index(op.f('ix_hrm_leave_policies_tenant_id'), 'hrm_leave_policies', ['tenant_id'], unique=False)

    # Create hrm_attendance_records table
    op.create_table('hrm_attendance_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('check_in_time', sa.Time(), nullable=True),
        sa.Column('check_out_time', sa.Time(), nullable=True),
        sa.Column('hours_worked', sa.String(length=10), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['hrm_employees.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hrm_attendance_records_id'), 'hrm_attendance_records', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_hrm_attendance_records_id'), table_name='hrm_attendance_records')
    op.drop_table('hrm_attendance_records')
    op.drop_index(op.f('ix_hrm_leave_policies_tenant_id'), table_name='hrm_leave_policies')
    op.drop_index(op.f('ix_hrm_leave_policies_id'), table_name='hrm_leave_policies')
    op.drop_table('hrm_leave_policies')
    op.drop_index(op.f('ix_hrm_leave_balances_id'), table_name='hrm_leave_balances')
    op.drop_table('hrm_leave_balances')
    op.drop_index(op.f('ix_hrm_leave_requests_id'), table_name='hrm_leave_requests')
    op.drop_table('hrm_leave_requests')
    op.drop_index(op.f('ix_hrm_employees_email'), table_name='hrm_employees')
    op.drop_index(op.f('ix_hrm_employees_employee_id'), table_name='hrm_employees')
    op.drop_index(op.f('ix_hrm_employees_tenant_id'), table_name='hrm_employees')
    op.drop_index(op.f('ix_hrm_employees_id'), table_name='hrm_employees')
    op.drop_table('hrm_employees')