<template>
  <div class="gl-dashboard">
    <!-- Header -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-3xl font-bold text-900 m-0">General Ledger Dashboard</h1>
        <p class="text-600 mt-1 mb-0">Complete double-entry accounting system</p>
      </div>
      <div class="flex gap-2">
        <Button icon="pi pi-refresh" label="Refresh" @click="loadDashboardData" :loading="loading" />
        <Button icon="pi pi-plus" label="New Journal Entry" @click="$router.push('/gl/journal-entries/new')" />
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid mb-4">
      <div class="col-12 md:col-3">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Total Accounts</div>
                <div class="text-2xl font-bold text-900">{{ kpis.totalAccounts.toLocaleString() }}</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-arrow-up text-green-500 mr-1"></i>
                  {{ kpis.accountsChange }}% from last period
                </div>
              </div>
              <div class="bg-blue-100 border-round p-3">
                <i class="pi pi-book text-blue-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-3">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Journal Entries</div>
                <div class="text-2xl font-bold text-900">{{ kpis.journalEntries.toLocaleString() }}</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-arrow-up text-green-500 mr-1"></i>
                  {{ kpis.entriesChange }}% this month
                </div>
              </div>
              <div class="bg-green-100 border-round p-3">
                <i class="pi pi-file-edit text-green-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-3">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Trial Balance</div>
                <div class="text-2xl font-bold" :class="kpis.trialBalanceStatus === 'balanced' ? 'text-green-500' : 'text-red-500'">
                  {{ kpis.trialBalanceStatus === 'balanced' ? 'Balanced' : 'Out of Balance' }}
                </div>
                <div class="text-sm text-500 mt-1">
                  Difference: {{ formatCurrency(kpis.trialBalanceDifference) }}
                </div>
              </div>
              <div class="bg-purple-100 border-round p-3">
                <i class="pi pi-balance-scale text-purple-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-3">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Period Status</div>
                <div class="text-2xl font-bold text-900">{{ kpis.currentPeriod }}</div>
                <div class="text-sm text-500 mt-1">
                  <Tag :value="kpis.periodStatus" :severity="getPeriodSeverity(kpis.periodStatus)" />
                </div>
              </div>
              <div class="bg-orange-100 border-round p-3">
                <i class="pi pi-calendar text-orange-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Charts and Data -->
    <div class="grid">
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>Account Balances Trend</template>
          <template #content>
            <Chart type="line" :data="chartData" :options="chartOptions" class="h-20rem" />
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-4">
        <Card>
          <template #title>Account Types Distribution</template>
          <template #content>
            <Chart type="doughnut" :data="doughnutData" :options="doughnutOptions" class="h-20rem" />
          </template>
        </Card>
      </div>
    </div>

    <!-- Recent Activity & Quick Actions -->
    <div class="grid mt-4">
      <div class="col-12 lg:col-6">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Recent Journal Entries</span>
              <Button label="View All" text @click="$router.push('/gl/journal-entries')" />
            </div>
          </template>
          <template #content>
            <DataTable :value="recentEntries" class="p-datatable-sm">
              <Column field="entry_number" header="Entry #" />
              <Column field="date" header="Date">
                <template #body="{ data }">
                  {{ formatDate(data.date) }}
                </template>
              </Column>
              <Column field="description" header="Description" />
              <Column field="total_amount" header="Amount">
                <template #body="{ data }">
                  {{ formatCurrency(data.total_amount) }}
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
      </div>
      
      <div class="col-12 lg:col-6">
        <Card>
          <template #title>Quick Actions</template>
          <template #content>
            <div class="grid">
              <div class="col-6" v-for="action in quickActions" :key="action.label">
                <Button
                  :label="action.label"
                  :icon="action.icon"
                  class="w-full mb-3"
                  :severity="action.severity"
                  @click="handleQuickAction(action.action)"
                />
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import Chart from 'primevue/chart'
import { useGlAccountsStore } from '@/modules/general-ledger/store/gl-accounts'
import { formatCurrency } from '@/utils/formatters'

