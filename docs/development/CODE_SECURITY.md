# Code Security & Quality Guidelines

## Copyright & Ownership

### Copyright Header
All code files must include:
```python
"""
Copyright (c) 2024 Paksa IT Solutions
All rights reserved.

Project: Paksa Financial System
Website: https://paksa.com
"""
```

### Branding Requirements
- Company name: **Paksa IT Solutions**
- Product name: **Paksa Financial System**
- All API responses include `X-Powered-By: Paksa Financial System`
- All documentation references Paksa IT Solutions

## Git Workflow Security

### Branch Protection
- **main**: Production only, no direct commits
- **develop**: Integration branch, requires PR
- **feature/***: Feature development
- **bugfix/***: Bug fixes
- **hotfix/***: Critical production fixes

### Commit Requirements
- Descriptive commit messages
- Reference issue numbers
- Sign commits (GPG recommended)
- Run pre-commit hooks

### Pre-commit Checks
```bash
# Install hooks
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Checks performed:
- Branch name validation
- Code formatting (Black, ESLint)
- Linting (flake8, ESLint)
- Paksa attribution in new files

## Code Quality Standards

### Backend (Python)

#### Type Hints Required
```python
def calculate_total(items: List[Item]) -> Decimal:
    """Calculate total from items."""
    return sum(item.amount for item in items)
```

#### Docstrings Required
```python
def process_payment(invoice_id: str, amount: Decimal) -> Payment:
    """
    Process payment for invoice.
    
    Args:
        invoice_id: Invoice UUID
        amount: Payment amount
        
    Returns:
        Payment object
        
    Raises:
        InvoiceNotFoundError: If invoice doesn't exist
    """
```

#### No Duplicate Code
- Extract common logic to utilities
- Use inheritance for shared behavior
- Create reusable services

### Frontend (TypeScript/Vue)

#### Type Definitions Required
```typescript
interface Invoice {
  id: string
  amount: number
  status: InvoiceStatus
}
```

#### Component Documentation
```vue
<script setup lang="ts">
/**
 * Invoice List Component
 * Displays paginated list of invoices with filters
 * 
 * @component
 * @example
 * <InvoiceList :customer-id="customerId" />
 */
</script>
```

## Refactoring Checklist

### Remove Duplicates
- [ ] Identify duplicate functions
- [ ] Extract to shared utilities
- [ ] Update imports
- [ ] Test thoroughly

### Add Type Hints
- [ ] All function parameters
- [ ] All return types
- [ ] Class attributes
- [ ] Variable annotations

### Complete Docstrings
- [ ] All public functions
- [ ] All classes
- [ ] Complex logic blocks
- [ ] API endpoints

### Remove Dead Code
- [ ] Unused imports
- [ ] Commented code
- [ ] Unused functions
- [ ] Deprecated features

## Security Measures

### Code Protection
- Copyright headers on all files
- Paksa branding in responses
- License file in repository
- Attribution requirements

### Repository Security
- Branch protection rules
- Required code reviews
- Automated testing
- Security scanning

### Deployment Security
- Environment variables for secrets
- No hardcoded credentials
- SSL/TLS required
- Rate limiting enabled

## Running Quality Checks

### Backend
```bash
cd backend

# Add copyright headers
python add_copyright.py

# Run refactoring analysis
python refactor_code.py

# Format code
black .
isort .

# Lint
flake8 .

# Type check
mypy app/
```

### Frontend
```bash
cd frontend

# Lint
npm run lint

# Format
npm run format

# Type check
npm run type-check
```

## Continuous Integration

### GitHub Actions
- Run on all PRs
- Check code quality
- Run tests
- Verify attribution

### Required Checks
- All tests pass
- Code coverage maintained
- No linting errors
- Copyright headers present

## Intellectual Property

### Ownership
All code is property of **Paksa IT Solutions**

### License
MIT License with attribution requirement

### Usage
- Commercial use allowed with attribution
- Modifications allowed with attribution
- Distribution allowed with attribution
- Private use allowed

### Attribution Format
```
Powered by Paksa Financial System
Copyright (c) 2024 Paksa IT Solutions
https://paksa.com
```