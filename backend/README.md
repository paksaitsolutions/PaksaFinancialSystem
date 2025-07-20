# Paksa Financial System - Backend

This is the backend service for the Paksa Financial System, built with FastAPI and PostgreSQL.

## Project Structure

```
backend/
├── .env.example               # Example environment variables
├── .gitignore
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
├── .pylintrc                 # Pylint configuration
├── .python-version           # Python version (for pyenv)
├── .tool-versions            # Version manager configuration (asdf)
├── alembic/                  # Database migrations
├── app/                      # Application package
│   ├── __init__.py
│   ├── api/                  # API routes
│   │   ├── v1/               # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/    # Route handlers
│   │   │   ├── deps.py       # Dependencies
│   │   │   └── routers/      # API routers
│   │   └── deps.py           # Common dependencies
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Configuration
│   │   ├── security.py       # Authentication & authorization
│   │   └── logging.py        # Logging configuration
│   ├── crud/                 # Database operations (CRUD)
│   ├── db/                   # Database configuration
│   │   ├── base.py           # Base database model
│   │   ├── base_class.py     # Base database class
│   │   ├── init_db.py        # Database initialization
│   │   └── session.py        # Database session management
│   ├── middleware/           # Custom middleware
│   │   ├── __init__.py
│   │   ├── error_handler.py  # Global error handling
│   │   └── request_id.py     # Request ID middleware
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic models (request/response)
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   └── auth.py           # Authentication service
│   ├── static/               # Static files
│   ├── tests/                # Tests
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_data/        # Test data
│   │   └── test_*.py         # Test files
│   └── utils/                # Utility functions
│       ├── __init__.py
│       ├── security.py       # Security utilities
│       └── validators.py     # Data validation
├── docker/                   # Docker configuration
│   ├── dev/                  # Development Docker files
│   └── prod/                 # Production Docker files
├── docs/                     # Documentation
│   ├── api/                  # API documentation
│   └── architecture/         # Architecture decision records (ADRs)
├── migrations/               # Database migrations (Alembic)
├── scripts/                  # Utility scripts
├── tests/                    # Integration/end-to-end tests
├── .env                      # Environment variables (git-ignored)
├── .env.test                 # Test environment variables
├── .flake8                   # Flake8 configuration
├── alembic.ini               # Alembic configuration
├── main.py                   # Application entry point
├── pyproject.toml            # Project metadata and dependencies
└── pytest.ini                # Pytest configuration
```

## Development Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- Redis (for caching and rate limiting)
- Docker (optional, for containerized development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/paksa-financial-system.git
   cd paksa-financial-system/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements/dev.txt
   ```

4. Copy the example environment file and update the values:
   ```bash
   cp .env.example .env
   ```

5. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Running the Application

1. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Access the API documentation at http://localhost:8000/api/docs

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=term-missing

# Run a specific test file
pytest tests/test_auth.py -v
```

### Code Style & Linting

```bash
# Run black code formatter
black .

# Run isort to sort imports
isort .

# Run flake8 for linting
flake8

# Run mypy for type checking
mypy .
```

## API Documentation

- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`
- OpenAPI schema: `/api/openapi.json`

## Deployment

### Docker

```bash
# Build the Docker image
docker-compose -f docker-compose.prod.yml build

# Start the services
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes (optional)

```bash
kubectl apply -f k8s/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Proprietary - © 2025 Paksa IT Solutions. All rights reserved.
