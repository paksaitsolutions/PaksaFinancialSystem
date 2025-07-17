# Tax Module API Reference

## Base URL
```
/api/v1/tax
```

## Authentication
All API endpoints require authentication using Bearer token:
```
Authorization: Bearer <your_access_token>
```

## Advanced Features

### AI-Powered Tax Optimization
Leverage machine learning to optimize tax strategies and minimize liabilities:
- **Smart Deduction Finder**: Identifies potential tax deductions and credits
- **Tax Scenario Planning**: Simulates different tax scenarios
- **Expense Categorization**: AI-driven categorization of expenses for optimal tax treatment

### Automated Tax Filing
Automate the entire tax filing process:
- **E-Filing Integration**: Direct submission to tax authorities
- **Form Generation**: Automatic generation of required tax forms
- **Payment Scheduling**: Schedule tax payments to avoid penalties

### Real-time Compliance Monitoring
Stay compliant with changing tax regulations:
- **Regulatory Updates**: Automatic updates for tax law changes
- **Compliance Alerts**: Real-time notifications for compliance issues
- **Audit Trail**: Comprehensive logging of all tax-related activities

## Endpoints

### Tax Transactions

#### Create a Tax Transaction
```http
POST /transactions
```

**Request Body**
```json
{
  "transaction_date": "2023-01-01",
  "tax_rate": 0.15,
  "taxable_amount": 1000.00,
  "tax_amount": 150.00,
  "total_amount": 1150.00,
  "document_number": "INV-001",
  "tax_type": "VAT",
  "transaction_type": "SALE",
  "status": "DRAFT",
  "company_id": "comp_123",
  "components": [
    {
      "tax_component": "VAT",
      "tax_rate": 0.15,
      "taxable_amount": 1000.00,
      "tax_amount": 150.00,
      "tax_type": "VAT",
      "tax_category": "STANDARD",
      "is_tax_inclusive": false
    }
  ]
}
```

**Response**
```json
{
  "id": "txn_123",
  "transaction_date": "2023-01-01",
  "tax_rate": 0.15,
  "taxable_amount": 1000.00,
  "tax_amount": 150.00,
  "total_amount": 1150.00,
  "document_number": "INV-001",
  "status": "DRAFT",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

#### Get Tax Transaction
```http
GET /transactions/{id}
```

**Response**
```json
{
  "id": "txn_123",
  "transaction_date": "2023-01-01",
  "tax_rate": 0.15,
  "taxable_amount": 1000.00,
  "tax_amount": 150.00,
  "total_amount": 1150.00,
  "document_number": "INV-001",
  "status": "DRAFT",
  "components": [
    {
      "id": "comp_123",
      "tax_component": "VAT",
      "tax_rate": 0.15,
      "taxable_amount": 1000.00,
      "tax_amount": 150.00,
      "tax_type": "VAT",
      "tax_category": "STANDARD",
      "is_tax_inclusive": false,
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    }
  ],
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

#### List Tax Transactions
```http
GET /transactions
```

**Query Parameters**
- `status` - Filter by status (DRAFT, POSTED, VOIDED)
- `start_date` - Start date filter (YYYY-MM-DD)
- `end_date` - End date filter (YYYY-MM-DD)
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20)

**Response**
```json
{
  "data": [
    {
      "id": "txn_123",
      "transaction_date": "2023-01-01",
      "document_number": "INV-001",
      "taxable_amount": 1000.00,
      "tax_amount": 150.00,
      "total_amount": 1150.00,
      "status": "DRAFT"
    }
  ],
  "pagination": {
    "total": 1,
    "page": 1,
    "limit": 20,
    "total_pages": 1
  }
}
```

### Tax Rates

#### List Tax Rates
```http
GET /rates
```

**Response**
```json
[
  {
    "id": "rate_123",
    "name": "Standard VAT",
    "rate": 0.15,
    "type": "PERCENTAGE",
    "is_active": true,
    "effective_from": "2023-01-01",
    "effective_to": null,
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  }
]
```

### Error Responses

#### 400 Bad Request
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "taxable_amount",
        "message": "must be a positive number"
      }
    ]
  }
}
```

#### 401 Unauthorized
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

#### 404 Not Found
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Tax transaction not found"
  }
}
```

## Rate Limiting
- 100 requests per minute per IP address
- 1000 requests per hour per user

## Versioning
API version is included in the URL path (e.g., `/api/v1/...`).

## Support
For support, please contact support@paksa.com
