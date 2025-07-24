"""Add compliance tables

Revision ID: 20240101_add_compliance_tables
Revises: 20240101_add_encryption_tables
Create Date: 2024-01-01 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


# revision identifiers, used by Alembic.
revision = '20240101_add_compliance_tables'
down_revision = '20240101_add_encryption_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create compliance_reports table
    op.create_table(
        'compliance_reports',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('report_name', sa.String(200), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('report_number', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('start_date', sa.DateTime, nullable=False),
        sa.Column('end_date', sa.DateTime, nullable=False),
        sa.Column('filters', JSON, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('generated_at', sa.DateTime, nullable=True),
        sa.Column('report_data', JSON, nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_size', sa.String(20), nullable=True),
        sa.Column('requested_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create compliance_policies table
    op.create_table(
        'compliance_policies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('policy_name', sa.String(200), nullable=False),
        sa.Column('policy_code', sa.String(50), nullable=False, unique=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('requirements', JSON, nullable=True),
        sa.Column('compliance_framework', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('effective_date', sa.DateTime, nullable=False),
        sa.Column('review_date', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_compliance_reports_type_status', 'compliance_reports', ['report_type', 'status'])
    op.create_index('ix_compliance_reports_dates', 'compliance_reports', ['start_date', 'end_date'])
    op.create_index('ix_compliance_policies_framework', 'compliance_policies', ['compliance_framework'])


def downgrade():
    op.drop_table('compliance_policies')
    op.drop_table('compliance_reports')