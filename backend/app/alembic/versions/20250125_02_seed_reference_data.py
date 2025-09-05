"""Seed reference data

Revision ID: 20250125_02
Revises: 20250125_01
Create Date: 2025-01-25 10:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
import uuid

# revision identifiers
revision = '20250125_02'
down_revision = '20250125_01'
branch_labels = None
depends_on = None


def upgrade():
    # Countries data
    countries_table = table('countries',
        column('id', sa.String),
        column('code', sa.String),
        column('name', sa.String),
        column('full_name', sa.String),
        column('iso3_code', sa.String),
        column('phone_code', sa.String),
        column('is_active', sa.Boolean)
    )
    
    op.bulk_insert(countries_table, [
        {'id': str(uuid.uuid4()), 'code': 'US', 'name': 'United States', 'full_name': 'United States of America', 'iso3_code': 'USA', 'phone_code': '+1', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'PK', 'name': 'Pakistan', 'full_name': 'Islamic Republic of Pakistan', 'iso3_code': 'PAK', 'phone_code': '+92', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'IN', 'name': 'India', 'full_name': 'Republic of India', 'iso3_code': 'IND', 'phone_code': '+91', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'GB', 'name': 'United Kingdom', 'full_name': 'United Kingdom of Great Britain and Northern Ireland', 'iso3_code': 'GBR', 'phone_code': '+44', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'CA', 'name': 'Canada', 'full_name': 'Canada', 'iso3_code': 'CAN', 'phone_code': '+1', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'AU', 'name': 'Australia', 'full_name': 'Commonwealth of Australia', 'iso3_code': 'AUS', 'phone_code': '+61', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'DE', 'name': 'Germany', 'full_name': 'Federal Republic of Germany', 'iso3_code': 'DEU', 'phone_code': '+49', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'FR', 'name': 'France', 'full_name': 'French Republic', 'iso3_code': 'FRA', 'phone_code': '+33', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'JP', 'name': 'Japan', 'full_name': 'Japan', 'iso3_code': 'JPN', 'phone_code': '+81', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'CN', 'name': 'China', 'full_name': 'People\'s Republic of China', 'iso3_code': 'CHN', 'phone_code': '+86', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'SA', 'name': 'Saudi Arabia', 'full_name': 'Kingdom of Saudi Arabia', 'iso3_code': 'SAU', 'phone_code': '+966', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'AE', 'name': 'United Arab Emirates', 'full_name': 'United Arab Emirates', 'iso3_code': 'ARE', 'phone_code': '+971', 'is_active': True}
    ])

    # Currencies data
    currencies_table = table('currencies',
        column('id', sa.String),
        column('code', sa.String),
        column('name', sa.String),
        column('symbol', sa.String),
        column('decimal_places', sa.Integer),
        column('is_active', sa.Boolean)
    )
    
    op.bulk_insert(currencies_table, [
        {'id': str(uuid.uuid4()), 'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'decimal_places': 2, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'PKR', 'name': 'Pakistani Rupee', 'symbol': '₨', 'decimal_places': 2, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'decimal_places': 2, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'decimal_places': 2, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'CAD', 'name': 'Canadian Dollar', 'symbol': 'C$', 'decimal_places': 2, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'AUD', 'name': 'Australian Dollar', 'symbol': 'A$', 'decimal_places': 2, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥', 'decimal_places': 0, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'CNY', 'name': 'Chinese Yuan', 'symbol': '¥', 'decimal_places': 2, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹', 'decimal_places': 2, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'SAR', 'name': 'Saudi Riyal', 'symbol': 'ر.س', 'decimal_places': 2, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'AED', 'name': 'UAE Dirham', 'symbol': 'د.إ', 'decimal_places': 2, 'is_active': True}
    ])

    # Languages data
    languages_table = table('languages',
        column('id', sa.String),
        column('code', sa.String),
        column('name', sa.String),
        column('native_name', sa.String),
        column('is_rtl', sa.Boolean),
        column('is_active', sa.Boolean)
    )
    
    op.bulk_insert(languages_table, [
        {'id': str(uuid.uuid4()), 'code': 'en-US', 'name': 'English (US)', 'native_name': 'English', 'is_rtl': False, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'ur-PK', 'name': 'Urdu (Pakistan)', 'native_name': 'اردو', 'is_rtl': True, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'ar-SA', 'name': 'Arabic (Saudi Arabia)', 'native_name': 'العربية', 'is_rtl': True, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'hi-IN', 'name': 'Hindi (India)', 'native_name': 'हिन्दी', 'is_rtl': False, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'es-ES', 'name': 'Spanish', 'native_name': 'Español', 'is_rtl': False, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'fr-FR', 'name': 'French', 'native_name': 'Français', 'is_rtl': False, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'de-DE', 'name': 'German', 'native_name': 'Deutsch', 'is_rtl': False, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'zh-CN', 'name': 'Chinese (Simplified)', 'native_name': '中文', 'is_rtl': False, 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'ja-JP', 'name': 'Japanese', 'native_name': '日本語', 'is_rtl': False, 'is_active': True}
    ])

    # Timezones data
    timezones_table = table('timezones',
        column('id', sa.String),
        column('code', sa.String),
        column('name', sa.String),
        column('utc_offset', sa.String),
        column('is_active', sa.Boolean)
    )
    
    op.bulk_insert(timezones_table, [
        {'id': str(uuid.uuid4()), 'code': 'UTC', 'name': 'UTC', 'utc_offset': '+00:00', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'Asia/Karachi', 'name': 'Pakistan Standard Time', 'utc_offset': '+05:00', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'Asia/Dubai', 'name': 'Gulf Standard Time', 'utc_offset': '+04:00', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'America/New_York', 'name': 'Eastern Time (US)', 'utc_offset': '-05:00', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'America/Chicago', 'name': 'Central Time (US)', 'utc_offset': '-06:00', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'America/Los_Angeles', 'name': 'Pacific Time (US)', 'utc_offset': '-08:00', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'Europe/London', 'name': 'Greenwich Mean Time', 'utc_offset': '+00:00', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'Europe/Paris', 'name': 'Central European Time', 'utc_offset': '+01:00', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'Asia/Tokyo', 'name': 'Japan Standard Time', 'utc_offset': '+09:00', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'Asia/Shanghai', 'name': 'China Standard Time', 'utc_offset': '+08:00', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'Australia/Sydney', 'name': 'Australian Eastern Time', 'utc_offset': '+10:00', 'is_active': True}
    ])

    # Account types data
    account_types_table = table('account_types',
        column('id', sa.String),
        column('code', sa.String),
        column('name', sa.String),
        column('category', sa.String),
        column('normal_balance', sa.String),
        column('is_active', sa.Boolean)
    )
    
    op.bulk_insert(account_types_table, [
        {'id': str(uuid.uuid4()), 'code': 'ASSET', 'name': 'Asset', 'category': 'BALANCE_SHEET', 'normal_balance': 'DEBIT', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'LIABILITY', 'name': 'Liability', 'category': 'BALANCE_SHEET', 'normal_balance': 'CREDIT', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'EQUITY', 'name': 'Equity', 'category': 'BALANCE_SHEET', 'normal_balance': 'CREDIT', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'REVENUE', 'name': 'Revenue', 'category': 'INCOME_STATEMENT', 'normal_balance': 'CREDIT', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'EXPENSE', 'name': 'Expense', 'category': 'INCOME_STATEMENT', 'normal_balance': 'DEBIT', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'COGS', 'name': 'Cost of Goods Sold', 'category': 'INCOME_STATEMENT', 'normal_balance': 'DEBIT', 'is_active': True}
    ])

    # Payment methods data
    payment_methods_table = table('payment_methods',
        column('id', sa.String),
        column('code', sa.String),
        column('name', sa.String),
        column('description', sa.String),
        column('is_active', sa.Boolean)
    )
    
    op.bulk_insert(payment_methods_table, [
        {'id': str(uuid.uuid4()), 'code': 'CASH', 'name': 'Cash', 'description': 'Cash payment', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'CHECK', 'name': 'Check', 'description': 'Check payment', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'BANK_TRANSFER', 'name': 'Bank Transfer', 'description': 'Electronic bank transfer', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'CREDIT_CARD', 'name': 'Credit Card', 'description': 'Credit card payment', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'DEBIT_CARD', 'name': 'Debit Card', 'description': 'Debit card payment', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'ONLINE_PAYMENT', 'name': 'Online Payment', 'description': 'Online payment gateway', 'is_active': True}
    ])

    # Tax types data
    tax_types_table = table('tax_types',
        column('id', sa.String),
        column('code', sa.String),
        column('name', sa.String),
        column('description', sa.String),
        column('is_active', sa.Boolean)
    )
    
    op.bulk_insert(tax_types_table, [
        {'id': str(uuid.uuid4()), 'code': 'SALES_TAX', 'name': 'Sales Tax', 'description': 'Sales tax on goods and services', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'VAT', 'name': 'Value Added Tax', 'description': 'Value added tax', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'GST', 'name': 'Goods and Services Tax', 'description': 'Goods and services tax', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'INCOME_TAX', 'name': 'Income Tax', 'description': 'Income tax', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'WITHHOLDING_TAX', 'name': 'Withholding Tax', 'description': 'Withholding tax', 'is_active': True}
    ])

    # Bank account types data
    bank_account_types_table = table('bank_account_types',
        column('id', sa.String),
        column('code', sa.String),
        column('name', sa.String),
        column('description', sa.String),
        column('is_active', sa.Boolean)
    )
    
    op.bulk_insert(bank_account_types_table, [
        {'id': str(uuid.uuid4()), 'code': 'CHECKING', 'name': 'Checking Account', 'description': 'Standard checking account', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'SAVINGS', 'name': 'Savings Account', 'description': 'Savings account', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'MONEY_MARKET', 'name': 'Money Market Account', 'description': 'Money market account', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'CREDIT_LINE', 'name': 'Line of Credit', 'description': 'Line of credit account', 'is_active': True},
        {'id': str(uuid.uuid4()), 'code': 'PETTY_CASH', 'name': 'Petty Cash', 'description': 'Petty cash account', 'is_active': True}
    ])


def downgrade():
    op.execute("DELETE FROM bank_account_types")
    op.execute("DELETE FROM tax_types")
    op.execute("DELETE FROM payment_methods")
    op.execute("DELETE FROM account_types")
    op.execute("DELETE FROM timezones")
    op.execute("DELETE FROM languages")
    op.execute("DELETE FROM currencies")
    op.execute("DELETE FROM countries")