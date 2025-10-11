<template>
  <UnifiedDashboard 
    title="Financial Dashboard" 
    subtitle="Welcome to Paksa Financial System"
  >
    <template #metrics>
      <UnifiedMetrics :metrics="dashboardMetrics" />
    </template>
    
    <template #content>



      <div class="content-grid">
        <Card>
          <template #header>
            <h3 class="card-title">Quick Actions</h3>
          </template>
          <template #content>
            <div class="actions-list">
              <Button label="New Invoice" icon="pi pi-plus" class="action-btn" @click="$router.push('/ar')" />
              <Button label="Record Payment" icon="pi pi-credit-card" class="action-btn btn-secondary" @click="$router.push('/ap')" />
              <Button label="Journal Entry" icon="pi pi-book" class="action-btn" @click="$router.push('/accounting/journal-entry')" />
              <Button label="View Reports" icon="pi pi-chart-bar" class="action-btn" @click="$router.push('/reports')" />
            </div>
          </template>
        </Card>

        <Card>
          <template #header>
            <h3 class="card-title">Recent Transactions</h3>
          </template>
          <template #content>
            <DataTable :value="recentTransactions" class="compact-table">
              <Column field="date" header="Date" />
              <Column field="description" header="Description" />
              <Column field="amount" header="Amount">
                <template #body="{ data }">
                  <span :class="data.amount >= 0 ? 'text-success' : 'text-error'">
                    {{ formatCurrency(data.amount) }}
                  </span>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </template>
  </UnifiedDashboard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const recentTransactions = ref([])
const dashboardStats = ref({
  totalRevenue: 0,
  netProfit: 0,
  customers: 0,
  overdue: 0
})

const dashboardMetrics = computed(() => [
  {
    id: 'revenue',
    icon: 'pi pi-dollar',
    value: `$${dashboardStats.value.totalRevenue.toLocaleString()}`,
    label: 'Total Revenue',
    color: 'var(--primary-500)'
  },
  {
    id: 'profit',
    icon: 'pi pi-chart-line',
    value: `$${dashboardStats.value.netProfit.toLocaleString()}`,
    label: 'Net Profit',
    color: 'var(--success-500)'
  },
  {
    id: 'customers',
    icon: 'pi pi-users',
    value: dashboardStats.value.customers.toLocaleString(),
    label: 'Customers',
    color: 'var(--info-500)'
  },
  {
    id: 'overdue',
    icon: 'pi pi-exclamation-triangle',
    value: `$${dashboardStats.value.overdue.toLocaleString()}`,
    label: 'Overdue',
    color: 'var(--error-500)'
  }
])
const loading = ref(false)

const loadDashboardData = async () => {
  loading.value = true
  try {
    const [statsResponse, transactionsResponse] = await Promise.all([
      fetch('http://localhost:8000/api/v1/dashboard/stats'),
      fetch('http://localhost:8000/api/v1/dashboard/recent-transactions')
    ])
    
    if (statsResponse.ok) {
      dashboardStats.value = await statsResponse.json()
    }
    
    if (transactionsResponse.ok) {
      recentTransactions.value = await transactionsResponse.json()
    }
  } catch (error) {
    console.error('Error loading dashboard data:', error)
    // Fallback data
    recentTransactions.value = [
      { date: '2024-01-15', description: 'Sales Invoice #1001', amount: 2500 },
      { date: '2024-01-14', description: 'Office Supplies', amount: -450 },
      { date: '2024-01-13', description: 'Customer Payment', amount: 1800 },
      { date: '2024-01-12', description: 'Utility Bill', amount: -320 },
      { date: '2024-01-11', description: 'Service Revenue', amount: 3200 }
    ]
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboardData()
})

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
}
</script>

<style scoped>
.content-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: var(--spacing-lg);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  margin: 0;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.action-btn {
  width: 100%;
  justify-content: flex-start;
}

:deep(.compact-table .p-datatable-tbody td) {
  padding: var(--spacing-sm) var(--spacing-md);
}

:deep(.compact-table .p-datatable-thead th) {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
}
</style>