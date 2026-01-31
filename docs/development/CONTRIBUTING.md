# Contributing Guidelines

## Code of Conduct
Be respectful, inclusive, and professional in all interactions.

## Getting Started
1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make your changes
5. Submit a pull request

## Development Standards

### Code Style

#### Python (Backend)
- Follow PEP 8
- Use Black for formatting
- Use isort for imports
- Maximum line length: 100 characters
- Use type hints

```python
def calculate_total(items: List[Item]) -> Decimal:
    """Calculate total amount from items."""
    return sum(item.amount for item in items)
```

#### TypeScript/Vue (Frontend)
- Follow Vue 3 Composition API style
- Use TypeScript for type safety
- Use Prettier for formatting
- Use ESLint for linting

```typescript
interface Invoice {
  id: string
  amount: number
  status: InvoiceStatus
}

const createInvoice = async (data: InvoiceCreate): Promise<Invoice> => {
  return await apiClient.post('/invoices', data)
}
```

### Testing Requirements

#### Backend
- Minimum 80% code coverage
- Unit tests for all services
- Integration tests for API endpoints
- Mock external dependencies

```python
def test_create_vendor(client):
    response = client.post('/api/ap/vendors', json={
        'vendor_name': 'Test Vendor',
        'email': 'test@vendor.com'
    })
    assert response.status_code == 200
    assert response.json()['vendor_name'] == 'Test Vendor'
```

#### Frontend
- Test critical components
- Test store logic
- E2E tests for user workflows

```typescript
it('should create invoice', async () => {
  const wrapper = mount(InvoiceForm)
  await wrapper.find('[data-testid="submit"]').trigger('click')
  expect(wrapper.emitted('created')).toBeTruthy()
})
```

### Documentation

#### Code Comments
- Document complex logic
- Explain "why" not "what"
- Keep comments up to date

#### Docstrings (Python)
```python
def process_payment(invoice_id: str, amount: Decimal) -> Payment:
    """
    Process payment for an invoice.
    
    Args:
        invoice_id: UUID of the invoice
        amount: Payment amount
        
    Returns:
        Payment object
        
    Raises:
        InvoiceNotFoundError: If invoice doesn't exist
        InsufficientFundsError: If amount exceeds invoice balance
    """
```

#### JSDoc (TypeScript)
```typescript
/**
 * Fetch customer by ID
 * @param id - Customer UUID
 * @returns Customer object
 * @throws {ApiError} If customer not found
 */
async function getCustomer(id: string): Promise<Customer> {
  // ...
}
```

## Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No console.log or debugger statements
- [ ] No commented-out code
- [ ] Commit messages are clear

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes
```

### Review Process
1. Automated checks must pass
2. At least one approval required
3. Address all review comments
4. Squash commits before merge

## Commit Messages

### Format
```
type(scope): subject

body (optional)

footer (optional)
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

### Examples
```
feat(ap): add vendor bulk import functionality

Implements CSV import for vendors with validation
and error reporting.

Closes #123
```

```
fix(ar): correct invoice total calculation

Fixed rounding error in tax calculation that caused
invoice totals to be off by 1 cent.

Fixes #456
```

## Branch Strategy

### Main Branches
- `main`: Production-ready code
- `develop`: Integration branch

### Feature Branches
- `feature/feature-name`
- `bugfix/bug-description`
- `hotfix/critical-fix`

### Workflow
1. Create branch from `develop`
2. Make changes
3. Create PR to `develop`
4. After approval, merge to `develop`
5. Periodically merge `develop` to `main`

## Code Review Guidelines

### As Author
- Keep PRs small and focused
- Provide context in description
- Respond to feedback promptly
- Be open to suggestions

### As Reviewer
- Review within 24 hours
- Be constructive and specific
- Ask questions, don't demand
- Approve when satisfied

### Review Checklist
- [ ] Code is readable and maintainable
- [ ] Logic is correct
- [ ] Tests are adequate
- [ ] No security issues
- [ ] Performance is acceptable
- [ ] Documentation is clear

## Security

### Reporting Vulnerabilities
Email security@paksa.com with:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices
- Never commit secrets
- Validate all inputs
- Use parameterized queries
- Implement rate limiting
- Keep dependencies updated
- Use HTTPS in production

## Performance

### Backend
- Use database indexes
- Implement caching
- Optimize queries
- Use async where appropriate
- Profile slow endpoints

### Frontend
- Lazy load components
- Optimize bundle size
- Minimize re-renders
- Use virtual scrolling for large lists
- Optimize images

## Questions?
- Check existing documentation
- Search closed issues
- Ask in team chat
- Email: dev@paksa.com