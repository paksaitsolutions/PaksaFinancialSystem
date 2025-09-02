# Paksa Financial System - Multi-Tenant Architecture

## Overview

The Paksa Financial System is designed as a comprehensive multi-tenant SaaS platform where each company operates as a separate entity with its own data, settings, branding, and configuration. This document describes the complete multi-tenant implementation.

## Key Features

### 1. Company Registration & Management
- **Super Admin Registration**: Super admins can register new companies
- **Company Activation**: Switch between companies with complete context switching
- **Company Branding**: Each company has its own logo, colors, and branding
- **Subscription Management**: Different plans with varying features and limits

### 2. Complete Data Isolation
- **Database Level**: Each company's data is completely isolated
- **User Management**: Users belong to specific companies
- **Settings Isolation**: Each company has independent settings
- **Module Configuration**: Companies can enable/disable specific modules

### 3. Dynamic Branding & Theming
- **Logo Integration**: Company logos appear throughout the system
- **Color Schemes**: Primary and secondary colors applied system-wide
- **Custom Domains**: Each company gets a subdomain (company.paksa.com)
- **Personalized Experience**: System adapts to company preferences

## Architecture Components

### Backend Components

#### 1. Database Models

**TenantCompany Model** (`app/models/tenant_company.py`)
```python
class TenantCompany(Base):
    # Company Information
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    industry = Column(String(100), nullable=True)
    
    # Branding & Customization
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), nullable=True)
    
    # Subscription & Limits
    plan = Column(String(50), nullable=False)
    max_users = Column(Integer, nullable=False)
    
    # Configuration
    enabled_modules = Column(JSON, nullable=True)
    feature_flags = Column(JSON, nullable=True)
```

**Supporting Models:**
- `CompanyAdmin`: Manages admin relationships
- `CompanyModule`: Controls module access per company
- `CompanySubscription`: Handles billing and subscriptions

#### 2. API Endpoints (`app/api/endpoints/tenant_company.py`)

**Core Endpoints:**
- `GET /companies` - List all companies with filtering
- `POST /companies` - Register new company with admin user
- `PUT /companies/{id}` - Update company information
- `POST /companies/{id}/activate` - Activate company context
- `DELETE /companies/{id}` - Soft delete company

**Management Endpoints:**
- `GET /companies/stats` - Company statistics
- `POST /companies/{id}/logo` - Upload company logo
- `GET /companies/{id}/modules` - Get company modules

#### 3. Business Logic (`app/services/tenant_service.py`)

**Key Services:**
- Company validation and access control
- Branding and customization management
- Subscription and limits checking
- Module enablement/disablement
- Analytics and reporting

### Frontend Components

#### 1. Tenant Management Interface

**Location**: `src/modules/tenant/views/TenantManagement.vue`

**Features:**
- Company registration form with comprehensive fields
- Company listing with search and filtering
- Company activation and switching
- Real-time branding application
- Company statistics dashboard

**Key Sections:**
- **Company Information**: Name, code, industry, address
- **Subscription & Configuration**: Plan selection, user limits
- **Branding & Customization**: Logo upload, color selection
- **Administrator Account**: Initial admin user setup

#### 2. Frontend Service (`src/services/tenantService.ts`)

**Capabilities:**
- Complete API integration
- Client-side validation
- Branding application utilities
- Company context management
- Local storage persistence

## Multi-Tenant Features

### 1. Company Registration Process

**Step 1: Company Information**
```typescript
{
  name: "Acme Corporation",
  code: "ACME001", 
  industry: "Manufacturing",
  size: "Large",
  address: "123 Business St, City, State"
}
```

**Step 2: Subscription & Configuration**
```typescript
{
  plan: "Professional",
  max_users: 50,
  subdomain: "acme",
  timezone: "America/New_York"
}
```

**Step 3: Branding & Customization**
```typescript
{
  logo_url: "/uploads/logos/acme-logo.png",
  primary_color: "#FF5722",
  secondary_color: "#FFC107"
}
```

**Step 4: Administrator Account**
```typescript
{
  admin_name: "John Smith",
  admin_email: "admin@acme.com",
  admin_password: "SecurePassword123",
  admin_phone: "+1-555-123-4567"
}
```

### 2. Company Activation & Context Switching

When a company is activated:

1. **Authentication Token Update**: New JWT token with company context
2. **Branding Application**: Logo, colors, and theme applied
3. **Module Configuration**: Available modules loaded
4. **Settings Context**: Company-specific settings loaded
5. **User Interface Update**: Navigation and features adjusted

### 3. Dynamic Branding System

**CSS Variable Updates:**
```javascript
document.documentElement.style.setProperty('--primary-color', company.primary_color)
```

**Logo Integration:**
```javascript
// Update favicon
const favicon = document.querySelector('link[rel="icon"]')
favicon.href = company.logo_url

// Update page title
document.title = `${company.name} - Financial System`
```

**Context Persistence:**
```javascript
localStorage.setItem('activeCompany', JSON.stringify(companyContext))
```

