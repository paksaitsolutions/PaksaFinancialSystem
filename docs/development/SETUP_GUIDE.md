# Developer Setup Guide

## Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 13+ (or SQLite for development)
- Git
- VS Code (recommended)

## Initial Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/paksa-financial-system.git
cd paksa-financial-system
```

### 2. Backend Setup

#### Create Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

#### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Environment Configuration
```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=sqlite:///./paksa.db
SECRET_KEY=your-secret-key-here
FIRST_SUPERUSER_EMAIL=admin@paksa.com
FIRST_SUPERUSER_PASSWORD=admin123
```

#### Initialize Database
```bash
python -m app.core.db.unified_init --mode development --sample-data
```

#### Run Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access API docs: `http://localhost:8000/docs`

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Environment Configuration
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

#### Run Frontend
```bash
npm run dev
```

Access app: `http://localhost:3003`

## Development Workflow

### Code Style

#### Backend
```bash
# Format code
black .
isort .

# Lint
flake8 .
```

#### Frontend
```bash
# Format
npm run format

# Lint
npm run lint
```

### Testing

#### Backend Tests
```bash
cd backend
pytest                    # Run all tests
pytest tests/test_ap_module.py  # Run specific test
pytest --cov             # With coverage
```

#### Frontend Tests
```bash
cd frontend
npm run test             # Unit tests
npm run test:coverage    # With coverage
npm run e2e              # E2E tests
```

### Database Migrations

#### Create Migration
```bash
alembic revision --autogenerate -m "Description"
```

#### Apply Migrations
```bash
alembic upgrade head
```

#### Rollback
```bash
alembic downgrade -1
```

## Project Structure

### Backend
```
backend/
├── app/
│   ├── api/              # API routes
│   ├── core/             # Core functionality
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── main.py           # Application entry
├── tests/                # Test files
└── requirements.txt      # Dependencies
```

### Frontend
```
frontend/
├── src/
│   ├── api/              # API services
│   ├── components/       # Vue components
│   ├── composables/      # Vue composables
│   ├── modules/          # Feature modules
│   ├── stores/           # Pinia stores
│   ├── types/            # TypeScript types
│   └── utils/            # Utilities
├── e2e/                  # E2E tests
└── package.json          # Dependencies
```

## Common Issues

### Backend Won't Start
**Problem**: `ModuleNotFoundError`
**Solution**: Ensure virtual environment is activated and dependencies installed

### Database Errors
**Problem**: Migration conflicts
**Solution**: 
```bash
alembic downgrade base
alembic upgrade head
```

### Frontend Build Errors
**Problem**: Node modules issues
**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

## IDE Configuration

### VS Code Extensions
- Python
- Pylance
- Vue Language Features (Volar)
- ESLint
- Prettier

### Recommended Settings
```json
{
  "editor.formatOnSave": true,
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

## Git Workflow

### Branch Naming
- `feature/feature-name`
- `bugfix/bug-description`
- `hotfix/critical-fix`

### Commit Messages
```
type(scope): description

feat(ap): add vendor bulk import
fix(ar): resolve invoice calculation bug
docs(api): update authentication guide
```

### Pull Request Process
1. Create feature branch
2. Make changes and commit
3. Write/update tests
4. Run linters and tests
5. Push and create PR
6. Request review
7. Address feedback
8. Merge after approval

## Debugging

### Backend
```python
import pdb; pdb.set_trace()  # Add breakpoint
```

### Frontend
```javascript
debugger;  // Add breakpoint
```

Use VS Code debugger for better experience.

## Performance Tips
- Use database indexes for frequent queries
- Implement caching for expensive operations
- Lazy load frontend components
- Use pagination for large datasets
- Profile code to identify bottlenecks

## Security Best Practices
- Never commit secrets
- Use environment variables
- Validate all inputs
- Implement rate limiting
- Keep dependencies updated
- Use HTTPS in production

## Getting Help
- Check documentation in `docs/`
- Review existing issues on GitHub
- Ask in team Slack channel
- Contact: dev@paksa.com