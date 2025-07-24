# Backend Refactoring: Migration Guide

## New Directory Structure

```
app/
├── core/                  # Core application functionality
│   ├── config/           # Configuration
│   ├── db/               # Database models and sessions
│   ├── security/         # Authentication and authorization
│   └── utils/            # Common utilities
│
├── api/                  # API endpoints
│   ├── v1/               # API version 1
│   │   ├── endpoints/    # Route handlers
│   │   └── deps.py       # Dependencies
│   └── deps.py           # Common dependencies
│
├── models/               # SQLAlchemy models
├── schemas/              # Pydantic models
├── crud/                 # Database operations
├── services/             # Business logic
└── tests/                # Test files
```

## Migration Steps

### 1. File Migration

1. **Core Functionality**
   - Move database configuration to `core/config/`
   - Move database session management to `core/db/`
   - Move authentication/security to `core/security/`
   - Move utilities to `core/utils/`

2. **API Layer**
   - Move API routes to `api/v1/endpoints/`
   - Move API dependencies to `api/deps.py` and `api/v1/deps.py`

3. **Data Layer**
   - Move SQLAlchemy models to `models/`
   - Move Pydantic schemas to `schemas/`
   - Move CRUD operations to `crud/`
   - Move business logic to `services/`

### 2. Update Imports

Update all import statements to reflect the new structure. For example:

- `from app.modules.core.database import SessionLocal` → `from app.core.db.session import SessionLocal`
- `from app.modules.core.security import get_current_user` → `from app.core.security.auth import get_current_user`

### 3. Update Tests

Update test files to use the new import paths and directory structure.

## Verification

1. Run unit tests: `pytest`
2. Run integration tests: `pytest tests/integration`
3. Start the development server and test all API endpoints

## Rollback Plan

If issues arise, you can revert to the previous commit:

```bash
git checkout <previous-commit-hash>
```
