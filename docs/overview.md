# Paksa Financial System - Architecture and Setup Guide

## System Overview

The Paksa Financial System is a comprehensive financial management platform designed to handle core accounting functions with a focus on reliability, security, and extensibility. The system follows a modular microservices architecture built with Python and FastAPI, with PostgreSQL as the primary database.

## Architecture

### Backend Structure

```
backend/
├── api/
│   └── v1/
│       ├── endpoints/         # API endpoint definitions
│       └── api.py             # Main API router
├── core/                     
│   ├── config.py             # Application configuration
│   ├── database.py           # Database connection and session management
│   └── security.py           # Authentication and authorization
├── crud/                     # Database operations
├── models/                   # SQLAlchemy models
├── schemas/                  # Pydantic models for request/response
├── services/                 # Business logic layer
└── scripts/                  # Database initialization and migration scripts
```

### Core Modules

1. **General Ledger**
   - Chart of Accounts management
   - Journal Entries
   - Financial reporting

2. **Accounts Payable** (Planned)
   - Vendor management
   - Bill processing
   - Payment tracking

3. **Accounts Receivable** (Planned)
   - Customer management
   - Invoicing
   - Payment processing

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis (for caching and background tasks)
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd paksa-financial-system
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory with the following variables:
   ```env
   # Database
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/paksa_finance
   
   # Security
   SECRET_KEY=your-secret-key
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   
   # CORS
   BACKEND_CORS_ORIGINS=["http://localhost:3000"]
   ```

5. **Database Setup**
   ```bash
   # Run database migrations
   alembic upgrade head
   
   # Initialize database with required data
   python -m backend.scripts.init_db
   ```

6. **Run the application**
   ```bash
   uvicorn backend.main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   
   API documentation (Swagger UI) will be available at `http://localhost:8000/docs`

## API Documentation

### Authentication
All API endpoints (except public ones) require authentication using JWT tokens.

1. Obtain a token by authenticating:
   ```
   POST /api/v1/auth/login
   ```

2. Include the token in subsequent requests:
   ```
   Authorization: Bearer <token>
   ```

### Key Endpoints

#### Chart of Accounts
- `GET /api/v1/chart-of-accounts/` - List all accounts
- `GET /api/v1/chart-of-accounts/tree` - Get accounts as a hierarchical tree
- `POST /api/v1/chart-of-accounts/` - Create a new account
- `GET /api/v1/chart-of-accounts/{account_id}` - Get account details
- `PUT /api/v1/chart-of-accounts/{account_id}` - Update an account
- `DELETE /api/v1/chart-of-accounts/{account_id}` - Delete an account

#### Journal Entries
- `GET /api/v1/journal-entries/` - List all journal entries
- `POST /api/v1/journal-entries/` - Create a new journal entry
- `GET /api/v1/journal-entries/{entry_id}` - Get journal entry details
- `PUT /api/v1/journal-entries/{entry_id}` - Update a journal entry
- `DELETE /api/v1/journal-entries/{entry_id}` - Delete a journal entry
- `POST /api/v1/journal-entries/{entry_id}/post` - Post a journal entry

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints throughout the codebase
- Document all public functions and classes with docstrings
- Keep functions small and focused on a single responsibility

### Testing
Run tests using pytest:
```bash
pytest
```

### Database Migrations
When making changes to the database schema:
1. Create a new migration:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```
2. Review the generated migration file
3. Apply the migration:
   ```bash
   alembic upgrade head
   ```

## Deployment

### Production Deployment
For production deployment, it's recommended to use:
- Gunicorn with Uvicorn workers
- Nginx as a reverse proxy
- PostgreSQL with connection pooling
- Redis for caching and background tasks

Example Gunicorn command:
```bash
gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Security Considerations

- Always use HTTPS in production
- Keep dependencies up to date
- Regularly backup the database
- Implement rate limiting
- Monitor for suspicious activities
- Follow the principle of least privilege for database users
