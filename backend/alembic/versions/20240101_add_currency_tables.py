"""Add currency tables

Revision ID: 20240101_add_currency_tables
Revises: 20240101_add_database_indexes
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = '20240101_add_currency_tables'
down_revision = '20240101_add_database_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # Create currencies table
    op.create_table(
        'currencies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('code', sa.String(3), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('symbol', sa.String(10), nullable=True),
        sa.Column('decimal_places', sa.Integer, nullable=False, default=2),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('is_base_currency', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint("LENGTH(code) = 3", name="ck_currency_code_length"),
        sa.CheckConstraint("decimal_places >= 0", name="ck_currency_decimal_places_positive")
    )
    
    # Create exchange_rates table
    op.create_table(
        'exchange_rates',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('source_currency_id', UUID(as_uuid=True), sa.ForeignKey('currencies.id'), nullable=False),
        sa.Column('target_currency_id', UUID(as_uuid=True), sa.ForeignKey('currencies.id'), nullable=False),
        sa.Column('rate', sa.Numeric(20, 10), nullable=False),
        sa.Column('effective_date', sa.Date, nullable=False, index=True),
        sa.Column('rate_type', sa.String(20), nullable=False, default='spot'),
        sa.Column('is_official', sa.Boolean, nullable=False, default=False),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', UUID(as_uuid=True), nullable=True),
        sa.UniqueConstraint('source_currency_id', 'target_currency_id', 'effective_date', 'rate_type', name='uq_exchange_rates_unique_rate'),
        sa.CheckConstraint("rate > 0", name="ck_exchange_rate_positive"),
        sa.CheckConstraint("source_currency_id != target_currency_id", name="ck_exchange_rate_different_currencies")
    )
    
    # Create indexes
    op.create_index('ix_exchange_rates_source_target', 'exchange_rates', ['source_currency_id', 'target_currency_id'])
    op.create_index('ix_exchange_rates_effective_date_rate_type', 'exchange_rates', ['effective_date', 'rate_type'])
    
    # Insert default currencies
    op.execute("""
    INSERT INTO currencies (id, code, name, symbol, decimal_places, status, is_base_currency)
    VALUES 
        (uuid_generate_v4(), 'USD', 'US Dollar', '$', 2, 'active', true),
        (uuid_generate_v4(), 'EUR', 'Euro', '€', 2, 'active', false),
        (uuid_generate_v4(), 'GBP', 'British Pound', '£', 2, 'active', false),
        (uuid_generate_v4(), 'PKR', 'Pakistani Rupee', '₨', 0, 'active', false),
        (uuid_generate_v4(), 'SAR', 'Saudi Riyal', '﷼', 2, 'active', false),
        (uuid_generate_v4(), 'AED', 'UAE Dirham', 'د.إ', 2, 'active', false)
    """)


def downgrade():
    op.drop_table('exchange_rates')
    op.drop_table('currencies')