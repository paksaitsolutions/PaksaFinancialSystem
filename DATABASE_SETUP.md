# Database Setup and Authentication Testing

This document provides instructions for setting up the database and testing the authentication flow for the Paksa Financial System.

## Database Configuration

### Backend Configuration

The backend database configuration is stored in the `.env` file. The system supports both SQLite and PostgreSQL databases.

#### Using SQLite (Default)

```
DB_ENGINE=sqlite
SQLITE_DB_PATH=./instance/paksa_finance.db
```

#### Using PostgreSQL

```
DB_ENGINE=postgresql
POSTGRES_DB=paksa_finance
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Database Migrations with Alembic

Alembic is configured for database migrations. Here's how to use it:

1. **Initialize migrations directory** (if not already done):
   ```bash
   cd backend
   alembic init alembic
   ```

2. **Create a new migration**:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

3. **Apply migrations**:
   ```bash
   alembic upgrade head
   ```

4. **Rollback migrations**:
   ```bash
   alembic downgrade -1  # Rollback one migration
   # OR
   alembic downgrade base  # Rollback all migrations
   ```

## Authentication Testing

A test script is provided to verify the authentication flow, including token refresh:

```bash
# Install axios if not already installed
npm install axios

# Run the test script
node test_auth_flow.js
```

The test script performs the following steps:
1. Login with test credentials
2. Access user profile with the access token
3. Refresh the access token
4. Verify the new token works

## Frontend Configuration

The frontend API configuration is stored in the `.env` file:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_API_PREFIX=/api/v1
```

Make sure the API URL matches your backend server configuration.

## Starting the Application

1. **Start the backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

## Troubleshooting

### Database Connection Issues

- Verify the database credentials in the `.env` file
- For PostgreSQL, ensure the database server is running
- For SQLite, ensure the directory for the database file exists

### Authentication Issues

- Check that the `SECRET_KEY` and `REFRESH_SECRET_KEY` are set in the backend `.env` file
- Verify that the API URLs in the frontend `.env` file match the backend server
- Check CORS settings if the frontend and backend are on different domains/ports