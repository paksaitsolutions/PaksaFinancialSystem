"""Add tenant_id columns to all tables

Revision ID: 20240119_add_tenant_id_columns
Revises: 20240118_create_fixed_assets_tables
Create Date: 2024-01-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '20240119_add_tenant_id_columns'
down_revision = '20240118_create_fixed_assets_tables'
branch_labels = None
depends_on = None

def upgrade():
    # List of tables that need tenant_id column
    tables = [
        'companies',
        'fixed_assets',
        'depreciation_entries', 
        'maintenance_records',
        'asset_categories',
        'budgets',
        'budget_line_items',
        'tax_jurisdictions',
        'tax_rates',
        'tax_transactions',
        'tax_transaction_components',
        'tax_exemptions',
        'tax_returns',
        'accounts',
        'journal_entries',
        'journal_entry_lines',
        'fiscal_periods'
    ]
    
    for table in tables:
        # Add tenant_id column
        op.add_column(table, sa.Column('tenant_id', sa.String(50), nullable=False, server_default='default'))
        
        # Create index on tenant_id
        op.create_index(f'idx_{table}_tenant_id', table, ['tenant_id'])
    
    # Enable Row Level Security on sensitive tables
    sensitive_tables = [
        'fixed_assets', 'depreciation_entries', 'maintenance_records',
        'budgets', 'budget_line_items', 'tax_transactions', 'accounts',
        'journal_entries', 'journal_entry_lines'
    ]
    
    for table in sensitive_tables:
        # Enable RLS
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        
        # Create tenant isolation policy
        op.execute(f"""
            CREATE POLICY tenant_isolation ON {table}
            FOR ALL
            TO PUBLIC
            USING (tenant_id = current_setting('app.current_tenant', true))
        """)

def downgrade():
    tables = [
        'companies',
        'fixed_assets',
        'depreciation_entries',
        'maintenance_records', 
        'asset_categories',
        'budgets',
        'budget_line_items',
        'tax_jurisdictions',
        'tax_rates',
        'tax_transactions',
        'tax_transaction_components',
        'tax_exemptions',
        'tax_returns',
        'accounts',
        'journal_entries',
        'journal_entry_lines',
        'fiscal_periods'
    ]
    
    # Drop RLS policies first
    sensitive_tables = [
        'fixed_assets', 'depreciation_entries', 'maintenance_records',
        'budgets', 'budget_line_items', 'tax_transactions', 'accounts',
        'journal_entries', 'journal_entry_lines'
    ]
    
    for table in sensitive_tables:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
    
    # Drop tenant_id columns and indexes
    for table in tables:
        op.drop_index(f'idx_{table}_tenant_id', table)
        op.drop_column(table, 'tenant_id')