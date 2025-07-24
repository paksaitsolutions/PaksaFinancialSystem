"""Add password policy tables

Revision ID: 20240101_add_password_policy_tables
Revises: 20240101_add_rbac_tables
Create Date: 2024-01-01 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '20240101_add_password_policy_tables'
down_revision = '20240101_add_rbac_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create password_policies table
    op.create_table(
        'password_policies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(100), nullable=False, default='Default Policy'),
        sa.Column('description', sa.Text, nullable=True),
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
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create password_history table
    op.create_table(
        'password_history',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create login_attempts table
    op.create_table(
        'login_attempts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('success', sa.Boolean, nullable=False),
        sa.Column('attempted_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Add password_changed_at column to users table
    op.add_column('users', sa.Column('password_changed_at', sa.DateTime, nullable=True))
    
    # Create indexes
    op.create_index('ix_password_history_user_created', 'password_history', ['user_id', 'created_at'])
    op.create_index('ix_login_attempts_user_attempted', 'login_attempts', ['user_id', 'attempted_at'])
    op.create_index('ix_login_attempts_success', 'login_attempts', ['success'])


def downgrade():
    op.drop_column('users', 'password_changed_at')
    op.drop_table('login_attempts')
    op.drop_table('password_history')
    op.drop_table('password_policies')