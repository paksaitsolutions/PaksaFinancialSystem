"""Add encryption tables

Revision ID: 20240101_add_encryption_tables
Revises: 20240101_add_audit_tables
Create Date: 2024-01-01 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '20240101_add_encryption_tables'
down_revision = '20240101_add_audit_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create encrypted_user_profiles table
    op.create_table(
        'encrypted_user_profiles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', sa.String(36), nullable=False, unique=True, index=True),
        sa.Column('ssn', sa.String(200), nullable=True),  # Encrypted fields are longer
        sa.Column('phone_number', sa.String(200), nullable=True),
        sa.Column('address_line1', sa.String(400), nullable=True),
        sa.Column('address_line2', sa.String(400), nullable=True),
        sa.Column('city', sa.String(200), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('zip_code', sa.String(200), nullable=True),
        sa.Column('bank_account_number', sa.String(200), nullable=True),
        sa.Column('routing_number', sa.String(200), nullable=True),
        sa.Column('tax_id', sa.String(200), nullable=True),
        sa.Column('emergency_contact_name', sa.String(200), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_encrypted_user_profiles_user_id', 'encrypted_user_profiles', ['user_id'])


def downgrade():
    op.drop_table('encrypted_user_profiles')