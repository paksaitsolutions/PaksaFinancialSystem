-- Migration: Create account_balance table
-- Created: 2025-07-09

-- Create the account_balance table
CREATE TABLE IF NOT EXISTS account_balance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL,
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ,
    opening_balance DECIMAL(23, 4) NOT NULL DEFAULT 0,
    period_debit DECIMAL(23, 4) NOT NULL DEFAULT 0,
    period_credit DECIMAL(23, 4) NOT NULL DEFAULT 0,
    closing_balance DECIMAL(23, 4) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Add foreign key constraint
    CONSTRAINT fk_account_balance_account
        FOREIGN KEY (account_id)
        REFERENCES account(id)
        ON DELETE CASCADE,
        
    -- Add unique constraint
    CONSTRAINT uq_account_balance_period
        UNIQUE (account_id, period_start)
);

-- Create index for faster lookups by account_id
CREATE INDEX IF NOT EXISTS idx_account_balance_account_id 
    ON account_balance(account_id);

-- Create index for period queries
CREATE INDEX IF NOT EXISTS idx_account_balance_period 
    ON account_balance(period_start, COALESCE(period_end, 'infinity'));

-- Create a function to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to automatically update the updated_at column
DROP TRIGGER IF EXISTS update_account_balance_updated_at ON account_balance;
CREATE TRIGGER update_account_balance_updated_at
BEFORE UPDATE ON account_balance
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Add a comment to the table
COMMENT ON TABLE account_balance IS 'Stores historical account balances for different periods';

-- Add comments to columns
COMMENT ON COLUMN account_balance.id IS 'Primary key';
COMMENT ON COLUMN account_balance.account_id IS 'Reference to the account';
COMMENT ON COLUMN account_balance.period_start IS 'Start of the period for this balance';
COMMENT ON COLUMN account_balance.period_end IS 'End of the period for this balance (NULL for open periods)';
COMMENT ON COLUMN account_balance.opening_balance IS 'Balance at the start of the period';
COMMENT ON COLUMN account_balance.period_debit IS 'Total debits during the period';
COMMENT ON COLUMN account_balance.period_credit IS 'Total credits during the period';
COMMENT ON COLUMN account_balance.closing_balance IS 'Balance at the end of the period';
COMMENT ON COLUMN account_balance.created_at IS 'When the record was created';
COMMENT ON COLUMN account_balance.updated_at IS 'When the record was last updated';
