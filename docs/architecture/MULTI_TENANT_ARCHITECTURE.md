# Multi-Company, Multi-User, Multi-Role System Architecture

## Current Status
The system is currently set up with basic user authentication but needs database schema updates to support full multi-tenancy.

## Required Database Schema Changes

### 1. Add Company/Role Columns to Users Table
```sql
ALTER TABLE users ADD COLUMN company_id UUID REFERENCES companies(id);
ALTER TABLE users ADD COLUMN role_id UUID REFERENCES roles(id);
```

### 2. Create User-Company-Role Relationships
```python
# In User model (after schema update):
company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
company = relationship("Company")
role = relationship("Role")
```

## Authentication Flow

### 1. User Login
```python
# User authenticates with email/password
user = User.authenticate(db, email, password)

# JWT token contains user_id
token = create_access_token(data={"sub": str(user.id)})
```

### 2. Request Processing
```python
# Every API request includes JWT token
# AuthContext extracts user, company, and role information
auth = get_auth_context(token)

# All data queries automatically filtered by company
invoices = db.query(APInvoice).filter(
    APInvoice.company_id == auth.company_id
).all()
```

### 3. Permission Checking
```python
# Role-based permissions
@router.post("/invoices")
async def create_invoice(
    auth: AuthContext = Depends(require_permission("create_invoice"))
):
    # Only users with 'create_invoice' permission can access
    pass

# Company-level data isolation
invoice.company_id = auth.company_id  # Auto-set from user context
```

## Data Isolation Strategy

### 1. Company-Level Isolation
- All financial data (invoices, payments, accounts) include `company_id`
- Queries automatically filtered by user's company
- No cross-company data access (except for superusers)

### 2. Role-Based Access Control
- Users assigned to roles (Admin, Accountant, Viewer, etc.)
- Roles have specific permissions (create_invoice, view_reports, etc.)
- API endpoints check permissions before allowing access

### 3. User Context Injection
```python
# Every API endpoint gets user context
async def get_invoices(auth: AuthContext = Depends(get_auth_context)):
    # auth.company_id - User's company
    # auth.user_id - Current user
    # auth.role_name - User's role
    # auth.has_permission("view_invoices") - Permission check
```

## Implementation Examples

### 1. Multi-Company Data Access
```python
# Automatic company filtering
@router.get("/customers")
async def get_customers(auth: AuthContext = Depends(get_auth_context)):
    customers = db.query(Customer).filter(
        Customer.company_id == auth.company_id
    ).all()
    return customers
```

### 2. Role-Based Permissions
```python
# Permission-based access
@router.delete("/invoices/{invoice_id}")
async def delete_invoice(
    invoice_id: str,
    auth: AuthContext = Depends(require_permission("delete_invoice"))
):
    # Only users with delete permission can access
    pass
```

### 3. Superuser Access
```python
# Cross-company access for superusers
@router.get("/admin/all-companies")
async def get_all_companies(
    auth: AuthContext = Depends(require_superuser())
):
    # Only superusers can see all companies
    companies = db.query(Company).all()
    return companies
```

## Current Implementation Status

✅ **Completed:**
- Basic user authentication
- JWT token system
- User model with superuser support
- Role and Permission models
- AuthContext framework

❌ **Pending (requires database migration):**
- Company-User relationships
- Role-User relationships
- Automatic company filtering
- Permission-based access control

## Next Steps

1. **Database Migration**: Add company_id and role_id to users table
2. **Update Models**: Add relationships between User, Company, and Role
3. **Implement Filtering**: Add company_id filters to all financial queries
4. **Permission System**: Implement role-based permission checking
5. **Frontend Updates**: Add company/role context to UI components

## Security Considerations

- All API endpoints must include authentication
- Data queries must be filtered by company_id
- Sensitive operations require specific permissions
- Audit trail should track user actions across companies
- Cross-company data access only for superusers