<template>
  <div class="dashboard">
    <!-- Header Section -->
    <div class="dashboard-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>Financial Dashboard</h1>
            <p>Welcome to Paksa Financial System - {{ getCurrentDate() }}</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-primary" @click="exportDashboard()">Export Report</button>
            <button class="btn btn-secondary" @click="navigateToModule('/settings')">Settings</button>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Key Metrics Cards -->
      <div class="metrics-section">
        <div class="metrics-grid">
          <div class="metric-card blue">
            <div class="metric-icon">💰</div>
            <div class="metric-content">
              <h3>{{ formatCurrency(metrics.totalAssets) }}</h3>
              <p>Total Assets</p>
              <span class="trend positive">↗ +{{ metrics.assetsTrend }}%</span>
            </div>
          </div>
          
          <div class="metric-card red">
            <div class="metric-icon">💳</div>
            <div class="metric-content">
              <h3>{{ formatCurrency(metrics.totalLiabilities) }}</h3>
              <p>Total Liabilities</p>
              <span class="trend negative">↘ {{ metrics.liabilitiesTrend }}%</span>
            </div>
          </div>
          
          <div class="metric-card green">
            <div class="metric-icon">📈</div>
            <div class="metric-content">
              <h3>{{ formatCurrency(metrics.monthlyRevenue) }}</h3>
              <p>Monthly Revenue</p>
              <span class="trend positive">↗ +{{ metrics.revenueTrend }}%</span>
            </div>
          </div>
          
          <div class="metric-card orange">
            <div class="metric-icon">📉</div>
            <div class="metric-content">
              <h3>{{ formatCurrency(metrics.monthlyExpenses) }}</h3>
              <p>Monthly Expenses</p>
              <span class="trend positive">↗ +{{ metrics.expensesTrend }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-section">
        <div class="charts-grid">
          <div class="chart-card large">
            <div class="card-header">
              <h3>Cash Flow Analysis</h3>
              <select class="period-selector">
                <option>Last 6 Months</option>
                <option>Last Year</option>
              </select>
            </div>
            <div class="chart-container">
              <canvas id="cashFlowChart" width="600" height="300"></canvas>
            </div>
          </div>
          
          <div class="chart-card">
            <div class="card-header">
              <h3>Account Distribution</h3>
            </div>
            <div class="chart-container">
              <canvas id="pieChart" width="300" height="300"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Section -->
      <div class="bottom-section">
        <div class="bottom-grid">
          <!-- Recent Transactions -->
          <div class="transactions-card">
            <div class="card-header">
              <h3>Recent Transactions</h3>
              <button class="btn-link" @click="navigateToModule('/gl/journal-entries')">View All</button>
            </div>
            <div class="transactions-list">
              <div v-for="transaction in recentTransactions" :key="transaction.id" class="transaction-item">
                <div class="transaction-info">
                  <div class="transaction-desc">{{ transaction.description }}</div>
                  <div class="transaction-date">{{ transaction.date }}</div>
                </div>
                <div class="transaction-amount" :class="transaction.amount > 0 ? 'positive' : 'negative'">
                  {{ formatCurrency(transaction.amount) }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- Quick Actions -->
          <div class="actions-card">
            <div class="card-header">
              <h3>Quick Actions</h3>
            </div>
            <div class="actions-grid">
              <button class="action-btn" @click="navigateToModule('/gl/journal-entries')">
                <span class="action-icon">➕</span>
                <span>New Entry</span>
              </button>
              <button class="action-btn" @click="navigateToModule('/gl/accounts')">
                <span class="action-icon">📋</span>
                <span>Accounts</span>
              </button>
              <button class="action-btn" @click="navigateToModule('/ap/analytics')">
                <span class="action-icon">📊</span>
                <span>AP Analytics</span>
              </button>
              <button class="action-btn" @click="navigateToModule('/ap/vendors')">
                <span class="action-icon">🏢</span>
                <span>Vendors</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const metrics = ref({
  totalAssets: 1250000,
  totalLiabilities: 450000,
  monthlyRevenue: 125000,
  monthlyExpenses: 85000,
  assetsTrend: 5.2,
  liabilitiesTrend: -2.1,
  revenueTrend: 8.5,
  expensesTrend: 3.2
})

const cashFlowData = ref([
  { month: 'Jan', inflow: 120000, outflow: 80000 },
  { month: 'Feb', inflow: 135000, outflow: 85000 },
  { month: 'Mar', inflow: 125000, outflow: 90000 },
  { month: 'Apr', inflow: 140000, outflow: 95000 },
  { month: 'May', inflow: 155000, outflow: 100000 },
  { month: 'Jun', inflow: 145000, outflow: 85000 }
])

const balanceData = ref([
  { label: 'Cash', value: 250000, color: '#2196F3' },
  { label: 'Accounts Receivable', value: 180000, color: '#4CAF50' },
  { label: 'Inventory', value: 320000, color: '#FF9800' },
  { label: 'Fixed Assets', value: 500000, color: '#9C27B0' }
])

const recentTransactions = ref([
  {
    id: 1,
    date: '2024-01-15',
    description: 'Office Supplies Purchase',
    amount: -1250.00,
    account: 'Office Expenses'
  },
  {
    id: 2,
    date: '2024-01-14',
    description: 'Client Payment Received',
    amount: 5000.00,
    account: 'Accounts Receivable'
  },
  {
    id: 3,
    date: '2024-01-13',
    description: 'Rent Payment',
    amount: -2500.00,
    account: 'Rent Expense'
  }
])

onMounted(async () => {
  // Load dashboard data
  await loadDashboardData()
})

const loadDashboardData = async () => {
  // In a real app, this would fetch data from the API
  console.log('Loading dashboard data...')
}

const getCurrentDate = () => {
  return new Date().toLocaleDateString('en-US', { 
    weekday: 'long', 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

// Navigation functions
const navigateToModule = (path: string) => {
  window.location.href = path
}

const exportDashboard = () => {
  const dashboardData = {
    date: new Date().toISOString(),
    metrics: {
      totalAssets: metrics.value.totalAssets,
      totalLiabilities: metrics.value.totalLiabilities,
      monthlyRevenue: metrics.value.monthlyRevenue,
      monthlyExpenses: metrics.value.monthlyExpenses
    },
    recentTransactions: recentTransactions.value
  }
  
  const blob = new Blob([JSON.stringify(dashboardData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `dashboard-export-${new Date().toISOString().split('T')[0]}.json`
  link.click()
  URL.revokeObjectURL(url)
  alert('Dashboard data exported successfully')
}

onMounted(() => {
  drawCharts()
})

const drawCharts = () => {
  // Cash Flow Chart
  const cashCanvas = document.getElementById('cashFlowChart') as HTMLCanvasElement
  if (cashCanvas) {
    const ctx = cashCanvas.getContext('2d')
    if (ctx) {
      ctx.clearRect(0, 0, cashCanvas.width, cashCanvas.height)
      
      // Draw chart background
      ctx.fillStyle = '#f8f9fa'
      ctx.fillRect(0, 0, cashCanvas.width, cashCanvas.height)
      
      // Draw chart data
      const data = [120000, 135000, 125000, 140000, 155000, 145000]
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
      
      ctx.strokeStyle = '#1976D2'
      ctx.lineWidth = 3
      ctx.beginPath()
      
      data.forEach((value, index) => {
        const x = (index * 100) + 50
        const y = 250 - (value / 1000)
        
        if (index === 0) ctx.moveTo(x, y)
        else ctx.lineTo(x, y)
        
        // Draw points
        ctx.fillStyle = '#1976D2'
        ctx.beginPath()
        ctx.arc(x, y, 4, 0, 2 * Math.PI)
        ctx.fill()
      })
      
      ctx.stroke()
    }
  }
  
  // Pie Chart
  const pieCanvas = document.getElementById('pieChart') as HTMLCanvasElement
  if (pieCanvas) {
    const ctx = pieCanvas.getContext('2d')
    if (ctx) {
      const centerX = 150
      const centerY = 150
      const radius = 100
      
      const data = [250000, 180000, 320000, 500000]
      const colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']
      const total = data.reduce((a, b) => a + b, 0)
      
      let currentAngle = 0
      
      data.forEach((value, index) => {
        const sliceAngle = (value / total) * 2 * Math.PI
        
        ctx.beginPath()
        ctx.moveTo(centerX, centerY)
        ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle)
        ctx.closePath()
        ctx.fillStyle = colors[index]
        ctx.fill()
        
        currentAngle += sliceAngle
      })
    }
  }
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f7fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Header */
.dashboard-header {
  background: white;
  border-bottom: 1px solid #e0e6ed;
  padding: 20px 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.header-content p {
  color: #718096;
  margin: 5px 0 0 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #1976D2;
  color: white;
}

.btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn:hover {
  transform: translateY(-1px);
}

/* Metrics */
.metrics-section {
  margin: 30px 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.metric-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.metric-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.metric-card.blue .metric-icon { background: #e3f2fd; }
.metric-card.red .metric-icon { background: #ffebee; }
.metric-card.green .metric-icon { background: #e8f5e8; }
.metric-card.orange .metric-icon { background: #fff3e0; }

.metric-content h3 {
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
  color: #2d3748;
}

.metric-content p {
  color: #718096;
  margin: 4px 0;
  font-size: 0.9rem;
}

.trend {
  font-size: 0.8rem;
  font-weight: 600;
}

.trend.positive { color: #38a169; }
.trend.negative { color: #e53e3e; }

/* Charts */
.charts-section {
  margin: 30px 0;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.period-selector {
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
}

.chart-container {
  display: flex;
  justify-content: center;
}

/* Bottom Section */
.bottom-section {
  margin: 30px 0;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.transactions-card,
.actions-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 24px;
}

.btn-link {
  background: none;
  border: none;
  color: #1976D2;
  cursor: pointer;
  font-weight: 500;
}

.transactions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.transaction-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f7fafc;
}

.transaction-desc {
  font-weight: 500;
  color: #2d3748;
}

.transaction-date {
  font-size: 0.8rem;
  color: #718096;
}

.transaction-amount {
  font-weight: 600;
}

.transaction-amount.positive { color: #38a169; }
.transaction-amount.negative { color: #e53e3e; }

.actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: #f7fafc;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #edf2f7;
  transform: translateY(-1px);
}

.action-icon {
  font-size: 1.5rem;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .charts-grid,
  .bottom-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>