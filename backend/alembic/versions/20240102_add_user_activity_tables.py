"""Add user activity tables

Revision ID: 20240102_add_user_activity_tables
Revises: 20240102_add_tenant_auth_tables
Create Date: 2024-01-02 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


# revision identifiers, used by Alembic.
revision = '20240102_add_user_activity_tables'
down_revision = '20240102_add_tenant_auth_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create login_history table
    op.create_table(
        'login_history',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('login_time', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('logout_time', sa.DateTime, nullable=True),
        sa.Column('session_duration', sa.Integer, nullable=True),
        sa.Column('login_method', sa.String(50), nullable=False, default='email_password'),
        sa.Column('success', sa.Boolean, nullable=False, default=True),
        sa.Column('failure_reason', sa.String(200), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('device_type', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create user_activities table
    op.create_table(
        'user_activities',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('activity_type', sa.String(50), nullable=False),
        sa.Column('action', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('resource_type', sa.String(100), nullable=True),
        sa.Column('resource_id', UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('request_method', sa.String(10), nullable=True),
        sa.Column('request_path', sa.String(500), nullable=True),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create company_password_policies table
    op.create_table(
        'company_password_policies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, unique=True, index=True),
        sa.Column('min_length', sa.Integer, nullable=False, default=8),
        sa.Column('max_length', sa.Integer, nullable=False, default=128),
        sa.Column('require_uppercase', sa.Boolean, nullable=False, default=True),
        sa.Column('require_lowercase', sa.Boolean, nullable=False, default=True),
        sa.Column('require_numbers', sa.Boolean, nullable=False, default=True),
        sa.Column('require_special_chars', sa.Boolean, nullable=False, default=True),
        sa.Column('password_history_count', sa.Integer, nullable=False, default=5),
        sa.Column('password_expiry_days', sa.Integer, nullable=False, default=90),
        sa.Column('max_failed_attempts', sa.Integer, nullable=False, default=5),
        sa.Column('lockout_duration_minutes', sa.Integer, nullable=False, default=30),
        sa.Column('reset_token_expiry_hours', sa.Integer, nullable=False, default=24),
        sa.Column('require_security_questions', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create cross_company_access table
    op.create_table(
        'cross_company_access',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('source_company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('target_company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('access_type', sa.String(50), nullable=False, default='read_only'),
        sa.Column('permissions', JSON, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('expires_at', sa.DateTime, nullable=True),
        sa.Column('approved_by', UUID(as_uuid=True), nullable=False),
        sa.Column('approval_reason', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create user_session_activities table
    op.create_table(
        'user_session_activities',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('session_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('activity_time', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('page_url', sa.String(500), nullable=True),
        sa.Column('action_taken', sa.String(200), nullable=True),
        sa.Column('response_time_ms', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_login_history_user_company', 'login_history', ['user_id', 'company_id'])
    op.create_index('ix_login_history_time', 'login_history', ['login_time'])
    op.create_index('ix_user_activities_user_company', 'user_activities', ['user_id', 'company_id'])
    op.create_index('ix_user_activities_type', 'user_activities', ['activity_type'])
    op.create_index('ix_cross_company_access_user_target', 'cross_company_access', ['user_id', 'target_company_id'])


def downgrade():
    op.drop_table('user_session_activities')
    op.drop_table('cross_company_access')
    op.drop_table('company_password_policies')
    op.drop_table('user_activities')
    op.drop_table('login_history')