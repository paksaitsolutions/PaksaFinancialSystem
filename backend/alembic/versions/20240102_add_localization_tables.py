"""Add localization tables

Revision ID: 20240102_add_localization_tables
Revises: 20240102_add_user_admin_tables
Create Date: 2024-01-02 07:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid


# revision identifiers, used by Alembic.
revision = '20240102_add_localization_tables'
down_revision = '20240102_add_user_admin_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create languages table
    op.create_table(
        'languages',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('code', sa.String(10), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('native_name', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create translations table
    op.create_table(
        'translations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('key', sa.String(200), nullable=False),
        sa.Column('language_code', sa.String(10), nullable=False),
        sa.Column('value', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create regional_settings table
    op.create_table(
        'regional_settings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('region_code', sa.String(10), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('currency_code', sa.String(3), nullable=False),
        sa.Column('timezone', sa.String(50), nullable=False),
        sa.Column('date_format', sa.String(20), nullable=False, default='YYYY-MM-DD'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True)
    )
    
    # Create indexes
    op.create_index('ix_languages_code', 'languages', ['code'])
    op.create_index('ix_translations_key_lang', 'translations', ['key', 'language_code'])
    op.create_index('ix_regional_settings_code', 'regional_settings', ['region_code'])
    
    # Insert default data
    op.execute("""
        INSERT INTO languages (id, code, name, native_name, is_active) VALUES
        (gen_random_uuid(), 'en', 'English', 'English', true),
        (gen_random_uuid(), 'es', 'Spanish', 'Español', true),
        (gen_random_uuid(), 'fr', 'French', 'Français', true)
    """)
    
    op.execute("""
        INSERT INTO regional_settings (id, region_code, name, currency_code, timezone, date_format) VALUES
        (gen_random_uuid(), 'US', 'United States', 'USD', 'America/New_York', 'MM/DD/YYYY'),
        (gen_random_uuid(), 'GB', 'United Kingdom', 'GBP', 'Europe/London', 'DD/MM/YYYY'),
        (gen_random_uuid(), 'EU', 'European Union', 'EUR', 'Europe/Paris', 'DD/MM/YYYY')
    """)


def downgrade():
    op.drop_table('regional_settings')
    op.drop_table('translations')
    op.drop_table('languages')