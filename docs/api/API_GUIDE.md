# API Documentation

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.paksa.com`

## Authentication

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

### Using Authentication
Include the token in all requests:
```http
Authorization: Bearer {access_token}
```

## Standard Response Format

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "VAL_001",
    "message": "Validation error",
    "details": { ... }
  }
}
```

### Paginated Response
```json
{
  "status": "success",
  "data": [...],
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Accounts Payable (AP)

### Get Dashboard Stats
```http
GET /api/ap/dashboard/stats
```

### List Vendors
```http
GET /api/ap/vendors?page=1&page_size=20&status=active
```

### Create Vendor
```http
POST /api/ap/vendors
Content-Type: application/json

{
  "vendor_code": "V001",
  "vendor_name": "ABC Supplies",
  "email": "contact@abc.com",
  "phone": "123-456-7890",
  "payment_terms": "Net 30"
}
```

### Create Bill
```http
POST /api/ap/bills
Content-Type: application/json

{
  "vendor_id": "uuid",
  "invoice_number": "INV-001",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-15",
  "line_items": [
    {
      "description": "Office Supplies",
      "quantity": 10,
      "unit_price": 25.00,
      "amount": 250.00
    }
  ]
}
```

### Process Payment
```http
POST /api/ap/payments
Content-Type: application/json

{
  "vendor_id": "uuid",
  "payment_date": "2024-01-20",
  "amount": 250.00,
  "payment_method": "bank_transfer",
  "invoices": [
    {
      "invoice_id": "uuid",
      "amount": 250.00
    }
  ]
}
```

## Accounts Receivable (AR)

### Get Analytics
```http
GET /api/ar/analytics
```

### List Customers
```http
GET /api/ar/customers?page=1&page_size=20
```

### Create Customer
```http
POST /api/ar/customers
Content-Type: application/json

{
  "customer_code": "C001",
  "customer_name": "XYZ Corp",
  "email": "billing@xyz.com",
  "phone": "987-654-3210",
  "credit_limit": 10000.00
}
```

### Create Invoice
```http
POST /api/ar/invoices
Content-Type: application/json

{
  "customer_id": "uuid",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-15",
  "line_items": [
    {
      "description": "Consulting Services",
      "quantity": 40,
      "unit_price": 150.00,
      "amount": 6000.00
    }
  ]
}
```

### Record Payment
```http
POST /api/ar/payments
Content-Type: application/json

{
  "customer_id": "uuid",
  "invoice_id": "uuid",
  "payment_date": "2024-01-20",
  "amount": 6000.00,
  "payment_method": "bank_transfer"
}
```

## General Ledger (GL)

### List Accounts
```http
GET /api/gl/accounts?page=1&page_size=50
```

### Create Journal Entry
```http
POST /api/gl/journal-entries
Content-Type: application/json

{
  "entry_date": "2024-01-15",
  "description": "Monthly rent payment",
  "lines": [
    {
      "account_id": "uuid",
      "debit_amount": 2000.00,
      "credit_amount": 0,
      "description": "Rent expense"
    },
    {
      "account_id": "uuid",
      "debit_amount": 0,
      "credit_amount": 2000.00,
      "description": "Cash payment"
    }
  ]
}
```

### Generate Trial Balance
```http
GET /api/gl/reports/trial-balance?as_of_date=2024-01-31
```

## Budget Management

### List Budgets
```http
GET /api/budget/budgets?fiscal_year=2024
```

### Create Budget
```http
POST /api/budget/budgets
Content-Type: application/json

{
  "budget_name": "2024 Operating Budget",
  "budget_year": 2024,
  "line_items": [
    {
      "account_id": "uuid",
      "period": "Q1",
      "budgeted_amount": 50000.00
    }
  ]
}
```

## Payroll

### List Employees
```http
GET /api/payroll/employees?page=1&page_size=20
```

### Create Pay Run
```http
POST /api/payroll/pay-runs
Content-Type: application/json

{
  "pay_period_start": "2024-01-01",
  "pay_period_end": "2024-01-15",
  "pay_date": "2024-01-20"
}
```

### Process Pay Run
```http
POST /api/payroll/pay-runs/{id}/process
```

## Error Codes

| Code | Description |
|------|-------------|
| AUTH_001 | Invalid credentials |
| AUTH_002 | Token expired |
| VAL_001 | Validation error |
| VAL_002 | Missing required field |
| DB_001 | Database error |
| BIZ_001 | Business logic error |
| SYS_001 | System error |

## Rate Limiting
- **Rate**: 100 requests per minute per user
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

## Pagination
All list endpoints support pagination:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `sort_by`: Field to sort by
- `sort_order`: `asc` or `desc`