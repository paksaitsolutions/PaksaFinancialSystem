"""Add operations tables

Revision ID: 20240102_add_operations_tables
Revises: 20240102_add_user_activity_tables
Create Date: 2024-01-02 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


# revision identifiers, used by Alembic.
revision = '20240102_add_operations_tables'
down_revision = '20240102_add_user_activity_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create system_logs table
    op.create_table(
        'system_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('level', sa.String(20), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('module', sa.String(100), nullable=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create system_alerts table
    op.create_table(
        'system_alerts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('alert_type', sa.String(50), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('resolved', sa.Boolean, nullable=False, default=False),
        sa.Column('resolved_at', sa.DateTime, nullable=True),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create backup_records table
    op.create_table(
        'backup_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('backup_type', sa.String(50), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='completed'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_system_logs_level', 'system_logs', ['level'])
    op.create_index('ix_system_logs_created', 'system_logs', ['created_at'])
    op.create_index('ix_system_alerts_resolved', 'system_alerts', ['resolved'])
    op.create_index('ix_system_alerts_severity', 'system_alerts', ['severity'])
    op.create_index('ix_backup_records_type', 'backup_records', ['backup_type'])
    op.create_index('ix_backup_records_status', 'backup_records', ['status'])


def downgrade():
    op.drop_table('backup_records')
    op.drop_table('system_alerts')
    op.drop_table('system_logs')