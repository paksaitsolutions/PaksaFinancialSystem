# Paksa Financial System - Unified Models Architecture

## Overview
This document outlines the unified model structure that eliminates duplicate classes and provides consistent data architecture across all financial modules.

## Key Benefits
- ✅ **Eliminates Duplicates**: Single source of truth for each entity
- ✅ **Consistent Relationships**: Standardized foreign keys and relationships
- ✅ **Module Integration**: All modules share the same core entities
- ✅ **Data Integrity**: Unified constraints and validation rules
- ✅ **Performance**: Optimized queries across modules

## Core Model Categories

### 1. Financial Core
- **ChartOfAccounts**: Unified chart of accounts for all modules
- **JournalEntry**: Central journal entries from GL, AP, AR, Payroll
- **JournalEntryLine**: Journal entry line items with proper account links

### 2. Vendor Management
- **Vendor**: Unified vendor for AP and Procurement
- **VendorContact**: Vendor contact information

### 3. Customer Management  
- **Customer**: Unified customer for AR and Sales
- **CustomerContact**: Customer contact information

### 4. Accounts Payable
- **APInvoice**: Vendor invoices
- **APInvoiceLineItem**: Invoice line items
- **APPayment**: Vendor payments
- **APInvoicePayment**: Invoice-payment associations

### 5. Accounts Receivable
- **ARInvoice**: Customer invoices
- **ARInvoiceLineItem**: Invoice line items  
- **ARPayment**: Customer payments
- **ARInvoicePayment**: Invoice-payment associations

### 6. Human Resources
- **Employee**: Unified employee for HRM and Payroll
- **Department**: Organizational departments
- **LeaveRequest**: Employee leave management

### 7. Payroll
- **PayrollRun**: Payroll processing runs
- **PayrollEntry**: Individual employee payroll entries

### 8. Inventory & Procurement
- **InventoryItem**: Product/service items
- **InventoryCategory**: Item categorization
- **PurchaseOrder**: Purchase orders
- **PurchaseOrderLineItem**: PO line items

### 9. Tax Management
- **TaxRate**: Tax rates and codes

### 10. Financial Management
- **FinancialPeriod**: Accounting periods
- **Budget**: Budget planning and tracking

### 11. System Configuration
- **Company**: Company/tenant information
- **Currency**: Multi-currency support
- **ExchangeRate**: Currency exchange rates

## Module Integration

### General Ledger (GL)
- Uses: ChartOfAccounts, JournalEntry, JournalEntryLine
- Integrates with: All modules via journal entries

### Accounts Payable (AP)  
- Uses: Vendor, APInvoice, APPayment, ChartOfAccounts
- Integrates with: GL (journal entries), Procurement (POs)

### Accounts Receivable (AR)
- Uses: Customer, ARInvoice, ARPayment, ChartOfAccounts  
- Integrates with: GL (journal entries), Inventory (items)

### Payroll
- Uses: Employee, Department, PayrollRun, PayrollEntry
- Integrates with: GL (journal entries), HRM (employees)

### Inventory
- Uses: InventoryItem, InventoryCategory, PurchaseOrder
- Integrates with: AP (invoices), GL (valuations)

### Human Resources (HRM)
- Uses: Employee, Department, LeaveRequest
- Integrates with: Payroll (employee data)

## Data Flow Integration

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Vendors   │────│ AP Invoices  │────│   GL        │
└─────────────┘    └──────────────┘    │ Journal     │
                                       │ Entries     │
┌─────────────┐    ┌──────────────┐    │             │
│  Customers  │────│ AR Invoices  │────│             │
└─────────────┘    └──────────────┘    │             │
                                       │             │
┌─────────────┐    ┌──────────────┐    │             │
│ Employees   │────│   Payroll    │────│             │
└─────────────┘    └──────────────┘    │             │
                                       │             │
┌─────────────┐    ┌──────────────┐    │             │
│ Inventory   │────│ Valuations   │────│             │
└─────────────┘    └──────────────┘    └─────────────┘
```

## Usage Examples

### Import Unified Models
```python
from app.models import (
    ChartOfAccounts,
    Vendor, 
    APInvoice,
    Customer,
    ARInvoice,
    Employee,
    PayrollRun
)
```

### Create AP Invoice with GL Integration
```python
# Create vendor invoice
invoice = APInvoice(
    vendor_id=vendor.id,
    invoice_number="INV-001",
    total_amount=1000.00
)

# Automatically creates journal entry
journal_entry = JournalEntry(
    description=f"AP Invoice {invoice.invoice_number}",
    source_module="AP"
)
```

### Cross-Module Reporting
```python
# Get all transactions for a customer across AR and GL
customer_transactions = session.query(JournalEntry).join(
    ARInvoice
).filter(
    ARInvoice.customer_id == customer.id
).all()
```

## Migration from Old Models

### Before (Duplicate Models)
```python
# Multiple duplicate classes
from app.models.accounting import Customer as AccountingCustomer
from app.models.accounts_receivable import Customer as ARCustomer  
from app.models.financial_core import Customer as FinancialCustomer
```

### After (Unified Models)
```python
# Single unified class
from app.models import Customer
```

## Best Practices

1. **Always use unified models** from `app.models` import
2. **Leverage relationships** for cross-module data access
3. **Use source_module** field in JournalEntry for tracking
4. **Maintain referential integrity** through proper foreign keys
5. **Follow naming conventions** for consistency

## Database Schema

All unified models use:
- **UUID primary keys** for better distribution
- **Audit fields** (created_at, updated_at, created_by)
- **Soft delete support** where applicable
- **Proper indexing** for performance
- **Consistent naming** (snake_case table names)

## Performance Optimizations

- **Indexed foreign keys** for fast joins
- **Composite indexes** for common query patterns  
- **Relationship loading** strategies (lazy/eager)
- **Query optimization** through proper joins
- **Caching strategies** for frequently accessed data

This unified architecture ensures all modules work together seamlessly while maintaining data integrity and performance.