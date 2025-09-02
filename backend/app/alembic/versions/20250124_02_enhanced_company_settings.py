"""Enhanced company settings

Revision ID: 20250124_02_enhanced_company_settings
Revises: 20250724_01_create_company_settings
Create Date: 2025-01-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250124_02_enhanced_company_settings'
down_revision = '20250724_01_create_company_settings'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to company_settings table
    op.add_column('company_settings', sa.Column('company_name', sa.String(length=255), nullable=False, server_default='Paksa Financial System'))
    op.add_column('company_settings', sa.Column('company_code', sa.String(length=50), nullable=True))
    op.add_column('company_settings', sa.Column('tax_id', sa.String(length=100), nullable=True))
    op.add_column('company_settings', sa.Column('registration_number', sa.String(length=100), nullable=True))
    op.add_column('company_settings', sa.Column('company_address', sa.Text(), nullable=True))
    
    # Financial Settings
    op.add_column('company_settings', sa.Column('base_currency', sa.String(length=3), nullable=False, server_default='USD'))
    op.add_column('company_settings', sa.Column('fiscal_year_start', sa.String(length=20), nullable=False, server_default='January'))
    op.add_column('company_settings', sa.Column('decimal_places', sa.Integer(), nullable=False, server_default='2'))
    op.add_column('company_settings', sa.Column('rounding_method', sa.String(length=20), nullable=False, server_default='round'))
    op.add_column('company_settings', sa.Column('multi_currency_enabled', sa.Boolean(), nullable=False, server_default='false'))
    
    # Regional Settings
    op.add_column('company_settings', sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC'))
    op.add_column('company_settings', sa.Column('date_format', sa.String(length=20), nullable=False, server_default='MM/DD/YYYY'))
    op.add_column('company_settings', sa.Column('time_format', sa.String(length=2), nullable=False, server_default='12'))
    op.add_column('company_settings', sa.Column('number_format', sa.String(length=10), nullable=False, server_default='US'))
    op.add_column('company_settings', sa.Column('week_start', sa.String(length=10), nullable=False, server_default='Sunday'))
    
    # Document Settings
    op.add_column('company_settings', sa.Column('invoice_prefix', sa.String(length=20), nullable=True, server_default='INV-'))
    op.add_column('company_settings', sa.Column('invoice_start_number', sa.Integer(), nullable=False, server_default='1000'))
    op.add_column('company_settings', sa.Column('bill_prefix', sa.String(length=20), nullable=True, server_default='BILL-'))
    op.add_column('company_settings', sa.Column('payment_prefix', sa.String(length=20), nullable=True, server_default='PAY-'))
    op.add_column('company_settings', sa.Column('auto_numbering_enabled', sa.Boolean(), nullable=False, server_default='true'))
    
    # System Preferences
    op.add_column('company_settings', sa.Column('session_timeout', sa.Integer(), nullable=False, server_default='60'))
    op.add_column('company_settings', sa.Column('default_page_size', sa.Integer(), nullable=False, server_default='25'))
    op.add_column('company_settings', sa.Column('default_theme', sa.String(length=20), nullable=False, server_default='light'))
    op.add_column('company_settings', sa.Column('backup_frequency', sa.String(length=20), nullable=False, server_default='daily'))
    op.add_column('company_settings', sa.Column('audit_trail_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('company_settings', sa.Column('email_notifications_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('company_settings', sa.Column('two_factor_auth_required', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('company_settings', sa.Column('auto_save_enabled', sa.Boolean(), nullable=False, server_default='true'))
    
    # Integration Settings
    op.add_column('company_settings', sa.Column('api_rate_limit', sa.Integer(), nullable=False, server_default='1000'))
    op.add_column('company_settings', sa.Column('webhook_timeout', sa.Integer(), nullable=False, server_default='30'))
    op.add_column('company_settings', sa.Column('api_logging_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('company_settings', sa.Column('webhook_retry_enabled', sa.Boolean(), nullable=False, server_default='true'))
    
    # Remove server defaults after adding columns
    op.alter_column('company_settings', 'company_name', server_default=None)
    op.alter_column('company_settings', 'base_currency', server_default=None)
    op.alter_column('company_settings', 'fiscal_year_start', server_default=None)
    op.alter_column('company_settings', 'decimal_places', server_default=None)
    op.alter_column('company_settings', 'rounding_method', server_default=None)
    op.alter_column('company_settings', 'multi_currency_enabled', server_default=None)
    op.alter_column('company_settings', 'timezone', server_default=None)
    op.alter_column('company_settings', 'date_format', server_default=None)
    op.alter_column('company_settings', 'time_format', server_default=None)
    op.alter_column('company_settings', 'number_format', server_default=None)
    op.alter_column('company_settings', 'week_start', server_default=None)
    op.alter_column('company_settings', 'invoice_start_number', server_default=None)
    op.alter_column('company_settings', 'auto_numbering_enabled', server_default=None)
    op.alter_column('company_settings', 'session_timeout', server_default=None)
    op.alter_column('company_settings', 'default_page_size', server_default=None)
    op.alter_column('company_settings', 'default_theme', server_default=None)
    op.alter_column('company_settings', 'backup_frequency', server_default=None)
    op.alter_column('company_settings', 'audit_trail_enabled', server_default=None)
    op.alter_column('company_settings', 'email_notifications_enabled', server_default=None)
    op.alter_column('company_settings', 'two_factor_auth_required', server_default=None)
    op.alter_column('company_settings', 'auto_save_enabled', server_default=None)
    op.alter_column('company_settings', 'api_rate_limit', server_default=None)
    op.alter_column('company_settings', 'webhook_timeout', server_default=None)
    op.alter_column('company_settings', 'api_logging_enabled', server_default=None)
    op.alter_column('company_settings', 'webhook_retry_enabled', server_default=None)


def downgrade():
    # Remove added columns
    op.drop_column('company_settings', 'webhook_retry_enabled')
    op.drop_column('company_settings', 'api_logging_enabled')
    op.drop_column('company_settings', 'webhook_timeout')
    op.drop_column('company_settings', 'api_rate_limit')
    op.drop_column('company_settings', 'auto_save_enabled')
    op.drop_column('company_settings', 'two_factor_auth_required')
    op.drop_column('company_settings', 'email_notifications_enabled')
    op.drop_column('company_settings', 'audit_trail_enabled')
    op.drop_column('company_settings', 'backup_frequency')
    op.drop_column('company_settings', 'default_theme')
    op.drop_column('company_settings', 'default_page_size')
    op.drop_column('company_settings', 'session_timeout')
    op.drop_column('company_settings', 'auto_numbering_enabled')
    op.drop_column('company_settings', 'payment_prefix')
    op.drop_column('company_settings', 'bill_prefix')
    op.drop_column('company_settings', 'invoice_start_number')
    op.drop_column('company_settings', 'invoice_prefix')
    op.drop_column('company_settings', 'week_start')
    op.drop_column('company_settings', 'number_format')
    op.drop_column('company_settings', 'time_format')
    op.drop_column('company_settings', 'date_format')
    op.drop_column('company_settings', 'timezone')
    op.drop_column('company_settings', 'multi_currency_enabled')
    op.drop_column('company_settings', 'rounding_method')
    op.drop_column('company_settings', 'decimal_places')
    op.drop_column('company_settings', 'fiscal_year_start')
    op.drop_column('company_settings', 'base_currency')
    op.drop_column('company_settings', 'company_address')
    op.drop_column('company_settings', 'registration_number')
    op.drop_column('company_settings', 'tax_id')
    op.drop_column('company_settings', 'company_code')
    op.drop_column('company_settings', 'company_name')