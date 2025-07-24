"""Create fixed assets tables

Revision ID: 20240118_create_fixed_assets_tables
Revises: 20240117_create_budget_tables
Create Date: 2024-01-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '20240118_create_fixed_assets_tables'
down_revision = '20240117_create_budget_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Create asset_categories table
    op.create_table('asset_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('default_useful_life', sa.Integer(), nullable=True),
        sa.Column('default_depreciation_method', sa.Enum('STRAIGHT_LINE', 'DECLINING_BALANCE', 'UNITS_OF_PRODUCTION', name='depreciationmethod'), nullable=True),
        sa.Column('default_salvage_rate', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create fixed_assets table
    op.create_table('fixed_assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset_number', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=False),
        sa.Column('purchase_cost', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('salvage_value', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('useful_life_years', sa.Integer(), nullable=False),
        sa.Column('depreciation_method', sa.Enum('STRAIGHT_LINE', 'DECLINING_BALANCE', 'UNITS_OF_PRODUCTION', name='depreciationmethod'), nullable=True),
        sa.Column('accumulated_depreciation', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'DISPOSED', 'UNDER_MAINTENANCE', 'RETIRED', name='assetstatus'), nullable=True),
        sa.Column('disposal_date', sa.Date(), nullable=True),
        sa.Column('disposal_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('disposal_reason', sa.Text(), nullable=True),
        sa.Column('vendor_name', sa.String(length=255), nullable=True),
        sa.Column('warranty_expiry', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_number')
    )
    
    # Create depreciation_entries table
    op.create_table('depreciation_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('period_date', sa.Date(), nullable=False),
        sa.Column('depreciation_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('accumulated_depreciation', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('book_value', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['fixed_assets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create maintenance_records table
    op.create_table('maintenance_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('maintenance_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('completed_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='maintenancestatus'), nullable=True),
        sa.Column('estimated_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('actual_cost', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('vendor_name', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('next_maintenance_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['asset_id'], ['fixed_assets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('maintenance_records')
    op.drop_table('depreciation_entries')
    op.drop_table('fixed_assets')
    op.drop_table('asset_categories')
    op.execute('DROP TYPE maintenancestatus')
    op.execute('DROP TYPE assetstatus')
    op.execute('DROP TYPE depreciationmethod')