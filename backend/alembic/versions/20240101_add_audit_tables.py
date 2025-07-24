"""Add audit tables

Revision ID: 20240101_add_audit_tables
Revises: 20240101_add_session_tables
Create Date: 2024-01-01 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


# revision identifiers, used by Alembic.
revision = '20240101_add_audit_tables'
down_revision = '20240101_add_session_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('session_id', UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(20), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(100), nullable=True),
        sa.Column('endpoint', sa.String(200), nullable=True),
        sa.Column('method', sa.String(10), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('old_values', JSON, nullable=True),
        sa.Column('new_values', JSON, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create audit_configs table
    op.create_table(
        'audit_configs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(100), nullable=False, default='Default Audit Config'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('log_read_operations', sa.String(10), nullable=False, default='false'),
        sa.Column('log_failed_attempts', sa.String(10), nullable=False, default='true'),
        sa.Column('retention_days', sa.String(10), nullable=False, default='2555'),
        sa.Column('excluded_resources', JSON, nullable=True),
        sa.Column('sensitive_resources', JSON, nullable=True),
        sa.Column('is_active', sa.String(10), nullable=False, default='true'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_audit_logs_user_timestamp', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('ix_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])


def downgrade():
    op.drop_table('audit_configs')
    op.drop_table('audit_logs')