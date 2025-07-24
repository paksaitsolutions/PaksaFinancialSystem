"""Add backup tables

Revision ID: 20240101_add_backup_tables
Revises: 20240101_add_retention_tables
Create Date: 2024-01-01 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


# revision identifiers, used by Alembic.
revision = '20240101_add_backup_tables'
down_revision = '20240101_add_retention_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create backups table
    op.create_table(
        'backups',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('backup_name', sa.String(200), nullable=False),
        sa.Column('backup_type', sa.String(20), nullable=False, default='full'),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('compression_type', sa.String(20), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('tables_included', JSON, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('checksum', sa.String(64), nullable=True),
        sa.Column('initiated_by', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create restore_operations table
    op.create_table(
        'restore_operations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('restore_name', sa.String(200), nullable=False),
        sa.Column('backup_id', UUID(as_uuid=True), nullable=False),
        sa.Column('restore_point', sa.DateTime, nullable=True),
        sa.Column('tables_to_restore', JSON, nullable=True),
        sa.Column('overwrite_existing', sa.Boolean, nullable=False, default=False),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('records_restored', sa.Integer, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('initiated_by', UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create backup_schedules table
    op.create_table(
        'backup_schedules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('schedule_name', sa.String(200), nullable=False),
        sa.Column('backup_type', sa.String(20), nullable=False, default='full'),
        sa.Column('cron_expression', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('retention_days', sa.Integer, nullable=False, default=30),
        sa.Column('compression_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('last_run', sa.DateTime, nullable=True),
        sa.Column('next_run', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_backups_status', 'backups', ['status'])
    op.create_index('ix_backups_type', 'backups', ['backup_type'])
    op.create_index('ix_restore_operations_backup_id', 'restore_operations', ['backup_id'])
    op.create_index('ix_backup_schedules_active', 'backup_schedules', ['is_active'])


def downgrade():
    op.drop_table('backup_schedules')
    op.drop_table('restore_operations')
    op.drop_table('backups')