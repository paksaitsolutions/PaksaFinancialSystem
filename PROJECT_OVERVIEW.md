# Paksa Financial System - Project Deep Dive

## 🏗️ Architecture Overview

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.10+
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy 2.0 with Alembic migrations
- **Authentication**: JWT tokens with OAuth2
- **API Documentation**: Auto-generated OpenAPI/Swagger at `/docs`

### Frontend (Vue 3)
- **Framework**: Vue 3 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **UI Library**: PrimeVue components with PrimeFlex CSS
- **State Management**: Pinia stores
- **Routing**: Vue Router 4

## 📁 Project Structure

```
PaksaFinancialSystem/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core configuration
│   │   ├── models/        # Database models
│   │   ├── modules/       # Business modules
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI application
│   ├── alembic/           # Database migrations
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── modules/       # Feature modules
│   │   ├── router/        # Route definitions
│   │   ├── stores/        # Pinia stores
│   │   └── main.ts        # Vue application
│   ├── package.json       # Node.js dependencies
│   └── vite.config.ts     # Vite configuration
└── .env                   # Environment variables
```

## 🚀 Quick Start Guide

### Prerequisites
- ✅ Python 3.10+ (Detected: 3.10.11)
- ✅ Node.js 18+ (Detected: v22.19.0)
- ✅ Database file exists (paksa_financial.db)

### Option 1: Automated Setup
```bash
# Run the quick setup (installs all dependencies)
quick_setup.bat

# Start both services
start_project.bat
```

### Option 2: Manual Setup
```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate.bat

# 2. Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# 3. Install frontend dependencies
cd frontend
npm install
cd ..

# 4. Start backend (Terminal 1)
run_backend.bat

# 5. Start frontend (Terminal 2)
run_frontend.bat
```

### Option 3: Individual Services
```bash
# Backend only
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend only
cd frontend
npm run dev
```

## 🔗 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3003 | Main application interface |
| Backend API | http://localhost:8000 | REST API endpoints |
| API Documentation | http://localhost:8000/docs | Interactive Swagger UI |
| Health Check | http://localhost:8000/health | System status |

## 🔐 Default Credentials

- **Email**: admin@paksa.com
- **Password**: admin123

## 📊 Available Modules

### Core Financial Modules
1. **General Ledger (GL)** - Chart of accounts, journal entries, trial balance
2. **Accounts Payable (AP)** - Vendor management, invoices, payments
3. **Accounts Receivable (AR)** - Customer management, invoicing, collections
4. **Budget Management** - Budget planning, tracking, variance analysis
5. **Cash Management** - Bank accounts, reconciliation, cash flow

### Operational Modules
6. **Human Resources (HRM)** - Employee management, departments
7. **Payroll** - Salary processing, payslips, tax calculations
8. **Inventory** - Stock management, locations, valuation
9. **Fixed Assets** - Asset tracking, depreciation
10. **Tax Management** - Tax rates, returns, compliance

### Reporting & Analytics
11. **Financial Reports** - P&L, Balance Sheet, Cash Flow
12. **Dashboard Analytics** - KPIs, charts, real-time data
13. **System Administration** - User management, permissions

## 🛠️ Development Features

### Backend Features
- **Security**: JWT authentication, CORS, rate limiting, CSRF protection
- **Database**: SQLAlchemy ORM with automatic migrations
- **API**: RESTful endpoints with automatic OpenAPI documentation
- **Validation**: Pydantic schemas for request/response validation
- **Error Handling**: Comprehensive error handling and logging

### Frontend Features
- **Modern UI**: PrimeVue components with responsive design
- **Performance**: Code splitting, lazy loading, optimized builds
- **Development**: Hot reload, TypeScript support, ESLint/Prettier
- **State Management**: Pinia stores for reactive state
- **Routing**: Protected routes with authentication guards

## 🔧 Configuration

### Environment Variables (.env)
```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./paksa_financial.db

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Admin User
FIRST_SUPERUSER_EMAIL=admin@paksa.com
FIRST_SUPERUSER_PASSWORD=admin123

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

## 📈 Next Steps

1. **Access the application** at http://localhost:3003
2. **Login** with the default credentials
3. **Explore modules** through the navigation menu
4. **Check API documentation** at http://localhost:8000/docs
5. **Review database** structure in the SQLite file

## 🐛 Troubleshooting

### Common Issues
- **Port conflicts**: Change ports in .env or vite.config.ts
- **Database errors**: Check if paksa_financial.db exists and is writable
- **Import errors**: Ensure virtual environment is activated
- **CORS issues**: Verify CORS_ORIGINS in backend configuration

### Logs
- Backend logs appear in the terminal running uvicorn
- Frontend logs appear in browser developer console
- Database queries can be seen when DEBUG=true