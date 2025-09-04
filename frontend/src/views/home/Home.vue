<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Financial Dashboard</h1>
      <p>Welcome to Paksa Financial System - Real-time overview of your financial performance</p>
    </div>

    <!-- Summary Cards -->
    <div class="summary-cards">
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-dollar text-blue"></i>
            <span>Total Revenue</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-blue">${{ kpis.revenue.current.toLocaleString() }}</div>
          <div class="summary-change text-green">+{{ kpis.revenue.change_percent }}%</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-credit-card text-green"></i>
            <span>Accounts Receivable</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-green">${{ financialSummary.accounts_receivable.toLocaleString() }}</div>
          <div class="summary-change text-red">-3.2%</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-money-bill text-orange"></i>
            <span>Accounts Payable</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-orange">${{ financialSummary.accounts_payable.toLocaleString() }}</div>
          <div class="summary-change text-green">-8.1%</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-wallet text-purple"></i>
            <span>Cash Balance</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-purple">${{ financialSummary.cash_balance.toLocaleString() }}</div>
          <div class="summary-change text-green">+5.7%</div>
        </template>
      </Card>
    </div>

    <!-- Main Content Area -->
    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Recent Transactions</span>
            <Button 
              label="View All" 
              icon="pi pi-arrow-right" 
              iconPos="right" 
              class="p-button-text p-button-sm" 
              @click="loadRecentTransactions" 
            />
          </div>
        </template>
        <template #content>
          <DataTable 
            :value="recentTransactions" 
            :rows="5" 
            :paginator="false"
            responsiveLayout="scroll"
          >
            <Column field="date" header="Date">
              <template #body="{ data }">
                <span>{{ formatDate(data.date) }}</span>
              </template>
            </Column>
            <Column field="description" header="Description" />
            <Column field="amount" header="Amount">
              <template #body="{ data }">
                <span :class="data.amount >= 0 ? 'text-green' : 'text-red'">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Quick Actions</span>
          </div>
        </template>
        <template #content>
          <div class="quick-actions-grid">
            <Button 
              label="Create Invoice" 
              icon="pi pi-plus" 
              class="p-button-outlined action-btn"
              @click="$router.push('/ar')"
            />
            <Button 
              label="Record Payment" 
              icon="pi pi-credit-card" 
              class="p-button-outlined action-btn"
              @click="$router.push('/ap')"
            />
            <Button 
              label="Journal Entry" 
              icon="pi pi-book" 
              class="p-button-outlined action-btn"
              @click="$router.push('/accounting/journal-entry')"
            />
            <Button 
              label="View Reports" 
              icon="pi pi-chart-bar" 
              class="p-button-outlined action-btn"
              @click="$router.push('/reports')"
            />
          </div>
        </template>
      </Card>
    </div>


  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '@/utils/apiClient'

const loading = ref(false)
const kpis = ref({
  revenue: { current: 1234567, change_percent: 12.5 },
  expenses: { current: 987654, change_percent: 8.3 }
})

const financialSummary = ref({
  total_revenue: 1234567,
  accounts_receivable: 456789,
  accounts_payable: 234567,
  cash_balance: 789123,
  net_income: 246913
})

const recentTransactions = ref([])
const systemAlerts = ref([])

const revenueChartData = ref({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [{
    label: 'Revenue',
    data: [85000, 92000, 88000, 95000, 102000, 98000],
    borderColor: '#3B82F6',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    tension: 0.4
  }]
})

const expenseChartData = ref({
  labels: ['Salaries', 'Rent', 'Utilities', 'Marketing', 'Travel'],
  datasets: [{
    data: [45000, 12000, 3500, 8000, 2500],
    backgroundColor: ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6']
  }]
})

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: function(value: any) {
          return '$' + value.toLocaleString()
        }
      }
    }
  }
})

const doughnutOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
})

const loadDashboardData = async () => {
  loading.value = true
  try {
    const [kpiResponse, summaryResponse, transactionsResponse, alertsResponse] = await Promise.all([
      apiClient.get('/analytics/kpis'),
      apiClient.get('/analytics/financial-summary'),
      apiClient.get('/analytics/recent-transactions'),
      apiClient.get('/analytics/alerts')
    ])
    
    kpis.value = kpiResponse.data
    financialSummary.value = summaryResponse.data
    recentTransactions.value = transactionsResponse.data
    systemAlerts.value = alertsResponse.data
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  } finally {
    loading.value = false
  }
}

const loadRecentTransactions = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/analytics/recent-transactions')
    recentTransactions.value = response.data
  } catch (error) {
    console.error('Error loading transactions:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'Completed': return 'success'
    case 'Pending': return 'warning'
    case 'Failed': return 'danger'
    default: return 'info'
  }
}

const getAlertIcon = (type: string) => {
  switch (type) {
    case 'warning': return 'pi pi-exclamation-triangle text-orange-500'
    case 'error': return 'pi pi-times-circle text-red-500'
    case 'info': return 'pi pi-info-circle text-blue-500'
    case 'success': return 'pi pi-check-circle text-green-500'
    default: return 'pi pi-info-circle text-blue-500'
  }
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.dashboard-header p {
  color: #6b7280;
  margin: 0;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  height: 100%;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.summary-amount {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.summary-change {
  font-size: 0.875rem;
  font-weight: 600;
}

.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.content-card {
  height: fit-content;
}

.card-title-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.action-btn {
  width: 100%;
}

.text-blue { color: #3b82f6; }
.text-green { color: #10b981; }
.text-orange { color: #f59e0b; }
.text-purple { color: #8b5cf6; }
.text-red { color: #ef4444; }

@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }
  
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>