"""Add migration tables

Revision ID: 20240102_add_migration_tables
Revises: 20240102_add_operations_tables
Create Date: 2024-01-02 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


# revision identifiers, used by Alembic.
revision = '20240102_add_migration_tables'
down_revision = '20240102_add_operations_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create import_jobs table
    op.create_table(
        'import_jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('job_name', sa.String(200), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('data_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('total_records', sa.Integer, nullable=True),
        sa.Column('processed_records', sa.Integer, nullable=False, default=0),
        sa.Column('error_records', sa.Integer, nullable=False, default=0),
        sa.Column('error_log', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create export_jobs table
    op.create_table(
        'export_jobs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('job_name', sa.String(200), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('data_type', sa.String(50), nullable=False),
        sa.Column('format', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('total_records', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_import_jobs_status', 'import_jobs', ['status'])
    op.create_index('ix_import_jobs_data_type', 'import_jobs', ['data_type'])
    op.create_index('ix_export_jobs_status', 'export_jobs', ['status'])
    op.create_index('ix_export_jobs_data_type', 'export_jobs', ['data_type'])


def downgrade():
    op.drop_table('export_jobs')
    op.drop_table('import_jobs')