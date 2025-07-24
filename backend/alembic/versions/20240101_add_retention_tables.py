"""Add retention tables

Revision ID: 20240101_add_retention_tables
Revises: 20240101_add_compliance_tables
Create Date: 2024-01-01 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


# revision identifiers, used by Alembic.
revision = '20240101_add_retention_tables'
down_revision = '20240101_add_compliance_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create data_retention_policies table
    op.create_table(
        'data_retention_policies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('policy_name', sa.String(200), nullable=False),
        sa.Column('policy_code', sa.String(50), nullable=False, unique=True),
        sa.Column('table_name', sa.String(100), nullable=False),
        sa.Column('data_category', sa.String(100), nullable=False),
        sa.Column('retention_period_days', sa.Integer, nullable=False),
        sa.Column('retention_action', sa.String(20), nullable=False, default='delete'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('legal_basis', sa.String(200), nullable=True),
        sa.Column('conditions', JSON, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('last_executed', sa.DateTime, nullable=True),
        sa.Column('next_execution', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create retention_executions table
    op.create_table(
        'retention_executions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('policy_id', UUID(as_uuid=True), nullable=False),
        sa.Column('execution_date', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('records_processed', sa.Integer, nullable=False, default=0),
        sa.Column('records_deleted', sa.Integer, nullable=False, default=0),
        sa.Column('records_archived', sa.Integer, nullable=False, default=0),
        sa.Column('records_anonymized', sa.Integer, nullable=False, default=0),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('execution_time_seconds', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_retention_policies_status', 'data_retention_policies', ['status'])
    op.create_index('ix_retention_policies_next_execution', 'data_retention_policies', ['next_execution'])
    op.create_index('ix_retention_executions_policy_date', 'retention_executions', ['policy_id', 'execution_date'])


def downgrade():
    op.drop_table('retention_executions')
    op.drop_table('data_retention_policies')