# Database Schema Documentation

## Overview
Paksa Financial System uses a unified database schema with centralized models in `app/models/core_models.py`.

## Core Tables

### users
User accounts and authentication
```sql
- id: UUID (PK)
- username: VARCHAR(50) UNIQUE
- email: VARCHAR(255) UNIQUE
- hashed_password: VARCHAR(255)
- full_name: VARCHAR(255)
- is_active: BOOLEAN
- is_superuser: BOOLEAN
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### companies
Multi-tenant company data
```sql
- id: UUID (PK)
- company_code: VARCHAR(20) UNIQUE
- company_name: VARCHAR(255)
- tax_id: VARCHAR(50)
- base_currency: VARCHAR(3)
- fiscal_year_end: VARCHAR(5)
- status: ENUM
```

## Financial Tables

### chart_of_accounts
GL account master
```sql
- id: UUID (PK)
- company_id: UUID (FK)
- account_code: VARCHAR(20) UNIQUE
- account_name: VARCHAR(255)
- account_type: VARCHAR(50)
- balance: NUMERIC(15,2)
- is_active: BOOLEAN
```

### journal_entries
GL journal entries
```sql
- id: UUID (PK)
- company_id: UUID (FK)
- entry_number: VARCHAR(50) UNIQUE
- entry_date: DATE
- description: TEXT
- total_debit: NUMERIC(15,2)
- total_credit: NUMERIC(15,2)
- status: VARCHAR(20)
- source_module: VARCHAR(20)
```

### journal_entry_lines
Journal entry line items
```sql
- id: UUID (PK)
- journal_entry_id: UUID (FK)
- account_id: UUID (FK)
- debit_amount: NUMERIC(15,2)
- credit_amount: NUMERIC(15,2)
- line_number: INTEGER
```

## AP Tables

### vendors
Vendor master
```sql
- id: UUID (PK)
- company_id: UUID (FK)
- vendor_code: VARCHAR(20) UNIQUE
- vendor_name: VARCHAR(255)
- email: VARCHAR(255)
- phone: VARCHAR(50)
- payment_terms: VARCHAR(50)
- credit_limit: NUMERIC(15,2)
- current_balance: NUMERIC(15,2)
- status: ENUM
```

### ap_invoices
AP bills/invoices
```sql
- id: UUID (PK)
- company_id: UUID (FK)
- vendor_id: UUID (FK)
- invoice_number: VARCHAR(50) UNIQUE
- invoice_date: DATE
- due_date: DATE
- total_amount: NUMERIC(15,2)
- paid_amount: NUMERIC(15,2)
- status: ENUM
```

### ap_payments
AP payments
```sql
- id: UUID (PK)
- company_id: UUID (FK)
- vendor_id: UUID (FK)
- payment_number: VARCHAR(50) UNIQUE
- payment_date: DATE
- amount: NUMERIC(15,2)
- payment_method: ENUM
- status: ENUM
```

## AR Tables

### customers
Customer master
```sql
- id: UUID (PK)
- company_id: UUID (FK)
- customer_code: VARCHAR(20) UNIQUE
- customer_name: VARCHAR(255)
- email: VARCHAR(255)
- phone: VARCHAR(50)
- credit_limit: NUMERIC(15,2)
- current_balance: NUMERIC(15,2)
- status: ENUM
```

### ar_invoices
AR invoices
```sql
- id: UUID (PK)
- company_id: UUID (FK)
- customer_id: UUID (FK)
- invoice_number: VARCHAR(50) UNIQUE
- invoice_date: DATE
- due_date: DATE
- total_amount: NUMERIC(15,2)
- paid_amount: NUMERIC(15,2)
- status: ENUM
```

### ar_payments
AR payments
```sql
- id: UUID (PK)
- company_id: UUID (FK)
- customer_id: UUID (FK)
- payment_number: VARCHAR(50) UNIQUE
- payment_date: DATE
- amount: NUMERIC(15,2)
- payment_method: ENUM
- status: ENUM
```

## Payroll Tables

### employees
Employee master
```sql
- id: UUID (PK)
- company_id: UUID (FK)
- employee_code: VARCHAR(20) UNIQUE
- first_name: VARCHAR(100)
- last_name: VARCHAR(100)
- email: VARCHAR(255)
- hire_date: DATE
- salary: NUMERIC(15,2)
- employment_type: ENUM
- status: VARCHAR(20)
```

### payroll_runs
Payroll processing runs
```sql
- id: UUID (PK)
- company_id: UUID (FK)
- run_number: VARCHAR(50) UNIQUE
- pay_period_start: DATE
- pay_period_end: DATE
- pay_date: DATE
- total_gross: NUMERIC(15,2)
- total_deductions: NUMERIC(15,2)
- total_net: NUMERIC(15,2)
- status: VARCHAR(20)
```

## Asset Tables

### fixed_assets
Fixed asset register
```sql
- id: UUID (PK)
- company_id: UUID (FK)
- asset_number: VARCHAR(50) UNIQUE
- asset_name: VARCHAR(255)
- purchase_date: DATE
- purchase_cost: NUMERIC(15,2)
- salvage_value: NUMERIC(15,2)
- useful_life_years: INTEGER
- accumulated_depreciation: NUMERIC(15,2)
- status: VARCHAR(20)
```

## Relationships

### One-to-Many
- companies → chart_of_accounts
- companies → vendors
- companies → customers
- vendors → ap_invoices
- customers → ar_invoices
- journal_entries → journal_entry_lines

### Many-to-Many
- ap_invoices ↔ ap_payments (via ap_invoice_payments)
- ar_invoices ↔ ar_payments (via ar_invoice_payments)

## Indexes

### Performance Indexes
```sql
CREATE INDEX idx_vendors_company ON vendors(company_id);
CREATE INDEX idx_invoices_vendor ON ap_invoices(vendor_id);
CREATE INDEX idx_invoices_date ON ap_invoices(invoice_date);
CREATE INDEX idx_payments_date ON ap_payments(payment_date);
```

## Enums

### InvoiceStatus
- DRAFT
- SENT
- PAID
- OVERDUE
- CANCELLED

### PaymentStatus
- PENDING
- COMPLETED
- FAILED
- CANCELLED

### PaymentMethod
- CASH
- CHECK
- CREDIT_CARD
- BANK_TRANSFER
- ACH

## Audit Fields
All tables include:
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- created_by: VARCHAR(200)
- updated_by: VARCHAR(200)

## Migrations
Located in: `backend/alembic/versions/`

### Create Migration
```bash
alembic revision --autogenerate -m "description"
```

### Apply Migration
```bash
alembic upgrade head
```

### Rollback
```bash
alembic downgrade -1
```

## Backup & Recovery
- Daily automated backups
- 30-day retention
- Point-in-time recovery available
- Backup location: Configured in deployment