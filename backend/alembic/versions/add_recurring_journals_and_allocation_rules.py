"""Add recurring_journals and allocation_rules tables

Revision ID: 1a2b3c4d5e6f
Revises: 123456789abc
Create Date: 2025-03-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = '123456789abc'
branch_labels = None
depends_on = None

def upgrade():
    # Create enum types first
    op.execute("""
    CREATE TYPE recurrence_frequency AS ENUM (
        'daily', 'weekly', 'biweekly', 'monthly', 
        'quarterly', 'semi_annually', 'annually', 'custom'
    )
    """)
    
    op.execute("""
    CREATE TYPE recurrence_end_type AS ENUM (
        'never', 'after_occurrences', 'on_date'
    )
    """)
    
    op.execute("""
    CREATE TYPE recurring_journal_status AS ENUM (
        'active', 'paused', 'completed', 'cancelled'
    )
    """)
    
    # Create recurring_journal_entries table
    op.create_table(
        'recurring_journal_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('frequency', sa.Enum('daily', 'weekly', 'biweekly', 'monthly', 'quarterly', 'semi_annually', 'annually', 'custom', name='recurrence_frequency'), nullable=False),
        sa.Column('interval', sa.Integer(), server_default='1', nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_type', sa.Enum('never', 'after_occurrences', 'on_date', name='recurrence_end_type'), server_default='never', nullable=False),
        sa.Column('end_after_occurrences', sa.Integer(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('active', 'paused', 'completed', 'cancelled', name='recurring_journal_status'), server_default='active', nullable=False),
        sa.Column('last_run_date', sa.Date(), nullable=True),
        sa.Column('next_run_date', sa.Date(), nullable=True),
        sa.Column('total_occurrences', sa.Integer(), server_default='0', nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on frequently queried columns
    op.create_index(op.f('ix_recurring_journal_entries_company_id'), 'recurring_journal_entries', ['company_id'], unique=False)
    op.create_index(op.f('ix_recurring_journal_entries_created_by'), 'recurring_journal_entries', ['created_by'], unique=False)
    op.create_index(op.f('ix_recurring_journal_entries_status'), 'recurring_journal_entries', ['status'], unique=False)
    op.create_index(op.f('ix_recurring_journal_entries_next_run_date'), 'recurring_journal_entries', ['next_run_date'], unique=False)
    
    # Create recurring_journal_templates table
    op.create_table(
        'recurring_journal_templates',
        sa.Column('recurring_journal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['recurring_journal_id'], ['recurring_journal_entries.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('recurring_journal_id')
    )
    
    # Create allocation_rules table
    op.create_table(
        'allocation_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('allocation_method', sa.String(length=50), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on allocation_rules
    op.create_index(op.f('ix_allocation_rules_company_id'), 'allocation_rules', ['company_id'], unique=False)
    op.create_index(op.f('ix_allocation_rules_is_active'), 'allocation_rules', ['is_active'], unique=False)
    
    # Create allocation_destinations table
    op.create_table(
        'allocation_destinations',
        sa.Column('allocation_rule_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('percentage', sa.Numeric(5, 2), nullable=True),
        sa.Column('fixed_amount', sa.Numeric(20, 6), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reference', sa.String(length=100), nullable=True),
        sa.Column('sequence', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['chart_of_accounts.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['allocation_rule_id'], ['allocation_rules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('allocation_rule_id', 'account_id')
    )
    
    # Create index on allocation_destinations
    op.create_index(op.f('ix_allocation_destinations_account_id'), 'allocation_destinations', ['account_id'], unique=False)
    
    # Add recurring_journal_id to journal_entries
    op.add_column('journal_entries', sa.Column('recurring_journal_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_journal_entries_recurring_journal_id',
        'journal_entries',
        'recurring_journal_entries',
        ['recurring_journal_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_index(op.f('ix_journal_entries_recurring_journal_id'), 'journal_entries', ['recurring_journal_id'], unique=False)


def downgrade():
    # Drop foreign key and index from journal_entries
    op.drop_constraint('fk_journal_entries_recurring_journal_id', 'journal_entries', type_='foreignkey')
    op.drop_index(op.f('ix_journal_entries_recurring_journal_id'), table_name='journal_entries')
    op.drop_column('journal_entries', 'recurring_journal_id')
    
    # Drop tables in reverse order of creation
    op.drop_table('allocation_destinations')
    op.drop_table('allocation_rules')
    op.drop_table('recurring_journal_templates')
    op.drop_table('recurring_journal_entries')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS recurring_journal_status")
    op.execute("DROP TYPE IF EXISTS recurrence_end_type")
    op.execute("DROP TYPE IF EXISTS recurrence_frequency")
