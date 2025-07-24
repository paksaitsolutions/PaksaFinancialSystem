"""Add session tables

Revision ID: 20240101_add_session_tables
Revises: 20240101_add_password_policy_tables
Create Date: 2024-01-01 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '20240101_add_session_tables'
down_revision = '20240101_add_password_policy_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('session_token', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('device_info', sa.Text, nullable=True),
        sa.Column('last_activity', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('terminated_at', sa.DateTime, nullable=True),
        sa.Column('termination_reason', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create session_configs table
    op.create_table(
        'session_configs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(100), nullable=False, default='Default Session Config'),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('session_timeout_minutes', sa.Integer, nullable=False, default=30),
        sa.Column('max_concurrent_sessions', sa.Integer, nullable=False, default=3),
        sa.Column('remember_me_duration_days', sa.Integer, nullable=False, default=30),
        sa.Column('require_fresh_login_minutes', sa.Integer, nullable=False, default=60),
        sa.Column('auto_logout_on_idle', sa.Boolean, nullable=False, default=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_user_sessions_user_status', 'user_sessions', ['user_id', 'status'])
    op.create_index('ix_user_sessions_expires_status', 'user_sessions', ['expires_at', 'status'])
    op.create_index('ix_user_sessions_last_activity', 'user_sessions', ['last_activity'])


def downgrade():
    op.drop_table('session_configs')
    op.drop_table('user_sessions')