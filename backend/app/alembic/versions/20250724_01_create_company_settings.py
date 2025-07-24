"""
Alembic migration for company_settings table.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'company_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('company_id', sa.Integer(), nullable=False, index=True),
        sa.Column('invoice_template', sa.JSON(), nullable=True),
        sa.Column('branding', sa.JSON(), nullable=True),
        sa.Column('default_currency', sa.String(length=10), nullable=True),
        sa.Column('tax_rates', sa.JSON(), nullable=True),
        sa.Column('languages', sa.JSON(), nullable=True),
        sa.Column('payment_methods', sa.JSON(), nullable=True),
        sa.Column('document_numbering', sa.JSON(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('notifications', sa.JSON(), nullable=True),
        sa.Column('integrations', sa.JSON(), nullable=True),
        sa.Column('feature_toggles', sa.JSON(), nullable=True),
        sa.Column('data_retention', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    )
    op.create_index('ix_company_settings_company_id', 'company_settings', ['company_id'])

def downgrade():
    op.drop_index('ix_company_settings_company_id', table_name='company_settings')
    op.drop_table('company_settings')
