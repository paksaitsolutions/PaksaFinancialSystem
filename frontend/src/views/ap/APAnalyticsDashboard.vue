<template>
  <div class="ap-analytics-dashboard">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>AP Analytics Dashboard</h1>
            <p>AI-powered insights and business intelligence for accounts payable</p>
          </div>
          <div class="header-actions">
            <select v-model="selectedPeriod" class="period-select">
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="1y">Last Year</option>
            </select>
            <button class="btn btn-primary" @click="exportReport">
              📊 Export Report
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- AI Insights Section -->
      <div class="ai-insights-section">
        <div class="section-header">
          <h2>🤖 AI-Powered Insights</h2>
          <button class="btn btn-outline" @click="refreshInsights">
            🔄 Refresh
          </button>
        </div>
        
        <div class="insights-grid">
          <div class="insight-card critical">
            <div class="insight-header">
              <span class="insight-icon">⚠️</span>
              <h3>Fraud Risk Alert</h3>
            </div>
            <div class="insight-content">
              <div class="insight-metric">3 High-Risk Invoices</div>
              <div class="insight-description">
                AI detected potential fraud patterns in recent invoices
              </div>
              <button class="insight-action" @click="viewFraudAlerts">
                Investigate →
              </button>
            </div>
          </div>

          <div class="insight-card warning">
            <div class="insight-header">
              <span class="insight-icon">💡</span>
              <h3>Cost Optimization</h3>
            </div>
            <div class="insight-content">
              <div class="insight-metric">$12,500 Potential Savings</div>
              <div class="insight-description">
                Early payment discounts available from 8 vendors
              </div>
              <button class="insight-action" @click="viewOptimizations">
                View Opportunities →
              </button>
            </div>
          </div>

          <div class="insight-card info">
            <div class="insight-header">
              <span class="insight-icon">📈</span>
              <h3>Cash Flow Prediction</h3>
            </div>
            <div class="insight-content">
              <div class="insight-metric">$245,000 Next 30 Days</div>
              <div class="insight-description">
                Predicted AP payments based on historical patterns
              </div>
              <button class="insight-action" @click="viewCashFlow">
                View Forecast →
              </button>
            </div>
          </div>

          <div class="insight-card success">
            <div class="insight-header">
              <span class="insight-icon">✅</span>
              <h3>Process Efficiency</h3>
            </div>
            <div class="insight-content">
              <div class="insight-metric">92% Automation Rate</div>
              <div class="insight-description">
                Invoice processing time reduced by 65% this month
              </div>
              <button class="insight-action" @click="viewEfficiency">
                View Details →
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Key Metrics Section -->
      <div class="metrics-section">
        <div class="section-header">
          <h2>📊 Key Performance Metrics</h2>
        </div>
        
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-header">
              <h3>Total Outstanding</h3>
              <span class="metric-trend up">+5.2%</span>
            </div>
            <div class="metric-value">{{ formatCurrency(kpiData.totalOutstanding) }}</div>
            <div class="metric-chart">
              <canvas ref="outstandingChart" width="200" height="60"></canvas>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <h3>Average Payment Days</h3>
              <span class="metric-trend down">-2.1 days</span>
            </div>
            <div class="metric-value">{{ kpiData.avgPaymentDays }} days</div>
            <div class="metric-chart">
              <canvas ref="paymentDaysChart" width="200" height="60"></canvas>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <h3>On-Time Payment Rate</h3>
              <span class="metric-trend up">+3.5%</span>
            </div>
            <div class="metric-value">{{ kpiData.onTimeRate }}%</div>
            <div class="metric-chart">
              <canvas ref="onTimeChart" width="200" height="60"></canvas>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <h3>Cost Per Invoice</h3>
              <span class="metric-trend down">-$1.20</span>
            </div>
            <div class="metric-value">{{ formatCurrency(kpiData.costPerInvoice) }}</div>
            <div class="metric-chart">
              <canvas ref="costChart" width="200" height="60"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-section">
        <div class="charts-grid">
          <!-- Cash Flow Forecast Chart -->
          <div class="chart-card large">
            <div class="chart-header">
              <h3>AI Cash Flow Forecast</h3>
              <div class="chart-controls">
                <select v-model="forecastPeriod">
                  <option value="30">30 Days</option>
                  <option value="60">60 Days</option>
                  <option value="90">90 Days</option>
                </select>
              </div>
            </div>
            <div class="chart-container">
              <canvas ref="cashFlowChart" width="800" height="300"></canvas>
            </div>
            <div class="chart-insights">
              <div class="insight-item">
                <span class="insight-label">Predicted Total:</span>
                <span class="insight-value">{{ formatCurrency(245000) }}</span>
              </div>
              <div class="insight-item">
                <span class="insight-label">Confidence:</span>
                <span class="insight-value">87%</span>
              </div>
              <div class="insight-item">
                <span class="insight-label">Peak Day:</span>
                <span class="insight-value">March 15</span>
              </div>
            </div>
          </div>

          <!-- Vendor Risk Analysis -->
          <div class="chart-card">
            <div class="chart-header">
              <h3>Vendor Risk Distribution</h3>
            </div>
            <div class="chart-container">
              <canvas ref="riskChart" width="400" height="300"></canvas>
            </div>
            <div class="risk-legend">
              <div class="legend-item low">
                <span class="legend-color"></span>
                <span>Low Risk (65%)</span>
              </div>
              <div class="legend-item medium">
                <span class="legend-color"></span>
                <span>Medium Risk (25%)</span>
              </div>
              <div class="legend-item high">
                <span class="legend-color"></span>
                <span>High Risk (10%)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Invoice Processing Analytics -->
        <div class="chart-card full-width">
          <div class="chart-header">
            <h3>Invoice Processing Analytics</h3>
            <div class="chart-tabs">
              <button class="tab-btn" :class="{ active: activeTab === 'volume' }" @click="activeTab = 'volume'">
                Volume
              </button>
              <button class="tab-btn" :class="{ active: activeTab === 'approval' }" @click="activeTab = 'approval'">
                Approval Time
              </button>
              <button class="tab-btn" :class="{ active: activeTab === 'exceptions' }" @click="activeTab = 'exceptions'">
                Exceptions
              </button>
            </div>
          </div>
          <div class="chart-container">
            <canvas ref="processingChart" width="1000" height="400"></canvas>
          </div>
        </div>
      </div>

      <!-- Vendor Performance Section -->
      <div class="vendor-performance-section">
        <div class="section-header">
          <h2>🏆 Top Vendor Performance</h2>
          <button class="btn btn-outline" @click="viewAllVendors">
            View All Vendors
          </button>
        </div>
        
        <div class="performance-grid">
          <div v-for="vendor in topVendors" :key="vendor.id" class="vendor-performance-card">
            <div class="vendor-header">
              <div class="vendor-info">
                <h4>{{ vendor.name }}</h4>
                <span class="vendor-category">{{ vendor.category }}</span>
              </div>
              <div class="vendor-score" :class="getScoreClass(vendor.overallScore)">
                {{ vendor.overallScore }}
              </div>
            </div>
            
            <div class="performance-metrics">
              <div class="metric-row">
                <span class="metric-label">Reliability</span>
                <div class="metric-bar">
                  <div class="metric-fill" :style="{ width: vendor.reliability + '%' }"></div>
                </div>
                <span class="metric-value">{{ vendor.reliability }}%</span>
              </div>
              
              <div class="metric-row">
                <span class="metric-label">On-Time Delivery</span>
                <div class="metric-bar">
                  <div class="metric-fill" :style="{ width: vendor.onTimeDelivery + '%' }"></div>
                </div>
                <span class="metric-value">{{ vendor.onTimeDelivery }}%</span>
              </div>
              
              <div class="metric-row">
                <span class="metric-label">Quality Score</span>
                <div class="metric-bar">
                  <div class="metric-fill" :style="{ width: vendor.quality + '%' }"></div>
                </div>
                <span class="metric-value">{{ vendor.quality }}%</span>
              </div>
            </div>
            
            <div class="vendor-stats">
              <div class="stat-item">
                <span class="stat-label">Total Spend</span>
                <span class="stat-value">{{ formatCurrency(vendor.totalSpend) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Invoices</span>
                <span class="stat-value">{{ vendor.invoiceCount }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Aging Analysis Section -->
      <div class="aging-section">
        <div class="section-header">
          <h2>📅 Aging Analysis</h2>
          <button class="btn btn-outline" @click="exportAging">
            Export Aging Report
          </button>
        </div>
        
        <div class="aging-grid">
          <div class="aging-summary">
            <h3>Outstanding by Age</h3>
            <div class="aging-bars">
              <div class="aging-bar">
                <div class="bar-label">Current</div>
                <div class="bar-container">
                  <div class="bar-fill current" :style="{ width: '75%' }"></div>
                </div>
                <div class="bar-value">{{ formatCurrency(180000) }}</div>
              </div>
              
              <div class="aging-bar">
                <div class="bar-label">1-30 Days</div>
                <div class="bar-container">
                  <div class="bar-fill days-30" :style="{ width: '45%' }"></div>
                </div>
                <div class="bar-value">{{ formatCurrency(85000) }}</div>
              </div>
              
              <div class="aging-bar">
                <div class="bar-label">31-60 Days</div>
                <div class="bar-container">
                  <div class="bar-fill days-60" :style="{ width: '25%' }"></div>
                </div>
                <div class="bar-value">{{ formatCurrency(45000) }}</div>
              </div>
              
              <div class="aging-bar">
                <div class="bar-label">60+ Days</div>
                <div class="bar-container">
                  <div class="bar-fill overdue" :style="{ width: '15%' }"></div>
                </div>
                <div class="bar-value">{{ formatCurrency(25000) }}</div>
              </div>
            </div>
          </div>
          
          <div class="aging-chart">
            <canvas ref="agingChart" width="400" height="300"></canvas>
          </div>
        </div>
      </div>

      <!-- AI Recommendations Section -->
      <div class="recommendations-section">
        <div class="section-header">
          <h2>🎯 AI Recommendations</h2>
          <span class="recommendation-count">{{ aiRecommendations.length }} active recommendations</span>
        </div>
        
        <div class="recommendations-list">
          <div v-for="rec in aiRecommendations" :key="rec.id" class="recommendation-card" :class="rec.priority">
            <div class="rec-header">
              <div class="rec-icon">{{ rec.icon }}</div>
              <div class="rec-title">{{ rec.title }}</div>
              <div class="rec-impact">{{ rec.impact }}</div>
            </div>
            <div class="rec-description">{{ rec.description }}</div>
            <div class="rec-actions">
              <button class="btn btn-sm btn-primary" @click="implementRecommendation(rec)">
                {{ rec.actionText }}
              </button>
              <button class="btn btn-sm btn-outline" @click="dismissRecommendation(rec)">
                Dismiss
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive data
const selectedPeriod = ref('30d')
const forecastPeriod = ref('30')
const activeTab = ref('volume')

// KPI Data
const kpiData = ref({
  totalOutstanding: 485000,
  avgPaymentDays: 28.5,
  onTimeRate: 87.3,
  costPerInvoice: 8.45
})

// Top Vendors Data
const topVendors = ref([
  {
    id: 1,
    name: 'Tech Solutions LLC',
    category: 'Technology',
    overallScore: 95,
    reliability: 98,
    onTimeDelivery: 94,
    quality: 92,
    totalSpend: 125000,
    invoiceCount: 45
  },
  {
    id: 2,
    name: 'ABC Supplies Inc.',
    category: 'Supplies',
    overallScore: 88,
    reliability: 85,
    onTimeDelivery: 90,
    quality: 89,
    totalSpend: 85000,
    invoiceCount: 32
  },
  {
    id: 3,
    name: 'Professional Services Co.',
    category: 'Services',
    overallScore: 82,
    reliability: 80,
    onTimeDelivery: 85,
    quality: 81,
    totalSpend: 95000,
    invoiceCount: 28
  }
])

// AI Recommendations
const aiRecommendations = ref([
  {
    id: 1,
    icon: '💰',
    title: 'Early Payment Discount Opportunity',
    description: 'Take advantage of 2% early payment discount from ABC Corp - potential savings of $2,400',
    priority: 'high',
    impact: 'High Impact',
    actionText: 'Schedule Payment'
  },
  {
    id: 2,
    icon: '⚡',
    title: 'Automate Recurring Payments',
    description: 'Set up automatic payments for 12 recurring vendors to reduce processing time by 40%',
    priority: 'medium',
    impact: 'Medium Impact',
    actionText: 'Set Up Automation'
  },
  {
    id: 3,
    icon: '🔍',
    title: 'Vendor Consolidation Opportunity',
    description: 'Consolidate 5 similar suppliers to negotiate better terms and reduce management overhead',
    priority: 'low',
    impact: 'Low Impact',
    actionText: 'Review Vendors'
  }
])

// Chart references
const outstandingChart = ref(null)
const paymentDaysChart = ref(null)
const onTimeChart = ref(null)
const costChart = ref(null)
const cashFlowChart = ref(null)
const riskChart = ref(null)
const processingChart = ref(null)
const agingChart = ref(null)

// Methods
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const getScoreClass = (score: number) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'average'
  return 'poor'
}

const drawCharts = () => {
  // Draw mini charts for KPI cards
  drawMiniChart(outstandingChart.value, [450, 465, 480, 485], '#3182ce')
  drawMiniChart(paymentDaysChart.value, [32, 30, 29, 28.5], '#10b981')
  drawMiniChart(onTimeChart.value, [82, 85, 86, 87.3], '#8b5cf6')
  drawMiniChart(costChart.value, [12, 10, 9, 8.45], '#f59e0b')
  
  // Draw main charts
  drawCashFlowChart()
  drawRiskChart()
  drawProcessingChart()
  drawAgingChart()
}

const drawMiniChart = (canvas: HTMLCanvasElement, data: number[], color: string) => {
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.strokeStyle = color
  ctx.lineWidth = 2
  ctx.beginPath()
  
  const width = canvas.width
  const height = canvas.height
  const stepX = width / (data.length - 1)
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  
  data.forEach((value, index) => {
    const x = index * stepX
    const y = height - ((value - min) / range) * height
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  
  ctx.stroke()
}

const drawCashFlowChart = () => {
  const canvas = cashFlowChart.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Sample cash flow data
  const data = [15000, 22000, 18000, 35000, 28000, 42000, 25000]
  const labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7']
  
  // Draw bars
  const barWidth = canvas.width / data.length * 0.8
  const maxValue = Math.max(...data)
  
  data.forEach((value, index) => {
    const barHeight = (value / maxValue) * (canvas.height - 40)
    const x = (index * canvas.width / data.length) + (canvas.width / data.length - barWidth) / 2
    const y = canvas.height - barHeight - 20
    
    ctx.fillStyle = '#3182ce'
    ctx.fillRect(x, y, barWidth, barHeight)
    
    // Draw value labels
    ctx.fillStyle = '#4a5568'
    ctx.font = '12px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(`$${(value/1000).toFixed(0)}K`, x + barWidth/2, y - 5)
  })
}

const drawRiskChart = () => {
  const canvas = riskChart.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Pie chart data
  const data = [65, 25, 10] // Low, Medium, High risk percentages
  const colors = ['#10b981', '#f59e0b', '#ef4444']
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2
  const radius = Math.min(centerX, centerY) - 20
  
  let currentAngle = 0
  
  data.forEach((value, index) => {
    const sliceAngle = (value / 100) * 2 * Math.PI
    
    ctx.beginPath()
    ctx.moveTo(centerX, centerY)
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle)
    ctx.closePath()
    ctx.fillStyle = colors[index]
    ctx.fill()
    
    currentAngle += sliceAngle
  })
}

const drawProcessingChart = () => {
  const canvas = processingChart.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Line chart for invoice processing volume
  const data = [120, 135, 125, 140, 155, 145, 160, 150, 165, 170, 158, 175]
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  
  ctx.strokeStyle = '#3182ce'
  ctx.lineWidth = 3
  ctx.beginPath()
  
  const stepX = canvas.width / (data.length - 1)
  const maxValue = Math.max(...data)
  const minValue = Math.min(...data)
  const range = maxValue - minValue
  
  data.forEach((value, index) => {
    const x = index * stepX
    const y = canvas.height - 40 - ((value - minValue) / range) * (canvas.height - 80)
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
    
    // Draw points
    ctx.fillStyle = '#3182ce'
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, 2 * Math.PI)
    ctx.fill()
  })
  
  ctx.stroke()
}

const drawAgingChart = () => {
  const canvas = agingChart.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Donut chart for aging
  const data = [180000, 85000, 45000, 25000]
  const colors = ['#10b981', '#f59e0b', '#ef4444', '#dc2626']
  const total = data.reduce((sum, value) => sum + value, 0)
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2
  const outerRadius = Math.min(centerX, centerY) - 20
  const innerRadius = outerRadius * 0.6
  
  let currentAngle = 0
  
  data.forEach((value, index) => {
    const sliceAngle = (value / total) * 2 * Math.PI
    
    ctx.beginPath()
    ctx.arc(centerX, centerY, outerRadius, currentAngle, currentAngle + sliceAngle)
    ctx.arc(centerX, centerY, innerRadius, currentAngle + sliceAngle, currentAngle, true)
    ctx.closePath()
    ctx.fillStyle = colors[index]
    ctx.fill()
    
    currentAngle += sliceAngle
  })
}

const refreshInsights = () => {
  // Simulate AI insights refresh
  aiInsights.value = [
    {
      id: Date.now(),
      icon: '🔄',
      title: 'Insights Refreshed',
      message: 'AI analysis updated with latest data',
      priority: 'info',
      action: null,
      actionText: ''
    }
  ]
  setTimeout(() => {
    // Restore original insights after 3 seconds
    aiInsights.value = [
      {
        id: 1,
        icon: '⚠️',
        title: 'High Risk Vendor Alert',
        message: 'ABC Corp has exceeded credit limit by $15,000',
        priority: 'high',
        action: 'review_vendor',
        actionText: 'Review Now'
      },
      {
        id: 2,
        icon: '💡',
        title: 'Payment Optimization',
        message: '5 vendors offer early payment discounts this week',
        priority: 'medium',
        action: 'view_discounts',
        actionText: 'View Opportunities'
      }
    ]
  }, 3000)
}

const exportReport = () => {
  // Generate analytics report
  const reportData = {
    date: new Date().toISOString(),
    totalOutstanding: kpiData.value.totalOutstanding,
    avgPaymentDays: kpiData.value.avgPaymentDays,
    onTimeRate: kpiData.value.onTimeRate,
    topVendors: topVendors.value
  }
  
  const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `ap-analytics-${new Date().toISOString().split('T')[0]}.json`
  link.click()
  URL.revokeObjectURL(url)
}

const exportAging = () => {
  const agingData = [
    { period: 'Current', amount: 180000 },
    { period: '1-30 Days', amount: 85000 },
    { period: '31-60 Days', amount: 45000 },
    { period: '60+ Days', amount: 25000 }
  ]
  
  const csv = convertToCSV(agingData)
  downloadCSV(csv, 'aging-report.csv')
}

const viewFraudAlerts = () => {
  router.push({ path: '/ap/invoices', query: { filter: 'high-risk' } })
}

const viewOptimizations = () => {
  router.push({ path: '/ap/payments', query: { filter: 'discounts' } })
}

const viewCashFlow = () => {
  router.push({ path: '/cash/forecast' })
}

const viewEfficiency = () => {
  alert('Process Efficiency Details:\n\n• Invoice processing time: 2.3 days (65% improvement)\n• Automation rate: 92%\n• Error rate: 0.8%\n• Cost per invoice: $8.45')
}

const viewAllVendors = () => {
  router.push('/ap/vendors')
}

const implementRecommendation = (rec: any) => {
  switch (rec.id) {
    case 1:
      router.push({ path: '/ap/payments', query: { vendor: 'abc-corp', action: 'schedule' } })
      break
    case 2:
      router.push({ path: '/ap/payments', query: { action: 'automate' } })
      break
    case 3:
      router.push({ path: '/ap/vendors', query: { action: 'consolidate' } })
      break
    default:
      alert(`Implementing: ${rec.title}`)
  }
}

const dismissRecommendation = (rec: any) => {
  const index = aiRecommendations.value.findIndex(r => r.id === rec.id)
  if (index > -1) {
    aiRecommendations.value.splice(index, 1)
  }
}

// Utility functions
const convertToCSV = (data: any[]) => {
  if (!data.length) return ''
  
  const headers = Object.keys(data[0])
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
  ].join('\n')
  
  return csvContent
}

const downloadCSV = (csv: string, filename: string) => {
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(url)
}

onMounted(async () => {
  await nextTick()
  drawCharts()
})
</script>