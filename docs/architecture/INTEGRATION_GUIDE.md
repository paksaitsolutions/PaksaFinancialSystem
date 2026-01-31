# Financial Modules Integration Guide

## Overview
The Paksa Financial System uses a unified model architecture where all financial modules (AP, AR, Cash, Payroll) integrate seamlessly with the General Ledger.

## Architecture

### Unified Models
All modules use models from `app.models.core_models`:
- `ChartOfAccounts` - Single chart of accounts for all modules
- `JournalEntry` - Unified journal entries with source tracking
- `JournalEntryLine` - Individual transaction lines

### Automatic GL Integration
Every financial transaction automatically generates GL journal entries:

**AP Transactions:**
- Invoice: Dr. Expense, Cr. Accounts Payable
- Payment: Dr. Accounts Payable, Cr. Cash

**AR Transactions:**
- Invoice: Dr. Accounts Receivable, Cr. Revenue  
- Payment: Dr. Cash, Cr. Accounts Receivable

**Cash Transactions:**
- All bank transactions post to GL with appropriate accounts

## Usage

### Import Models
```python
from app.models import ChartOfAccounts, JournalEntry, APInvoice, ARInvoice
```

### Create Transactions
```python
# AP Invoice automatically creates GL entry
invoice = ap_service.create_invoice(invoice_data)

# AR Payment automatically creates GL entry
payment = ar_service.create_payment(payment_data)
```

### Generate Reports
```python
# Consolidated financial statements
from app.services.gl.financial_statement_service import FinancialStatementService
service = FinancialStatementService(db)
balance_sheet = service.generate_financial_statement(FSType.BALANCE_SHEET, company_id, end_date)
```

## Key Benefits
- Single source of truth for all financial data
- Automatic audit trail through GL integration
- Consolidated reporting across all modules
- Real-time financial position visibility