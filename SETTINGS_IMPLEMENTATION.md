# Paksa Financial System - Settings Implementation

## Overview

This document describes the comprehensive settings implementation for the Paksa Financial System, accessible at `http://localhost:3003/settings/general`.

## Features Implemented

### 1. Company Information
- **Company Name** (Required) - Primary business name
- **Company Code** - Unique identifier for the company
- **Tax ID / EIN** - Tax identification number
- **Registration Number** - Business registration number
- **Company Address** - Complete business address

### 2. Financial Settings
- **Base Currency** (Required) - Primary currency for financial operations
- **Fiscal Year Start** (Required) - Starting month of fiscal year
- **Decimal Places** - Number of decimal places for currency (0-6)
- **Rounding Method** - How to handle rounding (round, ceil, floor, bankers)
- **Multi-Currency Support** - Enable/disable multi-currency functionality

### 3. Regional & Localization
- **Timezone** (Required) - System timezone
- **Default Language** - Interface language
- **Date Format** - How dates are displayed
- **Time Format** - 12-hour or 24-hour format
- **Number Format** - Regional number formatting
- **Week Start Day** - First day of the week

### 4. Document & Numbering
- **Invoice Number Prefix** - Prefix for invoice numbers
- **Invoice Start Number** - Starting number for invoices
- **Bill Number Prefix** - Prefix for bill numbers
- **Payment Number Prefix** - Prefix for payment numbers
- **Auto Numbering** - Enable automatic document numbering

### 5. System Preferences
- **Session Timeout** - User session timeout (5-480 minutes)
- **Default Page Size** - Items per page in lists (10-100)
- **Default Theme** - Light, dark, or auto theme
- **Backup Frequency** - How often to backup data
- **Audit Trail** - Enable/disable audit logging
- **Email Notifications** - Enable/disable email alerts
- **Two-Factor Authentication** - Require 2FA for users
- **Auto-Save** - Enable automatic saving

### 6. Integration & API
- **API Rate Limit** - Requests per minute (10-10000)
- **Webhook Timeout** - Timeout for webhooks (5-300 seconds)
- **API Logging** - Enable/disable API request logging
- **Webhook Retry** - Enable/disable webhook retry mechanism

## Technical Implementation

### Backend Components

#### 1. Database Model (`app/models/company_settings.py`)
```python
class CompanySettings(Base):
    # Company Information
    company_name = Column(String(255), nullable=False)
    company_code = Column(String(50), nullable=True)
    tax_id = Column(String(100), nullable=True)
    # ... additional fields
```

#### 2. API Schema (`app/schemas/company_settings.py`)
```python
class CompanySettingsBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    base_currency: str = Field(default='USD', regex=r'^[A-Z]{3}$')
    # ... validation rules
```

#### 3. API Endpoints (`app/api/endpoints/settings_enhanced.py`)
- `GET /company/{company_id}/settings` - Retrieve settings
- `POST /company/{company_id}/settings` - Create settings
- `PUT /company/{company_id}/settings` - Update settings
- `DELETE /company/{company_id}/settings` - Delete settings
- `GET /settings/defaults` - Get default options

#### 4. Database Migration (`app/alembic/versions/20250124_02_enhanced_company_settings.py`)
Adds all new columns to the `company_settings` table with proper defaults.

### Frontend Components

#### 1. Settings Service (`src/services/settingsService.ts`)
```typescript
class SettingsService {
  async getCompanySettings(companyId: number): Promise<CompanySettings>
  async updateCompanySettings(companyId: number, settings: Partial<CompanySettings>): Promise<CompanySettings>
  validateSettings(settings: Partial<CompanySettings>): string[]
}
```

#### 2. General Settings Component (`src/modules/settings/views/GeneralSettings.vue`)
- Comprehensive form with all settings categories
- Real-time validation
- Professional UI with PrimeVue components
- Responsive design for mobile devices

#### 3. Settings Layout (`src/modules/settings/views/SettingsView.vue`)
- Navigation between different settings sections
- Router-based navigation
- Consistent layout and styling

## Usage Instructions

### 1. Starting the Application
```bash
# Using the provided PowerShell script
.\start-dev.ps1

# Or manually:
# Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run dev
```

### 2. Accessing Settings
1. Navigate to `http://localhost:3003`
2. Login to the system
3. Go to Settings → General
4. Or directly access: `http://localhost:3003/settings/general`

### 3. Configuring Settings
1. Fill in company information
2. Set financial preferences
3. Configure regional settings
4. Customize document numbering
5. Adjust system preferences
6. Configure integration settings
7. Click "Save All Changes"

## Validation Rules

### Required Fields
- Company Name
- Base Currency
- Fiscal Year Start
- Timezone

### Field Constraints
- Company Name: 1-255 characters
- Currency Code: 3-letter ISO code
- Decimal Places: 0-6
- Session Timeout: 5-480 minutes
- Page Size: 10-100 items
- API Rate Limit: 10-10000 requests/minute
- Webhook Timeout: 5-300 seconds

## Default Values

The system provides sensible defaults for all settings:
- Company Name: "Paksa Financial System"
- Base Currency: USD
- Fiscal Year: January
- Timezone: UTC
- Language: English
- Theme: Light
- Session Timeout: 60 minutes

## Security Features

1. **Input Validation** - All inputs are validated on both client and server
2. **SQL Injection Prevention** - Using SQLAlchemy ORM
3. **XSS Protection** - Input sanitization
4. **Authentication Required** - All endpoints require valid JWT token
5. **Audit Trail** - All changes are logged when enabled

## Error Handling

1. **Client-side Validation** - Immediate feedback for invalid inputs
2. **Server-side Validation** - Comprehensive validation with detailed error messages
3. **Network Error Handling** - Graceful handling of connection issues
4. **User Feedback** - Toast notifications for all operations

## Mobile Responsiveness

The settings interface is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- Different screen orientations

## Future Enhancements

1. **Import/Export Settings** - Backup and restore configurations
2. **Settings Templates** - Pre-configured settings for different industries
3. **Advanced Validation** - Custom validation rules
4. **Settings History** - Track changes over time
5. **Bulk Operations** - Update multiple settings at once
6. **Settings API** - RESTful API for external integrations

## Troubleshooting

### Common Issues

1. **Settings Not Saving**
   - Check network connection
   - Verify authentication token
   - Check browser console for errors

2. **Validation Errors**
   - Ensure all required fields are filled
   - Check field format requirements
   - Verify value ranges

3. **UI Not Loading**
   - Clear browser cache
   - Check if backend is running
   - Verify API endpoints are accessible

### Support

For technical support or questions about the settings implementation, please refer to the main project documentation or contact the development team.