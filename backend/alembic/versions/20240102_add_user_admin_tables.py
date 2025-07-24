"""Add user admin tables

Revision ID: 20240102_add_user_admin_tables
Revises: 20240102_add_migration_tables
Create Date: 2024-01-02 06:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


# revision identifiers, used by Alembic.
revision = '20240102_add_user_admin_tables'
down_revision = '20240102_add_migration_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_provisions table
    op.create_table(
        'user_provisions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('company_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('provisioned_by', UUID(as_uuid=True), nullable=False),
        sa.Column('provision_type', sa.String(50), nullable=False, default='manual'),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('metadata', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create system_settings table
    op.create_table(
        'system_settings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('key', sa.String(100), nullable=False, unique=True),
        sa.Column('value', sa.String(1000), nullable=True),
        sa.Column('data_type', sa.String(20), nullable=False, default='string'),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('is_public', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_user_provisions_user_company', 'user_provisions', ['user_id', 'company_id'])
    op.create_index('ix_user_provisions_status', 'user_provisions', ['status'])
    op.create_index('ix_system_settings_key', 'system_settings', ['key'])


def downgrade():
    op.drop_table('system_settings')
    op.drop_table('user_provisions')