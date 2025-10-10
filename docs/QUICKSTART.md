# Paksa Financial System - Quick Start Guide

## 🚀 Quick Deployment

### Prerequisites
- Docker Desktop installed
- Git (optional)

### 1. Clone or Download
```bash
git clone <repository-url>
cd PaksaFinancialSystem_New
```

### 2. Deploy with One Command

**Windows:**
```powershell
.\deploy.ps1
```

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. Access the System
- **Frontend:** http://localhost
- **API Documentation:** http://localhost/docs
- **Backend API:** http://localhost/api

### 4. Default Login
- **Email:** admin@paksa.com
- **Password:** admin123

## 🛠️ Development Setup

### Backend Development
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 📋 Available Services

### Core Financial Modules
- ✅ **General Ledger** - Chart of accounts, journal entries, trial balance
- ✅ **Accounts Payable** - Vendor management, bill processing, payments
- ✅ **Accounts Receivable** - Customer management, invoicing, collections
- ✅ **Cash Management** - Bank accounts, transactions, reconciliation

### Operational Modules
- ✅ **Inventory Management** - Items, locations, adjustments
- ✅ **Fixed Assets** - Asset tracking, depreciation
- ✅ **Budget Management** - Planning, monitoring, forecasting
- ✅ **Payroll** - Employee management, pay runs, payslips

### Compliance & Analytics
- ✅ **Tax Management** - Tax rates, returns, compliance
- ✅ **Human Resources** - Employee records, attendance, performance
- ✅ **Reports & Analytics** - Financial statements, custom reports
- ✅ **AI & Business Intelligence** - Automated insights, forecasting

## 🔧 Configuration

### Environment Variables
Edit `.env` file to configure:
- Database connection
- Security settings
- Email configuration
- External integrations

### Database Options
- **Development:** SQLite (default)
- **Production:** PostgreSQL (recommended)

## 📊 Key Features

### Authentication & Security
- JWT-based authentication
- Role-based access control
- Secure password hashing
- Session management

### User Interface
- Modern Vue 3 + TypeScript frontend
- PrimeVue component library
- Responsive design
- Dark/light theme support

### API & Integration
- RESTful API with FastAPI
- OpenAPI/Swagger documentation
- Async database operations
- Comprehensive error handling

### Deployment
- Docker containerization
- Nginx load balancing
- Health monitoring
- Horizontal scaling ready

## 🚨 Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check what's using port 80/8000/3000
netstat -ano | findstr :80
# Kill process if needed
taskkill /PID <process_id> /F
```

**Docker issues:**
```bash
# Reset Docker
docker-compose down
docker system prune -f
docker-compose up --build
```

**Database issues:**
```bash
# Reset database
docker-compose down -v
docker-compose up
```

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f nginx
```

## 📞 Support

### Useful Commands
```bash
# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Update and rebuild
docker-compose pull
docker-compose up --build -d

# View system status
docker-compose ps
```

### Health Checks
- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000
- Full system: http://localhost

## 🎯 Next Steps

1. **Customize Configuration** - Edit `.env` for your environment
2. **Set Up Database** - Configure PostgreSQL for production
3. **Configure Email** - Set up SMTP for notifications
4. **Add Users** - Create additional user accounts
5. **Import Data** - Use data migration tools
6. **Customize Branding** - Update logos and themes
7. **Set Up Backups** - Configure automated backups
8. **Monitor System** - Set up logging and monitoring

## 📚 Documentation

- **API Docs:** http://localhost/docs
- **User Guide:** `/docs/user_guide.md`
- **Developer Guide:** `/docs/developer.md`
- **Architecture:** `/docs/architecture.md`

---

**🎉 You're ready to use Paksa Financial System!**