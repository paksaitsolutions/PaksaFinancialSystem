# Paksa Financial System - Development Best Practices

## 🚀 Git Workflow Best Practices

### Safe Git Operations
```bash
# Always check status before operations
git status

# Pull latest changes safely
git pull origin master

# Stage changes selectively
git add -A  # Add all changes
git add .   # Add current directory changes
git add specific-file.py  # Add specific files

# Commit with meaningful messages
git commit -m "Feature: Add AR predictive analytics with ML integration"

# Push changes safely
git push origin master
```

### Commit Message Standards
```
Format: Type: Brief description

Types:
- Feature: New functionality
- Fix: Bug fixes
- Enhance: Improvements to existing features
- Refactor: Code restructuring
- Docs: Documentation updates
- Test: Testing additions
- Config: Configuration changes

Examples:
- "Feature: Add multi-dimensional GL chart of accounts"
- "Enhance: Improve AR payment prediction accuracy"
- "Fix: Resolve journal entry balance validation"
```

### Branch Management
```bash
# Create feature branch
git checkout -b feature/cash-management

# Switch between branches
git checkout master
git checkout feature/cash-management

# Merge feature branch
git checkout master
git merge feature/cash-management

# Delete merged branch
git branch -d feature/cash-management
```

## 🏗️ Code Architecture Best Practices

### Backend Structure
```
backend/
├── app/
│   ├── modules/
│   │   ├── core_financials/
│   │   │   ├── general_ledger/
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── services.py
│   │   │   │   ├── crud.py
│   │   │   │   └── routes.py
│   │   │   ├── accounts_payable/
│   │   │   └── accounts_receivable/
│   │   ├── cross_cutting/
│   │   └── extended/
│   ├── api/
│   ├── core/
│   └── utils/
```

### Frontend Structure
```
frontend/
├── src/
│   ├── views/
│   │   ├── gl/
│   │   ├── ap/
│   │   └── ar/
│   ├── components/
│   │   ├── common/
│   │   ├── forms/
│   │   └── charts/
│   ├── services/
│   ├── stores/
│   ├── types/
│   └── utils/
```

### Service Layer Pattern
```python
# services.py
class GLService:
    def __init__(self, db: Session):
        self.db = db
        self.crud = GLAccountCRUD(db)
    
    def create_account(self, account_data: AccountCreate) -> Account:
        # Business logic here
        return self.crud.create(account_data)
```

### Vue 3 Composition API
```typescript
// Component structure
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Reactive state
const accounts = ref<Account[]>([])
const loading = ref(false)

// Computed properties
const totalBalance = computed(() => 
  accounts.value.reduce((sum, acc) => sum + acc.balance, 0)
)

// Methods
const loadAccounts = async () => {
  loading.value = true
  try {
    accounts.value = await accountService.getAll()
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  loadAccounts()
})
</script>
```

## 🔒 Security Best Practices

### Authentication & Authorization
```python
# JWT token validation
from fastapi import Depends, HTTPException
from app.core.auth import get_current_user

@router.get("/accounts")
async def get_accounts(
    current_user: User = Depends(get_current_user)
):
    # Verify permissions
    if not current_user.has_permission("gl.accounts.read"):
        raise HTTPException(403, "Insufficient permissions")
```

### Input Validation
```python
# Pydantic schemas for validation
class AccountCreate(BaseModel):
    account_code: str = Field(..., regex=r'^[0-9]{4,6}$')
    account_name: str = Field(..., min_length=1, max_length=255)
    account_type: AccountType
    
    @validator('account_code')
    def validate_unique_code(cls, v):
        # Custom validation logic
        return v
```

### SQL Injection Prevention
```python
# Use SQLAlchemy ORM, avoid raw SQL
query = session.query(Account).filter(
    Account.account_code == account_code
)

# If raw SQL needed, use parameters
session.execute(
    text("SELECT * FROM accounts WHERE code = :code"),
    {"code": account_code}
)
```

## 📊 Database Best Practices

### Model Design
```python
class GLAccount(Base):
    __tablename__ = "gl_accounts"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Business key with unique constraint
    account_code = Column(String(20), unique=True, nullable=False, index=True)
    
    # Required fields
    account_name = Column(String(255), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_account_type_active', 'account_type', 'is_active'),
    )
```

### Migration Best Practices
```python
# Alembic migration
def upgrade():
    # Add new columns with defaults
    op.add_column('gl_accounts', 
        sa.Column('department_required', sa.Boolean(), default=False)
    )
    
    # Update existing data
    op.execute("UPDATE gl_accounts SET department_required = false")
    
    # Add constraints after data update
    op.alter_column('gl_accounts', 'department_required', nullable=False)
```

## 🎨 Frontend Best Practices

### Component Design
```vue
<template>
  <div class="account-form">
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="account-code">Account Code *</label>
        <input 
          id="account-code"
          v-model="form.account_code"
          :class="{ 'error': errors.account_code }"
          required
        >
        <span v-if="errors.account_code" class="error-text">
          {{ errors.account_code }}
        </span>
      </div>
    </form>
  </div>
</template>
```

### State Management
```typescript
// Pinia store
export const useAccountStore = defineStore('accounts', () => {
  const accounts = ref<Account[]>([])
  const loading = ref(false)
  
  const getAccounts = async () => {
    loading.value = true
    try {
      const response = await accountService.getAll()
      accounts.value = response.data
    } catch (error) {
      console.error('Failed to load accounts:', error)
    } finally {
      loading.value = false
    }
  }
  
  return { accounts, loading, getAccounts }
})
```

