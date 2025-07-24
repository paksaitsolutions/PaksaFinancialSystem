"""Add company tables

Revision ID: 20240101_add_company_tables
Revises: 20240101_add_backup_tables
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


# revision identifiers, used by Alembic.
revision = '20240101_add_company_tables'
down_revision = '20240101_add_backup_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_name', sa.String(200), nullable=False),
        sa.Column('company_code', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('business_type', sa.String(50), nullable=True),
        sa.Column('tax_id', sa.String(50), nullable=True),
        sa.Column('registration_number', sa.String(100), nullable=True),
        sa.Column('address_line1', sa.String(200), nullable=True),
        sa.Column('address_line2', sa.String(200), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('primary_color', sa.String(7), nullable=True),
        sa.Column('secondary_color', sa.String(7), nullable=True),
        sa.Column('default_currency', sa.String(3), nullable=False, default='USD'),
        sa.Column('default_language', sa.String(5), nullable=False, default='en-US'),
        sa.Column('timezone', sa.String(50), nullable=False, default='UTC'),
        sa.Column('date_format', sa.String(20), nullable=False, default='MM/DD/YYYY'),
        sa.Column('fiscal_year_start', sa.String(5), nullable=False, default='01-01'),
        sa.Column('tax_settings', JSON, nullable=True),
        sa.Column('enabled_modules', JSON, nullable=True),
        sa.Column('numbering_formats', JSON, nullable=True),
        sa.Column('subscription_tier', sa.String(20), nullable=False, default='basic'),
        sa.Column('status', sa.String(20), nullable=False, default='trial'),
        sa.Column('trial_ends_at', sa.DateTime, nullable=True),
        sa.Column('database_schema', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create company_users table
    op.create_table(
        'company_users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('role', sa.String(50), nullable=False, default='user'),
        sa.Column('is_admin', sa.Boolean, nullable=False, default=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('permissions', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create company_settings table
    op.create_table(
        'company_settings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('chart_of_accounts_template', sa.String(50), nullable=True),
        sa.Column('approval_workflows', JSON, nullable=True),
        sa.Column('integrations', JSON, nullable=True),
        sa.Column('custom_fields', JSON, nullable=True),
        sa.Column('notification_settings', JSON, nullable=True),
        sa.Column('security_settings', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_companies_status', 'companies', ['status'])
    op.create_index('ix_companies_subscription', 'companies', ['subscription_tier'])
    op.create_index('ix_company_users_company_user', 'company_users', ['company_id', 'user_id'])
    op.create_index('ix_company_users_role', 'company_users', ['role'])


def downgrade():
    op.drop_table('company_settings')
    op.drop_table('company_users')
    op.drop_table('companies')