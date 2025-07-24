"""Add period close tables

Revision ID: 20240101_add_period_close_tables
Revises: 20240101_add_allocation_tables
Create Date: 2024-01-01 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '20240101_add_period_close_tables'
down_revision = '20240101_add_allocation_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create accounting_periods table
    op.create_table(
        'accounting_periods',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('period_name', sa.String(50), nullable=False),
        sa.Column('period_type', sa.String(20), nullable=False),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='open'),
        sa.Column('closed_by', UUID(as_uuid=True), nullable=True),
        sa.Column('closed_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create period_closes table
    op.create_table(
        'period_closes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('close_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('period_id', UUID(as_uuid=True), sa.ForeignKey('accounting_periods.id'), nullable=False),
        sa.Column('close_type', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='closing'),
        sa.Column('initiated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('initiated_by', UUID(as_uuid=True), nullable=False),
        sa.Column('completed_by', UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create period_close_tasks table
    op.create_table(
        'period_close_tasks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('period_close_id', UUID(as_uuid=True), sa.ForeignKey('period_closes.id'), nullable=False),
        sa.Column('task_name', sa.String(100), nullable=False),
        sa.Column('task_description', sa.Text, nullable=True),
        sa.Column('task_order', sa.Integer, nullable=False),
        sa.Column('is_required', sa.Boolean, nullable=False, default=True),
        sa.Column('is_automated', sa.Boolean, nullable=False, default=False),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('assigned_to', UUID(as_uuid=True), nullable=True),
        sa.Column('completed_by', UUID(as_uuid=True), nullable=True),
        sa.Column('result_message', sa.Text, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_accounting_periods_dates', 'accounting_periods', ['start_date', 'end_date'])
    op.create_index('ix_accounting_periods_status', 'accounting_periods', ['status'])
    op.create_index('ix_period_closes_period_status', 'period_closes', ['period_id', 'status'])
    op.create_index('ix_period_close_tasks_close_order', 'period_close_tasks', ['period_close_id', 'task_order'])


def downgrade():
    op.drop_table('period_close_tasks')
    op.drop_table('period_closes')
    op.drop_table('accounting_periods')