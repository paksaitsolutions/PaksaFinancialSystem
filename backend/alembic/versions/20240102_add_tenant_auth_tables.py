"""Add tenant auth tables

Revision ID: 20240102_add_tenant_auth_tables
Revises: 20240102_add_enhanced_reports_tables
Create Date: 2024-01-02 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


# revision identifiers, used by Alembic.
revision = '20240102_add_tenant_auth_tables'
down_revision = '20240102_add_enhanced_reports_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create tenant_auth_configs table
    op.create_table(
        'tenant_auth_configs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, unique=True, index=True),
        sa.Column('custom_login_url', sa.String(255), nullable=True),
        sa.Column('company_code_required', sa.Boolean, nullable=False, default=False),
        sa.Column('session_timeout_minutes', sa.Integer, nullable=False, default=30),
        sa.Column('remember_me_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('remember_me_duration_days', sa.Integer, nullable=False, default=30),
        sa.Column('concurrent_sessions_limit', sa.Integer, nullable=False, default=5),
        sa.Column('password_reset_enabled', sa.Boolean, nullable=False, default=True),
        sa.Column('password_reset_expiry_hours', sa.Integer, nullable=False, default=24),
        sa.Column('custom_reset_template', sa.Text, nullable=True),
        sa.Column('oauth_providers', JSON, nullable=True),
        sa.Column('saml_config', JSON, nullable=True),
        sa.Column('login_logo_url', sa.String(500), nullable=True),
        sa.Column('login_background_url', sa.String(500), nullable=True),
        sa.Column('brand_colors', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create tenant_sessions table
    op.create_table(
        'tenant_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('session_token', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('login_method', sa.String(50), nullable=False, default='email_password'),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('last_activity', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('remember_me', sa.Boolean, nullable=False, default=False),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('terminated_reason', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create company_login_attempts table
    op.create_table(
        'company_login_attempts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('email', sa.String(255), nullable=False, index=True),
        sa.Column('success', sa.Boolean, nullable=False),
        sa.Column('login_method', sa.String(50), nullable=False, default='email_password'),
        sa.Column('failure_reason', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('token', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('used', sa.Boolean, nullable=False, default=False),
        sa.Column('used_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create oauth_providers table
    op.create_table(
        'oauth_providers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('provider_name', sa.String(50), nullable=False),
        sa.Column('client_id', sa.String(255), nullable=False),
        sa.Column('client_secret', sa.String(500), nullable=False),
        sa.Column('redirect_uri', sa.String(500), nullable=False),
        sa.Column('scopes', JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('auto_create_users', sa.Boolean, nullable=False, default=False),
        sa.Column('default_role', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_tenant_sessions_user_company', 'tenant_sessions', ['user_id', 'company_id'])
    op.create_index('ix_tenant_sessions_expires', 'tenant_sessions', ['expires_at'])
    op.create_index('ix_tenant_sessions_status', 'tenant_sessions', ['status'])
    op.create_index('ix_login_attempts_company_email', 'company_login_attempts', ['company_id', 'email'])
    op.create_index('ix_login_attempts_created', 'company_login_attempts', ['created_at'])
    op.create_index('ix_password_reset_expires', 'password_reset_tokens', ['expires_at'])
    op.create_index('ix_oauth_providers_company_provider', 'oauth_providers', ['company_id', 'provider_name'])


def downgrade():
    op.drop_table('oauth_providers')
    op.drop_table('password_reset_tokens')
    op.drop_table('company_login_attempts')
    op.drop_table('tenant_sessions')
    op.drop_table('tenant_auth_configs')