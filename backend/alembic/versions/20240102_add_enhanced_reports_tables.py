"""Add enhanced reports tables

Revision ID: 20240102_add_enhanced_reports_tables
Revises: 20240101_add_company_tables
Create Date: 2024-01-02 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


# revision identifiers, used by Alembic.
revision = '20240102_add_enhanced_reports_tables'
down_revision = '20240101_add_company_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create company_reports table
    op.create_table(
        'company_reports',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('report_name', sa.String(200), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('period_start', sa.DateTime, nullable=False),
        sa.Column('period_end', sa.DateTime, nullable=False),
        sa.Column('filters', JSON, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('generated_at', sa.DateTime, nullable=True),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('file_format', sa.String(10), nullable=True),
        sa.Column('report_data', JSON, nullable=True),
        sa.Column('generated_by', UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create report_templates table
    op.create_table(
        'report_templates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('template_name', sa.String(200), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('template_config', JSON, nullable=False),
        sa.Column('is_default', sa.Boolean, nullable=False, default=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create report_schedules table
    op.create_table(
        'report_schedules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('schedule_name', sa.String(200), nullable=False),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('cron_expression', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('report_config', JSON, nullable=True),
        sa.Column('email_recipients', JSON, nullable=True),
        sa.Column('last_run', sa.DateTime, nullable=True),
        sa.Column('next_run', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_company_reports_type', 'company_reports', ['report_type'])
    op.create_index('ix_company_reports_status', 'company_reports', ['status'])
    op.create_index('ix_company_reports_period', 'company_reports', ['period_start', 'period_end'])
    op.create_index('ix_report_templates_type', 'report_templates', ['report_type'])
    op.create_index('ix_report_schedules_active', 'report_schedules', ['is_active'])


def downgrade():
    op.drop_table('report_schedules')
    op.drop_table('report_templates')
    op.drop_table('company_reports')