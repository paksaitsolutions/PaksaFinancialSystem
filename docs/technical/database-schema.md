# Database Schema Documentation

## Overview
The Paksa Financial System uses PostgreSQL with a multi-tenant architecture where all tables include a `tenant_id` for data isolation.

## Core Tables

### Users & Authentication
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_tenant (tenant_id),
    INDEX idx_users_email (email)
);

-- Roles table
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    permissions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Financial Core
```sql
-- Chart of Accounts
CREATE TABLE chart_of_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    account_code VARCHAR(20) NOT NULL,
    account_name VARCHAR(200) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    parent_account_id UUID,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_coa_tenant (tenant_id),
    INDEX idx_coa_code (account_code)
);

-- Journal Entries
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    entry_number VARCHAR(50) NOT NULL,
    entry_date DATE NOT NULL,
    description TEXT,
    total_debit DECIMAL(18,2) NOT NULL,
    total_credit DECIMAL(18,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_je_tenant (tenant_id),
    INDEX idx_je_date (entry_date)
);
```

### Invoicing
```sql
-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    invoice_number VARCHAR(50) NOT NULL,
    customer_id UUID NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    subtotal DECIMAL(18,2) NOT NULL,
    tax_amount DECIMAL(18,2) DEFAULT 0,
    total_amount DECIMAL(18,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_invoices_tenant (tenant_id),
    INDEX idx_invoices_number (invoice_number),
    INDEX idx_invoices_customer (customer_id)
);
```

### HRM
```sql
-- Employees
CREATE TABLE employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    employee_id VARCHAR(50) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    position VARCHAR(100),
    hire_date DATE NOT NULL,
    salary DECIMAL(18,2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_employees_tenant (tenant_id),
    INDEX idx_employees_id (employee_id)
);
```

## Indexes and Performance

### Primary Indexes
- All tables have UUID primary keys
- Tenant isolation through `tenant_id` indexes
- Business key indexes (invoice_number, employee_id, etc.)

### Composite Indexes
```sql
-- Multi-column indexes for common queries
CREATE INDEX idx_invoices_tenant_status ON invoices (tenant_id, status);
CREATE INDEX idx_employees_tenant_active ON employees (tenant_id, is_active);
CREATE INDEX idx_journal_entries_tenant_date ON journal_entries (tenant_id, entry_date);
```

## Data Types and Constraints

### Standard Patterns
- **IDs**: UUID with `gen_random_uuid()` default
- **Monetary**: DECIMAL(18,2) for currency values
- **Dates**: DATE for date-only, TIMESTAMP for datetime
- **Status**: VARCHAR(20) with enum-like constraints
- **Tenant Isolation**: UUID tenant_id in all business tables

### Constraints
```sql
-- Example constraints
ALTER TABLE invoices ADD CONSTRAINT chk_invoice_amounts 
    CHECK (subtotal >= 0 AND tax_amount >= 0 AND total_amount >= 0);

ALTER TABLE employees ADD CONSTRAINT chk_employee_salary 
    CHECK (salary IS NULL OR salary >= 0);
```

## Relationships

### Foreign Keys
- All tenant-scoped relationships include tenant_id validation
- Soft deletes preferred over hard deletes
- Cascade rules defined for data integrity

### Multi-Tenant Considerations
- Row-level security policies enforce tenant isolation
- All queries automatically filtered by tenant_id
- Cross-tenant references prevented by design