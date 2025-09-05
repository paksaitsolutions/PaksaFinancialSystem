"""Create reference data tables

Revision ID: 20250125_01
Revises: 
Create Date: 2025-01-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '20250125_01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Countries table
    op.create_table('countries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=2), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=True),
        sa.Column('iso3_code', sa.String(length=3), nullable=True),
        sa.Column('numeric_code', sa.String(length=3), nullable=True),
        sa.Column('phone_code', sa.String(length=10), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_countries_code'), 'countries', ['code'], unique=False)

    # Currencies table
    op.create_table('currencies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=3), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=True),
        sa.Column('decimal_places', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_currencies_code'), 'currencies', ['code'], unique=False)

    # Languages table
    op.create_table('languages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('native_name', sa.String(length=100), nullable=True),
        sa.Column('is_rtl', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_languages_code'), 'languages', ['code'], unique=False)

    # Timezones table
    op.create_table('timezones',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('utc_offset', sa.String(length=10), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_timezones_code'), 'timezones', ['code'], unique=False)

    # Account types table
    op.create_table('account_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('normal_balance', sa.String(length=10), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_account_types_code'), 'account_types', ['code'], unique=False)

    # Payment methods table
    op.create_table('payment_methods',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_payment_methods_code'), 'payment_methods', ['code'], unique=False)

    # Tax types table
    op.create_table('tax_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_tax_types_code'), 'tax_types', ['code'], unique=False)

    # Bank account types table
    op.create_table('bank_account_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_bank_account_types_code'), 'bank_account_types', ['code'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_bank_account_types_code'), table_name='bank_account_types')
    op.drop_table('bank_account_types')
    op.drop_index(op.f('ix_tax_types_code'), table_name='tax_types')
    op.drop_table('tax_types')
    op.drop_index(op.f('ix_payment_methods_code'), table_name='payment_methods')
    op.drop_table('payment_methods')
    op.drop_index(op.f('ix_account_types_code'), table_name='account_types')
    op.drop_table('account_types')
    op.drop_index(op.f('ix_timezones_code'), table_name='timezones')
    op.drop_table('timezones')
    op.drop_index(op.f('ix_languages_code'), table_name='languages')
    op.drop_table('languages')
    op.drop_index(op.f('ix_currencies_code'), table_name='currencies')
    op.drop_table('currencies')
    op.drop_index(op.f('ix_countries_code'), table_name='countries')
    op.drop_table('countries')