# Paksa Financial System

Enterprise financial management platform with FastAPI (backend) and Vue 3 + Vite (frontend).

## Overview
- Modules: GL, AP, AR, Budget, Cash, Inventory, Payroll, Tax, Fixed Assets, Reports, Admin
- Async SQLAlchemy, JWT auth, modular API under `/api/v1`

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- SQLite (dev) or PostgreSQL (prod)

### Backend
```bash
python -m venv .venv
./.venv/Scripts/activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r backend/requirements.txt

# Run API (standard entry)
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api/*` to the backend on port 8000.

### Default Login (Dev)
- Email: `admin@paksa.com`
- Password: `admin123`

Configure the first superuser via `.env`:
```
FIRST_SUPERUSER_EMAIL=admin@paksa.com
FIRST_SUPERUSER_PASSWORD=admin123
```

## Notes
- Main app module: `backend/app/main.py` (Dockerfile uses `app.main:app`)
- Versioned API router mounted at `/api/v1`
- For production, configure DB in environment variables or `backend/app/core/config/settings.py`

