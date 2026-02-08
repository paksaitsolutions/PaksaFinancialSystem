# Paksa Financial System API Documentation

## Overview
The Paksa Financial System provides a comprehensive RESTful API for financial management operations. All endpoints are secured with JWT authentication and support multi-tenant architecture.

## Contract Governance
- Backward compatibility policy: `docs/api/API_COMPATIBILITY_POLICY.md`
- Deprecation calendar: `docs/api/DEPRECATION_CALENDAR.md`
- Versioned OpenAPI snapshots: `docs/api/openapi/`

## Base URL
```
Production: https://api.paksa.com/v1
Development: http://localhost:8000/api/v1
```

## Authentication
All API requests require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Core Modules

### 1. General Ledger API
**Base Path:** `/api/v1/gl`

#### Accounts
- `GET /accounts` - List all accounts
- `POST /accounts` - Create new account
- `GET /accounts/{id}` - Get account details
- `PUT /accounts/{id}` - Update account
- `DELETE /accounts/{id}` - Delete account

#### Journal Entries
- `GET /journal-entries` - List journal entries
- `POST /journal-entries` - Create journal entry
- `GET /journal-entries/{id}` - Get journal entry
- `PUT /journal-entries/{id}` - Update journal entry
- `DELETE /journal-entries/{id}` - Delete journal entry

### 2. Accounts Payable API
**Base Path:** `/api/v1/ap`

#### Vendors
- `GET /vendors` - List vendors
- `POST /vendors` - Create vendor
- `GET /vendors/{id}` - Get vendor details
- `PUT /vendors/{id}` - Update vendor

#### Invoices
- `GET /invoices` - List AP invoices
- `POST /invoices` - Create AP invoice
- `GET /invoices/{id}` - Get invoice details

### 3. Accounts Receivable API
**Base Path:** `/api/v1/ar`

#### Customers
- `GET /customers` - List customers
- `POST /customers` - Create customer
- `GET /customers/{id}` - Get customer details

#### Invoices
- `GET /invoices` - List AR invoices
- `POST /invoices` - Create AR invoice

### 4. Budget Management API
**Base Path:** `/api/v1/budget`

#### Budgets
- `GET /budgets` - List budgets
- `POST /budgets` - Create budget
- `GET /budgets/{id}` - Get budget details
- `PUT /budgets/{id}` - Update budget

### 5. Human Resources API
**Base Path:** `/api/v1/hrm`

#### Employees
- `GET /employees` - List employees
- `POST /employees` - Create employee
- `GET /employees/{id}` - Get employee details

### 6. Payroll API
**Base Path:** `/api/v1/payroll`

#### Payroll Runs
- `GET /runs` - List payroll runs
- `POST /runs` - Create payroll run
- `GET /runs/{id}` - Get payroll run details

## Error Handling
All API endpoints return standardized error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "account_name",
      "issue": "Required field missing"
    }
  }
}
```

## Rate Limiting
- 1000 requests per hour per user
- 100 requests per minute per IP
- Rate limit headers included in responses

## Pagination
List endpoints support pagination:
```
GET /api/v1/accounts?page=1&limit=50&sort=name&order=asc
```

## Multi-Tenant Support
All requests are automatically scoped to the authenticated user's tenant. Cross-tenant access is prevented at the database level.

## Interactive Documentation
Visit `/docs` for Swagger UI documentation with interactive API testing.