## Subscription Plans & Features

### Basic Plan ($29/month)
- Up to 10 users
- 5GB storage
- Core modules: GL, AP, AR
- Email support
- Standard reports

### Professional Plan ($79/month)
- Up to 50 users
- 25GB storage
- All basic modules + Payroll, Inventory
- Priority support
- Advanced reports
- API access

### Enterprise Plan ($199/month)
- Up to 200 users
- 100GB storage
- All modules included
- 24/7 phone support
- Custom reports
- Advanced API access
- Custom integrations

### Custom Plan (Contact Sales)
- Unlimited users
- Custom storage
- Custom development
- White-label options
- On-premise deployment

## Security & Access Control

### 1. Data Isolation
- **Row-Level Security**: All queries filtered by company_id
- **API Middleware**: Automatic company context validation
- **User Permissions**: Role-based access within companies

### 2. Authentication & Authorization
- **JWT Tokens**: Include company context
- **Multi-Company Access**: Users can belong to multiple companies
- **Role Management**: Company-specific roles and permissions

### 3. Audit & Compliance
- **Activity Logging**: All actions logged per company
- **Data Retention**: Company-specific retention policies
- **Backup & Recovery**: Isolated backup strategies

## Usage Instructions

### 1. Accessing Company Management

**URL**: `http://localhost:3003/settings/tenant`

**Navigation**: Settings → Tenant Management

### 2. Registering a New Company

1. Click "Register New Company"
2. Fill in company information
3. Select subscription plan
4. Configure branding options
5. Set up administrator account
6. Submit registration

### 3. Switching Between Companies

1. Click "Company Selector"
2. Choose desired company from list
3. System automatically switches context
4. Branding and settings update immediately

### 4. Managing Company Settings

1. Select company from list
2. Click "Company Settings" action
3. Modify configuration as needed
4. Save changes

## API Integration Examples

### Register New Company
```javascript
const companyData = {
  name: "Tech Solutions Inc",
  code: "TECH001",
  subdomain: "techsol",
  plan: "Professional",
  admin_name: "Jane Doe",
  admin_email: "admin@techsol.com",
  admin_password: "SecurePass123"
}

const company = await tenantService.registerCompany(companyData)
```

### Activate Company
```javascript
const response = await tenantService.activateCompany(companyId)
// New token automatically stored
// Branding automatically applied
```

### Upload Company Logo
```javascript
const logoFile = document.getElementById('logoInput').files[0]
const result = await tenantService.uploadCompanyLogo(companyId, logoFile)
```

## Database Schema

### Core Tables

**tenant_companies**
- Company master data
- Branding configuration
- Subscription information
- Feature flags

**company_admins**
- User-company relationships
- Role assignments
- Permission matrices

**company_modules**
- Module enablement per company
- License tracking
- Configuration storage

**company_subscriptions**
- Billing information
- Payment tracking
- Subscription lifecycle

## Development Guidelines

### 1. Adding New Features

When adding company-specific features:

1. **Database**: Add company_id foreign key
2. **API**: Include company context validation
3. **Frontend**: Check company permissions
4. **Testing**: Test with multiple companies

### 2. Branding Integration

For new UI components:

1. **Use CSS Variables**: Reference `--primary-color`
2. **Logo Placement**: Use company logo where appropriate
3. **Theme Consistency**: Follow company color scheme
4. **Responsive Design**: Ensure branding works on all devices

### 3. Module Development

When creating new modules:

1. **Registration**: Add to available modules list
2. **Permissions**: Define company-level permissions
3. **Configuration**: Allow company-specific settings
4. **Licensing**: Support different license types

## Troubleshooting

### Common Issues

1. **Company Not Switching**
   - Check authentication token
   - Verify company access permissions
   - Clear browser cache

2. **Branding Not Applied**
   - Verify logo URL accessibility
   - Check CSS variable updates
   - Confirm color format (hex)

3. **Module Access Denied**
   - Check company module enablement
   - Verify user permissions
   - Confirm subscription plan includes module

### Support & Maintenance

1. **Monitoring**: Track company usage and performance
2. **Backups**: Implement company-specific backup strategies
3. **Updates**: Test changes across multiple company contexts
4. **Scaling**: Monitor resource usage per company

## Future Enhancements

### Planned Features

1. **White-Label Options**: Complete branding customization
2. **Custom Domains**: company.com instead of company.paksa.com
3. **Advanced Analytics**: Company performance metrics
4. **Marketplace**: Third-party module integration
5. **Mobile Apps**: Company-branded mobile applications

### Technical Improvements

1. **Microservices**: Split into company-specific services
2. **Caching**: Company-specific cache strategies
3. **CDN Integration**: Optimized asset delivery
4. **Real-time Updates**: WebSocket-based company switching
5. **Advanced Security**: Enhanced isolation and encryption

This multi-tenant architecture provides a robust foundation for scaling the Paksa Financial System to serve multiple companies while maintaining complete data isolation, customization, and security.