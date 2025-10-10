# Project Wiki

## Project Description

This project is a financial system with a backend written in Python and a frontend likely written in JavaScript. It includes modules for accounting, accounts payable, accounts receivable, AI assistant, auth, BI AI, HRM, inventory, invoicing, procurement, and tax. The project is deployed using Kubernetes.

## Project Structure

- `.github`: Contains GitHub configuration files.
- `.venv`: Contains the Python virtual environment.
- `alembic`: Contains database migration scripts.
- `backend`: Contains the backend code.
- `frontend`: Contains the frontend code.
- `instance`: Contains instance-specific configuration.
- `k8s`: Contains Kubernetes configuration files.
- `monitoring`: Contains monitoring configuration files.
- `nginx`: Contains Nginx configuration files.
- `ops`: Contains operational scripts and configuration.
- `postgres`: Contains PostgreSQL configuration files.
- `postgres_data`: Contains PostgreSQL data.
- `redis_data`: Contains Redis data.

## How to Run the Project

### Backend

1. Create a virtual environment: `python -m venv .venv`
2. Activate the virtual environment:
    - Windows: `.venv\Scripts\activate`
    - Linux/macOS: `source .venv/bin/activate`
3. Install the dependencies: `pip install -r backend/requirements.txt`
4. Run the backend: `uvicorn app.main:app --reload`

### Frontend

1. Install the dependencies: `npm install`
2. Run the frontend: `npm run dev`

## How to Test the Project

### Backend

1. Navigate to the `backend` directory: `cd backend`
2. Run the tests: `pytest`

## How to Test the Project

[To be added]