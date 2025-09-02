"""Create tenant companies tables

Revision ID: 20250124_03_create_tenant_companies
Revises: 20250124_02_enhanced_company_settings
Create Date: 2025-01-24 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250124_03_create_tenant_companies'
down_revision = '20250124_02_enhanced_company_settings'
branch_labels = None
depends_on = None


def upgrade():
    # Create tenant_companies table
    op.create_table('tenant_companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('size', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('subdomain', sa.String(length=100), nullable=False),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True),
        sa.Column('secondary_color', sa.String(length=7), nullable=True),
        sa.Column('plan', sa.String(length=50), nullable=False),
        sa.Column('max_users', sa.Integer(), nullable=False),
        sa.Column('current_users', sa.Integer(), nullable=False),
        sa.Column('storage_limit_gb', sa.Integer(), nullable=False),
        sa.Column('api_rate_limit', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.Column('subscription_ends_at', sa.DateTime(), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('date_format', sa.String(length=20), nullable=False),
        sa.Column('enabled_modules', sa.JSON(), nullable=True),
        sa.Column('feature_flags', sa.JSON(), nullable=True),
        sa.Column('custom_settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('domain'),
        sa.UniqueConstraint('subdomain')
    )
    
    # Create indexes
    op.create_index(op.f('ix_tenant_companies_id'), 'tenant_companies', ['id'], unique=False)
    op.create_index(op.f('ix_tenant_companies_name'), 'tenant_companies', ['name'], unique=False)
    op.create_index(op.f('ix_tenant_companies_code'), 'tenant_companies', ['code'], unique=False)
    op.create_index(op.f('ix_tenant_companies_domain'), 'tenant_companies', ['domain'], unique=False)
    op.create_index(op.f('ix_tenant_companies_subdomain'), 'tenant_companies', ['subdomain'], unique=False)

    # Create company_admins table
    op.create_table('company_admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['tenant_companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create company_modules table
    op.create_table('company_modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('module_name', sa.String(length=100), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('license_type', sa.String(length=50), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['tenant_companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create company_subscriptions table
    op.create_table('company_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('plan_name', sa.String(length=50), nullable=False),
        sa.Column('billing_cycle', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('starts_at', sa.DateTime(), nullable=False),
        sa.Column('ends_at', sa.DateTime(), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('external_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['tenant_companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Add company_id column to users table if it doesn't exist
    try:
        op.add_column('users', sa.Column('company_id', sa.Integer(), nullable=True))
        op.create_foreign_key('fk_users_company_id', 'users', 'tenant_companies', ['company_id'], ['id'])
    except Exception:
        # Column might already exist
        pass

    # Set default values for new columns
    op.execute("UPDATE tenant_companies SET primary_color = '#1976D2' WHERE primary_color IS NULL")
    op.execute("UPDATE tenant_companies SET plan = 'Basic' WHERE plan IS NULL OR plan = ''")
    op.execute("UPDATE tenant_companies SET max_users = 10 WHERE max_users IS NULL OR max_users = 0")
    op.execute("UPDATE tenant_companies SET current_users = 0 WHERE current_users IS NULL")
    op.execute("UPDATE tenant_companies SET storage_limit_gb = 5 WHERE storage_limit_gb IS NULL OR storage_limit_gb = 0")
    op.execute("UPDATE tenant_companies SET api_rate_limit = 1000 WHERE api_rate_limit IS NULL OR api_rate_limit = 0")
    op.execute("UPDATE tenant_companies SET status = 'Active' WHERE status IS NULL OR status = ''")
    op.execute("UPDATE tenant_companies SET is_active = true WHERE is_active IS NULL")
    op.execute("UPDATE tenant_companies SET timezone = 'UTC' WHERE timezone IS NULL OR timezone = ''")
    op.execute("UPDATE tenant_companies SET language = 'en' WHERE language IS NULL OR language = ''")
    op.execute("UPDATE tenant_companies SET currency = 'USD' WHERE currency IS NULL OR currency = ''")
    op.execute("UPDATE tenant_companies SET date_format = 'MM/DD/YYYY' WHERE date_format IS NULL OR date_format = ''")
    
    # Set default values for company_admins
    op.execute("UPDATE company_admins SET role = 'admin' WHERE role IS NULL OR role = ''")
    op.execute("UPDATE company_admins SET is_primary = false WHERE is_primary IS NULL")
    
    # Set default values for company_modules
    op.execute("UPDATE company_modules SET is_enabled = true WHERE is_enabled IS NULL")
    
    # Set default values for company_subscriptions
    op.execute("UPDATE company_subscriptions SET billing_cycle = 'monthly' WHERE billing_cycle IS NULL OR billing_cycle = ''")
    op.execute("UPDATE company_subscriptions SET currency = 'USD' WHERE currency IS NULL OR currency = ''")
    op.execute("UPDATE company_subscriptions SET status = 'active' WHERE status IS NULL OR status = ''")
    op.execute("UPDATE company_subscriptions SET auto_renew = true WHERE auto_renew IS NULL")


def downgrade():
    # Drop foreign key constraint from users table
    try:
        op.drop_constraint('fk_users_company_id', 'users', type_='foreignkey')
        op.drop_column('users', 'company_id')
    except Exception:
        pass

    # Drop tables in reverse order
    op.drop_table('company_subscriptions')
    op.drop_table('company_modules')
    op.drop_table('company_admins')
    
    # Drop indexes
    op.drop_index(op.f('ix_tenant_companies_subdomain'), table_name='tenant_companies')
    op.drop_index(op.f('ix_tenant_companies_domain'), table_name='tenant_companies')
    op.drop_index(op.f('ix_tenant_companies_code'), table_name='tenant_companies')
    op.drop_index(op.f('ix_tenant_companies_name'), table_name='tenant_companies')
    op.drop_index(op.f('ix_tenant_companies_id'), table_name='tenant_companies')
    
    op.drop_table('tenant_companies')