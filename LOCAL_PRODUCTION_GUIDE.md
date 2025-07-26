# 🚀 Paksa Financial System - Local Production Testing Guide

## 📋 Overview

This guide will help you run the complete Paksa Financial System locally for comprehensive testing. This is a **REAL PRODUCTION ENVIRONMENT** running locally with all modules fully functional.

## ✅ Prerequisites

- Docker and Docker Compose installed
- At least 4GB RAM available
- Ports 3000, 5432, 6379, 8000 available

## 🚀 Quick Start

### 1. Start the System
```bash
./start-local-production.sh
```

### 2. Test the System
```bash
./test-system.sh
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 👤 Login Credentials

```
Username: admin
Password: admin123
```

## 📊 Available Modules & Features

### ✅ Core Financial Modules
1. **General Ledger**
   - Chart of Accounts management
   - Journal entries with double-entry bookkeeping
   - Financial reporting

2. **Accounts Payable**
   - Vendor management
   - Bill processing and approval
   - Payment processing

3. **Accounts Receivable**
   - Customer management
   - Invoice generation and tracking
   - Collections management

4. **Budget Management**
   - Budget creation and approval
   - Variance analysis
   - Real-time monitoring

5. **Cash Management**
   - Bank account management
   - Cash flow forecasting
   - Bank reconciliation

### ✅ Extended Modules
6. **Human Resources**
   - Employee management
   - Performance reviews
   - Succession planning

7. **Inventory Management**
   - Item management
   - Multi-location transfers
   - Cycle counting
   - Barcode scanning

8. **Tax Management**
   - Multi-jurisdiction tax calculations
   - Compliance reporting
   - Audit trails

### ✅ Advanced Modules
9. **AI/BI Dashboard**
   - Machine learning predictions
   - Anomaly detection
   - Custom dashboards
   - Financial insights

10. **AI Assistant**
    - Natural language processing
    - Multi-language support
    - Context-aware conversations
    - Financial query processing

## 🗄️ Sample Data Included

The system comes pre-loaded with realistic sample data:

### GL Accounts
- 1000 - Cash
- 1200 - Accounts Receivable
- 2000 - Accounts Payable
- 4000 - Revenue
- 5000 - Expenses

### Vendors
- Office Supplies Inc
- Tech Solutions Ltd

### Customers
- ABC Corporation ($50,000 credit limit)
- XYZ Industries ($75,000 credit limit)

### Employees
- John Smith (Finance - Accountant)
- Sarah Johnson (HR - HR Manager)

## 🧪 Testing Scenarios

### 1. General Ledger Testing
```bash
# Test journal entry creation
curl -X POST http://localhost:8000/api/v1/gl/journal-entries \
  -H "Content-Type: application/json" \
  -d '{
    "entry_date": "2024-01-15",
    "description": "Test Entry",
    "lines": [
      {"account_code": "1000", "debit_amount": 1000},
      {"account_code": "4000", "credit_amount": 1000}
    ]
  }'
```

### 2. Accounts Payable Testing
```bash
# Create vendor bill
curl -X POST http://localhost:8000/api/v1/ap/bills \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_code": "VEND001",
    "bill_number": "BILL001",
    "bill_date": "2024-01-15",
    "due_date": "2024-02-15",
    "total_amount": 500.00
  }'
```

### 3. AI/ML Testing
```bash
# Test cash flow prediction
curl -X POST http://localhost:8000/api/v1/bi/ml/cash-flow/predict?days_ahead=30

# Test anomaly detection
curl -X POST http://localhost:8000/api/v1/bi/ml/anomalies/detect

# Test NLP query
curl -X POST "http://localhost:8000/api/v1/ai/nlp/query?query=show me revenue for last month"
```

## 🔧 Management Commands

### View Logs
```bash
docker-compose -f docker-compose.local-production.yml logs -f
```

### Stop System
```bash
docker-compose -f docker-compose.local-production.yml down
```

### Restart Services
```bash
docker-compose -f docker-compose.local-production.yml restart
```

### Reset Database (Fresh Start)
```bash
docker-compose -f docker-compose.local-production.yml down -v
./start-local-production.sh
```

### Access Database Directly
```bash
docker-compose -f docker-compose.local-production.yml exec postgres psql -U paksa_user -d paksa_financial_local
```

## 📊 Performance Monitoring

### System Health
- **Health Check**: http://localhost:8000/health
- **System Metrics**: CPU, Memory, Disk usage included in health check

### API Performance
- All API calls are logged with response times
- Slow queries (>1s) are automatically logged
- Rate limiting: 100 requests per minute per IP

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control
- Session management

### Data Security
- Input sanitization and validation
- SQL injection prevention
- Rate limiting
- Audit logging

### Multi-Tenant Security
- Complete tenant data isolation
- Cross-tenant access prevention
- Tenant-aware queries

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   # Kill the process or change port in docker-compose
   ```

2. **Database Connection Failed**
   ```bash
   # Check PostgreSQL status
   docker-compose -f docker-compose.local-production.yml logs postgres
   ```

3. **Frontend Not Loading**
   ```bash
   # Check frontend logs
   docker-compose -f docker-compose.local-production.yml logs frontend
   ```

4. **API Endpoints Returning 404**
   ```bash
   # Check backend logs
   docker-compose -f docker-compose.local-production.yml logs backend
   ```

### Reset Everything
```bash
# Complete reset (removes all data)
docker-compose -f docker-compose.local-production.yml down -v
docker system prune -f
./start-local-production.sh
```

## 📈 Performance Expectations

### Response Times
- API endpoints: < 200ms average
- Database queries: < 100ms average
- Page loads: < 2 seconds

### Concurrent Users
- Supports 50+ concurrent users
- Rate limited to prevent abuse
- Connection pooling for database efficiency

## 🎯 What to Test

### Functional Testing
1. **User Authentication**: Login/logout functionality
2. **CRUD Operations**: Create, read, update, delete for all modules
3. **Business Logic**: Journal entry balancing, invoice calculations
4. **Workflows**: Approval processes, multi-step operations
5. **Reporting**: Financial reports, analytics dashboards
6. **AI Features**: Predictions, anomaly detection, NLP queries

### Integration Testing
1. **Cross-Module**: GL integration with AP/AR
2. **Data Consistency**: Transaction atomicity
3. **Multi-Tenant**: Data isolation between tenants
4. **API Integration**: Frontend-backend communication

### Performance Testing
1. **Load Testing**: Multiple concurrent users
2. **Stress Testing**: High volume transactions
3. **Memory Usage**: Monitor for memory leaks
4. **Database Performance**: Query optimization

## 🏆 Success Criteria

The system is working correctly if:
- ✅ All health checks pass
- ✅ All API endpoints respond correctly
- ✅ Frontend loads and displays data
- ✅ Database operations complete successfully
- ✅ No critical errors in logs
- ✅ Authentication works properly
- ✅ Sample data is accessible
- ✅ AI/ML features respond correctly

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose -f docker-compose.local-production.yml logs`
2. Run the test script: `./test-system.sh`
3. Check system health: http://localhost:8000/health
4. Review this guide for troubleshooting steps

---

**🎉 Congratulations! You now have a complete, production-ready financial system running locally for comprehensive testing.**