const router = useRouter()
const toast = useToast()
const glStore = useGlAccountsStore()
const loading = ref(false)

// KPI Data
const kpis = ref({
  totalAccounts: 0,
  accountsChange: 0,
  journalEntries: 0,
  entriesChange: 0,
  trialBalanceStatus: 'balanced',
  trialBalanceDifference: 0,
  currentPeriod: '',
  periodStatus: 'open'
})

// Chart Data
const chartData = ref({
  labels: [],
  datasets: []
})

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: function(value) {
          return formatCurrency(value)
        }
      }
    }
  }
})

const doughnutData = ref({
  labels: [],
  datasets: []
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

// Recent Entries
const recentEntries = ref([])

// Quick Actions
const quickActions = ref([
  { label: 'New Journal Entry', icon: 'pi pi-plus', action: 'new-entry', severity: 'primary' },
  { label: 'Trial Balance', icon: 'pi pi-balance-scale', action: 'trial-balance', severity: 'info' },
  { label: 'Chart of Accounts', icon: 'pi pi-book', action: 'chart-accounts', severity: 'secondary' },
  { label: 'Financial Statements', icon: 'pi pi-file-pdf', action: 'statements', severity: 'success' },
  { label: 'Period Close', icon: 'pi pi-calendar-times', action: 'period-close', severity: 'warning' },
  { label: 'Reconciliation', icon: 'pi pi-sync', action: 'reconciliation', severity: 'help' }
])

// Methods
const loadDashboardData = async () => {
  loading.value = true
  try {
    const [dashboardData, entriesData, balanceData] = await Promise.all([
      glStore.getDashboardKPIs(),
      glStore.getRecentJournalEntries(5),
      glStore.getTrialBalance()
    ])
    
    // Update KPIs
    kpis.value = {
      totalAccounts: dashboardData.total_accounts,
      accountsChange: dashboardData.accounts_change,
      journalEntries: dashboardData.journal_entries,
      entriesChange: dashboardData.entries_change,
      trialBalanceStatus: dashboardData.trial_balance_status,
      trialBalanceDifference: dashboardData.trial_balance_difference,
      currentPeriod: dashboardData.current_period,
      periodStatus: dashboardData.period_status
    }
    
    // Update chart data
    chartData.value = {
      labels: dashboardData.balance_trend.map(d => d.period),
      datasets: [
        {
          label: 'Assets',
          data: dashboardData.balance_trend.map(d => d.assets),
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Liabilities',
          data: dashboardData.balance_trend.map(d => d.liabilities),
          borderColor: '#EF4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4
        },
        {
          label: 'Equity',
          data: dashboardData.balance_trend.map(d => d.equity),
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4
        }
      ]
    }
    
    // Update doughnut data
    doughnutData.value = {
      labels: dashboardData.account_distribution.map(d => d.type),
      datasets: [{
        data: dashboardData.account_distribution.map(d => d.count),
        backgroundColor: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'],
        borderWidth: 0
      }]
    }
    
    recentEntries.value = entriesData
    
  } catch (error) {
    console.error('Error loading dashboard data:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load dashboard data',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const handleQuickAction = (action: string) => {
  const routes = {
    'new-entry': '/gl/journal-entries/new',
    'trial-balance': '/gl/trial-balance',
    'chart-accounts': '/gl/accounts',
    'statements': '/gl/financial-statements',
    'period-close': '/gl/period-close',
    'reconciliation': '/gl/reconciliation'
  }
  
  if (routes[action]) {
    router.push(routes[action])
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const getPeriodSeverity = (status: string) => {
  const severities = {
    open: 'success',
    closing: 'warning',
    closed: 'info'
  }
  return severities[status] || 'info'
}

const getStatusSeverity = (status: string) => {
  const severities = {
    draft: 'secondary',
    posted: 'success',
    pending: 'warning',
    rejected: 'danger'
  }
  return severities[status] || 'info'
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.gl-dashboard {
  padding: 1.5rem;
}
</style>
