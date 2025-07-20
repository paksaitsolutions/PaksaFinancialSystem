<template>
  <div class="ar-analytics-dashboard">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>🤖 AR Intelligence Center</h1>
            <p>AI-powered insights and predictive analytics for accounts receivable</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-outline" @click="refreshData">🔄 Refresh</button>
            <button class="btn btn-secondary" @click="exportReport">📊 Export</button>
            <button class="btn btn-primary" @click="showPredictions = !showPredictions">
              {{ showPredictions ? '📈 Hide' : '🔮 Show' }} Predictions
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- AI Insights Panel -->
      <div class="ai-insights-panel">
        <div class="insights-header">
          <h3>🧠 AI Insights & Alerts</h3>
          <div class="insight-controls">
            <select v-model="selectedTimeframe" class="insight-select">
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
          </div>
        </div>
        
        <div class="insights-grid">
          <div v-for="insight in aiInsights" :key="insight.id" class="insight-card" :class="insight.priority">
            <div class="insight-icon">{{ insight.icon }}</div>
            <div class="insight-content">
              <h4>{{ insight.title }}</h4>
              <p>{{ insight.message }}</p>
              <div class="insight-metrics" v-if="insight.metrics">
                <span v-for="metric in insight.metrics" :key="metric.label" class="metric">
                  {{ metric.label }}: <strong>{{ metric.value }}</strong>
                </span>
              </div>
              <button v-if="insight.action" class="btn-action" @click="executeInsightAction(insight)">
                {{ insight.actionText }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Key Performance Indicators -->
      <div class="kpi-section">
        <h3>📊 Key Performance Indicators</h3>
        <div class="kpi-grid">
          <div class="kpi-card" v-for="kpi in kpis" :key="kpi.id">
            <div class="kpi-header">
              <span class="kpi-icon">{{ kpi.icon }}</span>
              <span class="kpi-title">{{ kpi.title }}</span>
            </div>
            <div class="kpi-value" :class="kpi.trend">{{ kpi.value }}</div>
            <div class="kpi-change">
              <span class="change-indicator" :class="kpi.trend">
                {{ kpi.trend === 'positive' ? '↗' : kpi.trend === 'negative' ? '↘' : '→' }}
              </span>
              <span class="change-text">{{ kpi.change }}</span>
            </div>
            <div class="kpi-target" v-if="kpi.target">
              Target: {{ kpi.target }}
            </div>
          </div>
        </div>
      </div>

      <!-- Predictive Analytics Section -->
      <div v-if="showPredictions" class="predictions-section">
        <h3>🔮 Predictive Analytics</h3>
        
        <div class="predictions-grid">
          <!-- Payment Forecasting -->
          <div class="prediction-card">
            <div class="card-header">
              <h4>💰 Payment Forecasting</h4>
              <span class="confidence-badge">85% Confidence</span>
            </div>
            <div class="forecast-chart">
              <div class="chart-placeholder">
                <div class="forecast-bars">
                  <div v-for="(forecast, index) in paymentForecasts" :key="index" class="forecast-bar">
                    <div class="bar" :style="{ height: forecast.percentage + '%' }" :class="forecast.risk"></div>
                    <span class="bar-label">{{ forecast.period }}</span>
                    <span class="bar-amount">{{ formatCurrency(forecast.amount) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Risk Assessment -->
          <div class="prediction-card">
            <div class="card-header">
              <h4>⚠️ Delinquency Risk</h4>
              <span class="risk-summary">{{ highRiskCount }} High Risk</span>
            </div>
            <div class="risk-breakdown">
              <div v-for="risk in riskBreakdown" :key="risk.level" class="risk-item">
                <div class="risk-indicator" :class="risk.level"></div>
                <div class="risk-details">
                  <span class="risk-label">{{ risk.label }}</span>
                  <span class="risk-count">{{ risk.count }} customers</span>
                  <span class="risk-amount">{{ formatCurrency(risk.amount) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Customer Segmentation -->
          <div class="prediction-card">
            <div class="card-header">
              <h4>👥 Customer Segmentation</h4>
              <span class="segment-info">AI-Powered</span>
            </div>
            <div class="segmentation-chart">
              <div v-for="segment in customerSegments" :key="segment.id" class="segment-item">
                <div class="segment-color" :style="{ backgroundColor: segment.color }"></div>
                <div class="segment-info">
                  <span class="segment-name">{{ segment.name }}</span>
                  <span class="segment-count">{{ segment.count }} customers</span>
                  <span class="segment-value">{{ formatCurrency(segment.value) }}</span>
                </div>
                <div class="segment-percentage">{{ segment.percentage }}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Advanced Analytics Charts -->
      <div class="analytics-charts">
        <div class="charts-grid">
          <!-- DSO Trend Analysis -->
          <div class="chart-card">
            <div class="chart-header">
              <h4>📈 DSO Trend Analysis</h4>
              <div class="chart-controls">
                <select v-model="dsoTimeframe" class="chart-select">
                  <option value="6months">6 Months</option>
                  <option value="12months">12 Months</option>
                  <option value="24months">24 Months</option>
                </select>
              </div>
            </div>
            <div class="chart-container">
              <div class="trend-chart">
                <div class="chart-line">
                  <div v-for="(point, index) in dsoTrend" :key="index" class="trend-point" 
                       :style="{ left: (index * 100 / (dsoTrend.length - 1)) + '%', bottom: point.percentage + '%' }">
                    <div class="point-tooltip">
                      {{ point.period }}: {{ point.value }} days
                    </div>
                  </div>
                </div>
                <div class="chart-grid">
                  <div v-for="i in 5" :key="i" class="grid-line" :style="{ bottom: (i * 20) + '%' }"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- Collection Effectiveness -->
          <div class="chart-card">
            <div class="chart-header">
              <h4>🎯 Collection Effectiveness</h4>
              <span class="effectiveness-score">CEI: 92.5%</span>
            </div>
            <div class="effectiveness-breakdown">
              <div v-for="metric in collectionMetrics" :key="metric.name" class="metric-item">
                <div class="metric-bar">
                  <div class="bar-fill" :style="{ width: metric.percentage + '%' }" :class="metric.status"></div>
                </div>
                <div class="metric-details">
                  <span class="metric-name">{{ metric.name }}</span>
                  <span class="metric-value">{{ metric.value }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Aging Analysis -->
          <div class="chart-card">
            <div class="chart-header">
              <h4>⏰ Aging Analysis</h4>
              <button class="btn-sm btn-outline" @click="drillDownAging">Drill Down</button>
            </div>
            <div class="aging-chart">
              <div v-for="bucket in agingBuckets" :key="bucket.range" class="aging-bucket">
                <div class="bucket-header">
                  <span class="bucket-range">{{ bucket.range }}</span>
                  <span class="bucket-amount">{{ formatCurrency(bucket.amount) }}</span>
                </div>
                <div class="bucket-bar">
                  <div class="bar-segment" :style="{ width: bucket.percentage + '%' }" :class="bucket.risk"></div>
                </div>
                <div class="bucket-details">
                  <span class="bucket-count">{{ bucket.invoiceCount }} invoices</span>
                  <span class="bucket-trend" :class="bucket.trendDirection">
                    {{ bucket.trend }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Items & Recommendations -->
      <div class="action-items-section">
        <h3>🎯 Recommended Actions</h3>
        <div class="actions-grid">
          <div v-for="action in recommendedActions" :key="action.id" class="action-card" :class="action.priority">
            <div class="action-header">
              <span class="action-icon">{{ action.icon }}</span>
              <div class="action-title">
                <h4>{{ action.title }}</h4>
                <span class="action-impact">{{ action.impact }}</span>
              </div>
              <span class="action-priority">{{ action.priority }}</span>
            </div>
            <div class="action-content">
              <p>{{ action.description }}</p>
              <div class="action-metrics">
                <span class="metric">Potential Impact: <strong>{{ action.potentialImpact }}</strong></span>
                <span class="metric">Timeline: <strong>{{ action.timeline }}</strong></span>
              </div>
            </div>
            <div class="action-footer">
              <button class="btn btn-sm btn-primary" @click="executeAction(action)">
                {{ action.actionText }}
              </button>
              <button class="btn btn-sm btn-outline" @click="scheduleAction(action)">
                Schedule
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Reactive state
const showPredictions = ref(true)
const selectedTimeframe = ref('month')
const dsoTimeframe = ref('12months')
const highRiskCount = ref(12)

// AI Insights
const aiInsights = ref([
  {
    id: 1,
    icon: '🚨',
    title: 'Critical Payment Risk Alert',
    message: '5 high-value customers showing 85%+ delinquency probability',
    priority: 'critical',
    metrics: [
      { label: 'Total at Risk', value: '$125,000' },
      { label: 'Avg Delay', value: '45 days' }
    ],
    action: 'review_critical',
    actionText: 'Review Now'
  },
  {
    id: 2,
    icon: '💡',
    title: 'Collection Opportunity',
    message: 'AI identified optimal collection timing for 15 accounts',
    priority: 'high',
    metrics: [
      { label: 'Success Rate', value: '92%' },
      { label: 'Potential Recovery', value: '$85,000' }
    ],
    action: 'optimize_collections',
    actionText: 'Optimize Now'
  },
  {
    id: 3,
    icon: '📈',
    title: 'Cash Flow Forecast',
    message: 'Expected $450K collections in next 30 days with 88% confidence',
    priority: 'medium',
    metrics: [
      { label: 'Confidence', value: '88%' },
      { label: 'Variance', value: '±$25K' }
    ],
    action: 'view_forecast',
    actionText: 'View Details'
  }
])

// KPIs
const kpis = ref([
  {
    id: 'dso',
    icon: '📅',
    title: 'Days Sales Outstanding',
    value: '32.5 days',
    change: '-2.3 days vs last month',
    trend: 'positive',
    target: '≤ 30 days'
  },
  {
    id: 'cei',
    icon: '🎯',
    title: 'Collection Effectiveness',
    value: '92.5%',
    change: '+1.8% vs last month',
    trend: 'positive',
    target: '≥ 90%'
  },
  {
    id: 'bad_debt',
    icon: '💸',
    title: 'Bad Debt Rate',
    value: '1.2%',
    change: '-0.3% vs last month',
    trend: 'positive',
    target: '≤ 2%'
  },
  {
    id: 'cash_collected',
    icon: '💰',
    title: 'Cash Collected MTD',
    value: '$1.2M',
    change: '+15% vs last month',
    trend: 'positive',
    target: '$1.5M'
  }
])

// Payment Forecasts
const paymentForecasts = ref([
  { period: 'Week 1', amount: 125000, percentage: 80, risk: 'low' },
  { period: 'Week 2', amount: 98000, percentage: 65, risk: 'medium' },
  { period: 'Week 3', amount: 156000, percentage: 95, risk: 'low' },
  { period: 'Week 4', amount: 87000, percentage: 55, risk: 'high' }
])

// Risk Breakdown
const riskBreakdown = ref([
  { level: 'critical', label: 'Critical Risk', count: 5, amount: 125000 },
  { level: 'high', label: 'High Risk', count: 12, amount: 285000 },
  { level: 'medium', label: 'Medium Risk', count: 28, amount: 450000 },
  { level: 'low', label: 'Low Risk', count: 156, amount: 1250000 }
])

// Customer Segments
const customerSegments = ref([
  { id: 1, name: 'Champions', count: 45, value: 850000, percentage: 35, color: '#10B981' },
  { id: 2, name: 'Loyal Customers', count: 78, value: 650000, percentage: 28, color: '#3B82F6' },
  { id: 3, name: 'Potential Loyalists', count: 52, value: 420000, percentage: 22, color: '#F59E0B' },
  { id: 4, name: 'At Risk', count: 23, value: 180000, percentage: 15, color: '#EF4444' }
])

// DSO Trend
const dsoTrend = ref([
  { period: 'Jan', value: 35.2, percentage: 70 },
  { period: 'Feb', value: 33.8, percentage: 65 },
  { period: 'Mar', value: 36.1, percentage: 75 },
  { period: 'Apr', value: 31.5, percentage: 58 },
  { period: 'May', value: 29.8, percentage: 52 },
  { period: 'Jun', value: 32.5, percentage: 62 }
])

// Collection Metrics
const collectionMetrics = ref([
  { name: 'Current Collections', value: '95%', percentage: 95, status: 'excellent' },
  { name: '1-30 Days', value: '88%', percentage: 88, status: 'good' },
  { name: '31-60 Days', value: '72%', percentage: 72, status: 'fair' },
  { name: '60+ Days', value: '45%', percentage: 45, status: 'poor' }
])

// Aging Buckets
const agingBuckets = ref([
  { range: 'Current', amount: 850000, percentage: 45, invoiceCount: 156, risk: 'low', trend: '+5%', trendDirection: 'positive' },
  { range: '1-30 Days', amount: 420000, percentage: 25, invoiceCount: 89, risk: 'medium', trend: '-2%', trendDirection: 'positive' },
  { range: '31-60 Days', amount: 285000, percentage: 18, invoiceCount: 45, risk: 'high', trend: '+8%', trendDirection: 'negative' },
  { range: '60+ Days', amount: 125000, percentage: 12, invoiceCount: 23, risk: 'critical', trend: '-12%', trendDirection: 'positive' }
])

// Recommended Actions
const recommendedActions = ref([
  {
    id: 1,
    icon: '📞',
    title: 'Proactive Customer Outreach',
    description: 'Contact 12 high-risk customers before they become overdue',
    impact: 'High Revenue Impact',
    priority: 'high',
    potentialImpact: '$85,000 recovery',
    timeline: '2-3 days',
    actionText: 'Start Outreach'
  },
  {
    id: 2,
    icon: '🤖',
    title: 'Automate Collection Workflow',
    description: 'Deploy AI-powered collection sequences for medium-risk accounts',
    impact: 'Efficiency Gain',
    priority: 'medium',
    potentialImpact: '40% time savings',
    timeline: '1 week',
    actionText: 'Deploy Automation'
  },
  {
    id: 3,
    icon: '💳',
    title: 'Payment Plan Offers',
    description: 'Offer flexible payment plans to 8 struggling customers',
    impact: 'Relationship Preservation',
    priority: 'medium',
    potentialImpact: '$45,000 retention',
    timeline: '3-5 days',
    actionText: 'Create Plans'
  }
])

// Methods
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

const executeInsightAction = (insight: any) => {
  switch (insight.action) {
    case 'review_critical':
      router.push('/ar/customers?filter=critical-risk')
      break
    case 'optimize_collections':
      router.push('/ar/collections/optimize')
      break
    case 'view_forecast':
      router.push('/ar/analytics/forecast')
      break
    default:
      alert(`Executing: ${insight.title}`)
  }
}

const executeAction = (action: any) => {
  alert(`Executing: ${action.title}`)
}

const scheduleAction = (action: any) => {
  alert(`Scheduling: ${action.title}`)
}

const drillDownAging = () => {
  router.push('/ar/reports/aging-detail')
}

const refreshData = () => {
  alert('Refreshing AI analytics data...')
}

const exportReport = () => {
  alert('Exporting analytics report...')
}

onMounted(() => {
  // Load analytics data
})
</script>

<style>
@import '/src/assets/styles/ar-advanced.css';

/* AI Analytics specific styles */
.ar-analytics-dashboard {
  min-height: 100vh;
  background: #f8fafc;
}

.ai-insights-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 32px;
  margin: 30px 0;
  color: white;
  position: relative;
  overflow: hidden;
}

.insights-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.insights-header h3 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
}

.insight-controls {
  display: flex;
  gap: 12px;
}

.insight-select {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.insight-card {
  background: rgba(255,255,255,0.15);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.2);
  transition: all 0.3s;
}

.insight-card:hover {
  transform: translateY(-2px);
  background: rgba(255,255,255,0.2);
}

.insight-card.critical {
  border-left: 4px solid #ff6b6b;
}

.insight-card.high {
  border-left: 4px solid #feca57;
}

.insight-card.medium {
  border-left: 4px solid #48dbfb;
}

.insight-icon {
  font-size: 2rem;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
}

.insight-content h4 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.insight-content p {
  margin: 0 0 12px 0;
  font-size: 0.95rem;
  opacity: 0.9;
  line-height: 1.4;
}

.insight-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.insight-metrics .metric {
  background: rgba(255,255,255,0.2);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.btn-action {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.btn-action:hover {
  background: rgba(255,255,255,0.3);
  transform: translateY(-1px);
}

/* KPI Section */
.kpi-section {
  margin: 40px 0;
}

.kpi-section h3 {
  margin-bottom: 24px;
  color: #2d3748;
  font-size: 1.3rem;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.kpi-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
  transition: all 0.3s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.1);
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.kpi-icon {
  font-size: 1.5rem;
}

.kpi-title {
  font-weight: 600;
  color: #4a5568;
  font-size: 0.9rem;
}

.kpi-value {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.kpi-value.positive { color: #10b981; }
.kpi-value.negative { color: #ef4444; }
.kpi-value.neutral { color: #6b7280; }

.kpi-change {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.change-indicator {
  font-size: 1.2rem;
}

.change-indicator.positive { color: #10b981; }
.change-indicator.negative { color: #ef4444; }

.change-text {
  font-size: 0.85rem;
  color: #6b7280;
}

.kpi-target {
  font-size: 0.8rem;
  color: #9ca3af;
  font-style: italic;
}

/* Predictions Section */
.predictions-section {
  margin: 40px 0;
}

.predictions-section h3 {
  margin-bottom: 24px;
  color: #2d3748;
  font-size: 1.3rem;
}

.predictions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.prediction-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h4 {
  margin: 0;
  color: #2d3748;
  font-size: 1.1rem;
}

.confidence-badge,
.risk-summary,
.segment-info {
  background: #e0f2fe;
  color: #0277bd;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Forecast Chart */
.forecast-chart {
  height: 200px;
  position: relative;
}

.forecast-bars {
  display: flex;
  align-items: end;
  height: 100%;
  gap: 16px;
  padding: 20px 0;
}

.forecast-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.bar {
  width: 100%;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s;
  min-height: 20px;
}

.bar.low { background: #10b981; }
.bar.medium { background: #f59e0b; }
.bar.high { background: #ef4444; }

.bar-label {
  margin-top: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #4a5568;
}

.bar-amount {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 4px;
}

/* Risk Breakdown */
.risk-breakdown {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.risk-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.risk-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.risk-indicator.critical { background: #ef4444; }
.risk-indicator.high { background: #f59e0b; }
.risk-indicator.medium { background: #3b82f6; }
.risk-indicator.low { background: #10b981; }

.risk-details {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.risk-label {
  font-weight: 600;
  color: #2d3748;
}

.risk-count,
.risk-amount {
  font-size: 0.85rem;
  color: #6b7280;
}

/* Customer Segmentation */
.segmentation-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.segment-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.segment-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.segment-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.segment-name {
  font-weight: 600;
  color: #2d3748;
}

.segment-count,
.segment-value {
  font-size: 0.8rem;
  color: #6b7280;
}

.segment-percentage {
  font-weight: 600;
  color: #4a5568;
}

/* Charts Section */
.analytics-charts {
  margin: 40px 0;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h4 {
  margin: 0;
  color: #2d3748;
  font-size: 1.1rem;
}

.chart-select {
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.85rem;
}

/* Action Items */
.action-items-section {
  margin: 40px 0;
}

.action-items-section h3 {
  margin-bottom: 24px;
  color: #2d3748;
  font-size: 1.3rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.action-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  border: 1px solid #e2e8f0;
  transition: all 0.3s;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.1);
}

.action-card.high {
  border-left: 4px solid #f59e0b;
}

.action-card.medium {
  border-left: 4px solid #3b82f6;
}

.action-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.action-icon {
  font-size: 1.5rem;
}

.action-title {
  flex: 1;
}

.action-title h4 {
  margin: 0 0 4px 0;
  color: #2d3748;
  font-size: 1rem;
}

.action-impact {
  font-size: 0.8rem;
  color: #6b7280;
}

.action-priority {
  background: #fef3c7;
  color: #92400e;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.action-content p {
  margin: 0 0 12px 0;
  color: #4a5568;
  line-height: 1.5;
}

.action-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.action-metrics .metric {
  font-size: 0.8rem;
  color: #6b7280;
}

.action-footer {
  display: flex;
  gap: 12px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .insights-grid,
  .kpi-grid,
  .predictions-grid,
  .charts-grid,
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .insight-card {
    flex-direction: column;
    text-align: center;
  }
  
  .forecast-bars {
    gap: 8px;
  }
  
  .action-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>