### Error Handling
```typescript
// Global error handler
const handleApiError = (error: any) => {
  if (error.response?.status === 401) {
    router.push('/login')
  } else if (error.response?.status === 403) {
    showNotification('Access denied', 'error')
  } else {
    showNotification('An error occurred', 'error')
  }
}
```

## 🧪 Testing Best Practices

### Backend Testing
```python
# pytest fixtures
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = SessionLocal()
    yield session
    session.close()

# Test service methods
def test_create_account(db_session):
    service = GLService(db_session)
    account_data = AccountCreate(
        account_code="1000",
        account_name="Cash",
        account_type=AccountType.ASSET
    )
    
    account = service.create_account(account_data)
    assert account.account_code == "1000"
    assert account.account_name == "Cash"
```

### Frontend Testing
```typescript
// Vue Test Utils
import { mount } from '@vue/test-utils'
import AccountForm from '@/components/AccountForm.vue'

describe('AccountForm', () => {
  it('validates required fields', async () => {
    const wrapper = mount(AccountForm)
    
    await wrapper.find('form').trigger('submit')
    
    expect(wrapper.find('.error-text').exists()).toBe(true)
  })
})
```

## 🚀 Performance Best Practices

### Database Optimization
```python
# Use indexes for frequent queries
class GLAccount(Base):
    __table_args__ = (
        Index('idx_account_code', 'account_code'),
        Index('idx_account_type_active', 'account_type', 'is_active'),
    )

# Eager loading for relationships
accounts = session.query(GLAccount).options(
    joinedload(GLAccount.journal_entries)
).all()

# Pagination for large datasets
def get_accounts_paginated(skip: int = 0, limit: int = 100):
    return session.query(GLAccount).offset(skip).limit(limit).all()
```

### Frontend Optimization
```typescript
// Lazy loading components
const AccountForm = defineAsyncComponent(() => import('./AccountForm.vue'))

// Debounced search
import { debounce } from '@/utils/debounce'

const searchAccounts = debounce(async (query: string) => {
  // Search implementation
}, 300)

// Virtual scrolling for large lists
<template>
  <virtual-list
    :data-sources="accounts"
    :data-key="'id'"
    :keeps="50"
  >
    <template #item="{ record }">
      <AccountItem :account="record" />
    </template>
  </virtual-list>
</template>
```

## 📝 Documentation Standards

### Code Documentation
```python
def create_journal_entry(
    self, 
    entry_data: JournalEntryCreate
) -> JournalEntry:
    """
    Create a new journal entry with validation and posting.
    
    Args:
        entry_data: Journal entry data including lines and metadata
        
    Returns:
        Created journal entry with generated entry number
        
    Raises:
        ValueError: If entry is not balanced or validation fails
        PermissionError: If user lacks posting permissions
    """
```

### API Documentation
```python
@router.post("/accounts", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new GL account.
    
    - **account_code**: Unique 4-6 digit account code
    - **account_name**: Descriptive account name
    - **account_type**: Asset, Liability, Equity, Revenue, or Expense
    """
```

## 🔧 Development Environment

### Local Setup
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install
npm run dev

# Database setup
docker-compose up -d postgres
alembic upgrade head
```

### Environment Variables
```bash
# .env file
DATABASE_URL=postgresql://user:pass@localhost/paksa_financial
SECRET_KEY=your-secret-key
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
```

## 🚨 Error Handling

### Backend Error Handling
```python
from fastapi import HTTPException

class GLService:
    def create_account(self, account_data: AccountCreate) -> Account:
        try:
            # Validate business rules
            if self.account_exists(account_data.account_code):
                raise HTTPException(400, "Account code already exists")
            
            return self.crud.create(account_data)
        except IntegrityError:
            raise HTTPException(400, "Database constraint violation")
        except Exception as e:
            logger.error(f"Failed to create account: {e}")
            raise HTTPException(500, "Internal server error")
```

### Frontend Error Handling
```typescript
const createAccount = async (accountData: AccountCreate) => {
  try {
    const response = await accountService.create(accountData)
    showNotification('Account created successfully', 'success')
    return response.data
  } catch (error: any) {
    if (error.response?.status === 400) {
      showNotification(error.response.data.detail, 'error')
    } else {
      showNotification('Failed to create account', 'error')
    }
    throw error
  }
}
```

## 📊 Monitoring & Logging

### Application Logging
```python
import logging

logger = logging.getLogger(__name__)

class GLService:
    def create_account(self, account_data: AccountCreate) -> Account:
        logger.info(f"Creating account: {account_data.account_code}")
        
        try:
            account = self.crud.create(account_data)
            logger.info(f"Account created successfully: {account.id}")
            return account
        except Exception as e:
            logger.error(f"Failed to create account: {e}", exc_info=True)
            raise
```

### Performance Monitoring
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        if execution_time > 1.0:  # Log slow operations
            logger.warning(f"Slow operation: {func.__name__} took {execution_time:.2f}s")
        
        return result
    return wrapper
```

---

## 🎯 Key Takeaways

1. **Always pull before pushing** to avoid conflicts
2. **Use meaningful commit messages** for better tracking
3. **Follow consistent code structure** across modules
4. **Implement proper error handling** at all levels
5. **Write tests** for critical business logic
6. **Document complex functions** and APIs
7. **Use type hints** for better code maintainability
8. **Optimize database queries** with proper indexing
9. **Handle security** with proper validation and authentication
10. **Monitor performance** and log important operations

These best practices ensure maintainable, scalable, and robust financial software development.