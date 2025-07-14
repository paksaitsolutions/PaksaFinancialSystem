# 🚀 Quick Start Guide - Run Home Page & Dashboard

## Option 1: Quick Development Start

```bash
# Navigate to project root
cd /workspaces/PaksaFinancialSystem

# Make startup script executable (if not already)
chmod +x start-dev.sh

# Start both backend and frontend
./start-dev.sh
```

## Option 2: Frontend Only (for UI preview)

```bash
# Navigate to frontend directory
cd /workspaces/PaksaFinancialSystem/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Option 3: Docker Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f frontend
```

## 🌐 Access URLs

Once running, access these URLs:

- **Home Page**: http://localhost:3000/
- **Dashboard**: http://localhost:3000/dashboard
- **Chart of Accounts**: http://localhost:3000/gl/accounts

## 📋 What You'll See

### Home Page Features:
- ✅ Professional hero section with gradient background
- ✅ 6 feature cards for financial modules
- ✅ System statistics (150+ accounts, 2.5K+ transactions)
- ✅ Quick access panel with 6 action buttons
- ✅ Responsive design with hover effects

### Dashboard Features:
- ✅ 4 KPI metric cards with trend indicators
- ✅ Cash flow chart (6-month visualization)
- ✅ Account balance pie chart with legend
- ✅ Recent transactions list
- ✅ Quick actions panel

## 🔧 Troubleshooting

### If npm install fails:
```bash
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### If port 3000 is busy:
```bash
# Use different port
npm run dev -- --port 3001
```

### If Vuetify components don't load:
```bash
# Ensure Vuetify is installed
npm install vuetify @mdi/font
```

## 📱 Mobile Preview

The interface is fully responsive:
- **Desktop**: Full 4-column layout
- **Tablet**: 2-column responsive grid
- **Mobile**: Single column with touch-friendly buttons

## 🎨 Visual Features

- **Material Design**: Modern Vuetify 3 components
- **Color Coding**: Blue (assets), Red (liabilities), Green (revenue)
- **Animations**: Smooth hover effects and transitions
- **Icons**: Material Design Icons throughout
- **Charts**: Canvas-based visualizations

The system is ready to run and provides a complete financial management interface!