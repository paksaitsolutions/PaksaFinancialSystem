# Paksa Financial System API Documentation

## Introduction
Welcome to the Paksa Financial System API documentation. This API provides programmatic access to the comprehensive financial management capabilities of the Paksa Financial System.

## Authentication
All API requests require authentication using JWT (JSON Web Tokens). Include the token in the `Authorization` header:

```http
Authorization: Bearer your_jwt_token_here
```

## Base URL
All API endpoints are relative to the base URL:
```
https://api.paksa.com/v1
```

## Rate Limiting
- Standard: 1000 requests per minute
- Burst: 100 requests per second

## Response Format
All API responses follow a standard format:

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2025-08-19T12:00:00Z"
}
```

## Error Handling
Errors follow this format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  },
  "timestamp": "2025-08-19T12:00:00Z"
}
```

## Common Error Codes
- `400`: Bad Request - Invalid request parameters
- `401`: Unauthorized - Authentication required
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error - Server-side error

## Versioning
API versioning is handled through the URL path (e.g., `/v1/...`).

## Pagination
List responses are paginated. Example response:

```json
{
  "data": [],
  "pagination": {
    "total": 100,
    "count": 10,
    "per_page": 10,
    "current_page": 1,
    "total_pages": 10
  }
}
```

## Date/Time Format
All dates and times are in ISO 8601 format (UTC): `YYYY-MM-DDTHH:MM:SSZ`

## Data Types
- **Amounts**: Always in the smallest currency unit (e.g., cents for USD)
- **Currencies**: Follow ISO 4217 (e.g., USD, EUR, PKR)
- **Decimals**: Always use `.` as decimal separator

## Webhooks
For real-time updates, configure webhook endpoints in your account settings.

## Support
For API support, contact api-support@paksa.com
