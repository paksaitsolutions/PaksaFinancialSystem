# Paksa Financial System

Enterprise-grade financial management platform built with FastAPI (backend) and Vue 3 + Vite (frontend). A comprehensive solution for managing all aspects of business finance.

## 🌟 Features

### Core Modules
- **General Ledger**: Complete double-entry accounting system
- **Accounts Payable**: Vendor invoices, payments, and expense tracking
- **Accounts Receivable**: Customer invoicing and payment processing
- **Banking & Cash**: Bank reconciliation and cash flow management
- **Budgeting**: Financial planning and budget tracking
- **Inventory**: Stock management and valuation
- **Fixed Assets**: Asset tracking and depreciation
- **Payroll**: Employee compensation and benefits
- **Tax Management**: Tax calculation and reporting
- **Financial Reports**: Comprehensive reporting suite

### Technical Highlights
- 🚀 **Modern Stack**: FastAPI + Vue 3 + TypeScript + Vite
- 🔐 **Security**: JWT authentication, RBAC, and data encryption
- 📊 **Real-time**: WebSocket support for live updates
- 📱 **Responsive**: Mobile-first design with PrimeVue components
- 🌐 **i18n**: Multi-language support built-in

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 13+ (or SQLite for development)
- Redis (for caching and WebSockets)

### Environment Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/paksa-financial-system.git
   cd paksa-financial-system
   ```

2. Set up backend:
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   .\.venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac

   # Install dependencies
   pip install -r backend/requirements.txt

   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Set up frontend:
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   # Edit .env.local if needed
   ```

### Running the Application

#### Development Mode
```bash
# Backend
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in a new terminal)
cd frontend
npm run dev
```

#### Production Deployment
```bash
# Build frontend
cd frontend
npm run build

# Run with Uvicorn (behind a reverse proxy like Nginx in production)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# Or using Docker
# docker-compose up -d --build
```

## 🔐 Authentication
Default admin credentials (change in production):
- **Email**: admin@paksa.com
- **Password**: admin123

Configure initial superuser via environment variables:
```
FIRST_SUPERUSER_EMAIL=admin@paksa.com
FIRST_SUPERUSER_PASSWORD=your_secure_password
```

## 📚 Documentation
- **API Documentation**: Available at `/docs` when running locally
- **Architecture**: See `docs/architecture.md`
- **API Reference**: See `docs/api/`

## 🛠 Development

### Code Style
- Backend: Black, isort, flake8
- Frontend: ESLint, Prettier

### Testing
```bash
# Backend tests
pytest

# Frontend tests
cd frontend
npm test
```

## 📦 Deployment

### Docker
```bash
docker-compose up -d --build
```

### Kubernetes
See `k8s/` directory for deployment manifests.

## 🤝 Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team
- [Paksa IT Solutions](https://github.com/paksaitsolutions) - Project Lead

## 🙏 Acknowledgments
- Built with ❤️ using amazing open source software

