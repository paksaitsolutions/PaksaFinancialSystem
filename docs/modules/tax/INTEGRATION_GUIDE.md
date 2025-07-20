# Tax Module Integration Guide

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Webhooks](#webhooks)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Overview
This guide provides technical details for integrating with the Tax Module's API. The API follows RESTful principles and uses JSON for request/response payloads.

## Authentication

### API Keys
1. Generate an API key from **Settings** > **API Access**
2. Include the key in the `Authorization` header:
   ```
   Authorization: Bearer your_api_key_here
   ```

### Scopes
- `tax:read` - Read access to tax data
- `tax:write` - Write access to tax data
- `tax:reports` - Access to tax reports

## API Endpoints

### Base URL
```
https://api.paksa.com/v1/tax
```

### Available Endpoints

#### Tax Transactions
- `POST /transactions` - Create a new tax transaction
- `GET /transactions` - List transactions
- `GET /transactions/{id}` - Get transaction details
- `PUT /transactions/{id}` - Update a transaction
- `DELETE /transactions/{id}` - Void a transaction

#### Tax Rates
- `GET /rates` - List tax rates
- `POST /rates` - Create a new tax rate
- `GET /rates/{id}` - Get rate details
- `PUT /rates/{id}` - Update a tax rate

### Example: Creating a Tax Transaction

```javascript
const createTransaction = async () => {
  const response = await fetch('https://api.paksa.com/v1/tax/transactions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer your_api_key_here'
    },
    body: JSON.stringify({
      transaction_date: '2023-01-15',
      tax_rate: 0.15,
      taxable_amount: 1000.00,
      tax_amount: 150.00,
      total_amount: 1150.00,
      document_number: 'INV-001',
      tax_type: 'VAT',
      transaction_type: 'SALE',
      status: 'DRAFT',
      company_id: 'comp_123',
      components: [
        {
          tax_component: 'VAT',
          tax_rate: 0.15,
          taxable_amount: 1000.00,
          tax_amount: 150.00,
          tax_type: 'VAT',
          tax_category: 'STANDARD',
          is_tax_inclusive: false
        }
      ]
    })
  });
  
  return await response.json();
};
```

## Webhooks

### Available Events
- `transaction.created`
- `transaction.updated`
- `transaction.voided`
- `tax_rate.updated`

### Webhook Payload Example
```json
{
  "event": "transaction.created",
  "data": {
    "id": "txn_123",
    "document_number": "INV-001",
    "status": "POSTED",
    "total_amount": 1150.00,
    "tax_amount": 150.00,
    "created_at": "2023-01-15T10:30:00Z"
  },
  "timestamp": "2023-01-15T10:30:05Z"
}
```

### Setting Up Webhooks
1. Go to **Settings** > **Webhooks**
2. Click **Add Webhook**
3. Enter the endpoint URL
4. Select events to subscribe to
5. Set the webhook status to **Active**

## Error Handling

### Common HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Response Format
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

## Rate Limiting
- 100 requests per minute per IP address
- 1000 requests per hour per API key

### Rate Limit Headers
- `X-RateLimit-Limit` - Request limit
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Time when limit resets (UTC timestamp)

## AI-Powered Tax Features

### AI Tax Optimization

#### Smart Deduction Engine
```javascript
// Example: Get AI-suggested deductions
const getDeductionSuggestions = async (companyId, fiscalYear) => {
  const response = await fetch(`/api/v1/tax/ai/deductions/suggestions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      company_id: companyId,
      fiscal_year: fiscalYear,
      analysis_depth: 'DEEP'  // BASIC, STANDARD, or DEEP
    })
  });
  return await response.json();
};
```

#### Tax Scenario Planning
```javascript
// Example: Run tax scenario simulation
const runTaxScenario = async (scenario) => {
  const response = await fetch('/api/v1/tax/ai/scenarios', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      scenario_name: 'expansion_2024',
      base_year: 2023,
      projection_years: 3,
      assumptions: {
        revenue_growth: 0.15,
        expense_categories: [
          { category: 'R&D', growth_rate: 0.2 },
          { category: 'Marketing', growth_rate: 0.1 }
        ]
      },
      tax_strategies: ['R&D_CREDITS', 'DEPRECIATION']
    })
  });
  return await response.json();
};
```

### Automated Tax Filing

#### E-Filing Integration
```javascript
// Example: Submit tax filing
const submitTaxFiling = async (filingData) => {
  const response = await fetch('/api/v1/tax/filings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      tax_year: 2023,
      tax_type: 'INCOME_TAX',
      jurisdiction: 'FEDERAL',
      form_type: '1120',
      filing_data: filingData,
      auto_submit: true,
      payment_strategy: 'AUTO_DEBIT',
      estimated_payment_date: '2023-04-15',
      callback_url: 'https://your-app.com/filing-callback'
    })
  });
  return await response.json();
};
```

### Real-time Compliance Monitoring

#### Compliance Webhook Setup
```javascript
// Example: Set up compliance webhook
const setupComplianceWebhook = async () => {
  const response = await fetch('/api/v1/webhooks', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      name: 'compliance-monitor',
      url: 'https://your-app.com/webhooks/compliance',
      events: [
        'regulation.update',
        'compliance.alert',
        'filing.deadline',
        'tax.law.change'
      ],
      active: true,
      secret: 'your_webhook_secret_here'
    })
  });
  return await response.json();
};
```

#### Compliance Check Endpoint
```javascript
// Example: Check transaction compliance
const checkTransactionCompliance = async (transaction) => {
  const response = await fetch('/api/v1/tax/compliance/check', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`
    },
    body: JSON.stringify({
      transaction: transaction,
      jurisdiction: transaction.jurisdiction || 'US',
      check_types: [
        'AML',
        'TAX_EVASION',
        'SANCTIONS',
        'PEPS'
      ],
      risk_threshold: 'MEDIUM'
    })
  });
  return await response.json();
};
```

## Best Practices

### Request Handling
1. Always include proper error handling
2. Implement retry logic with exponential backoff
3. Cache responses when appropriate
4. Use proper content types in headers

### Security
1. Never expose API keys in client-side code
2. Rotate API keys regularly
3. Use the principle of least privilege for API keys
4. Monitor API usage for suspicious activity

### Performance
1. Use pagination for large datasets
2. Only request necessary fields
3. Implement client-side caching
4. Use webhooks instead of polling when possible

## Troubleshooting

### Common Issues

#### Authentication Failures
- Verify API key is correct
- Check key permissions
- Ensure the key hasn't expired

#### Rate Limiting
- Implement proper error handling
- Add delays between requests
- Consider batching requests

#### Data Validation Errors
- Review the API documentation
- Check required fields
- Validate data types and formats

### Getting Help
- API Documentation: [API_REFERENCE.md](API_REFERENCE.md)
- Support: integration-support@paksa.com
- Status Page: https://status.paksa.com
