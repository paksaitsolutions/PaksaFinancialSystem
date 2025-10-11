<template>
  <UnifiedDashboard 
    title="General Ledger" 
    subtitle="Manage your chart of accounts and journal entries"
  >
    <template #actions>
      <Button label="New Journal Entry" icon="pi pi-plus" class="btn-primary" @click="navigateToJournalEntry" />
    </template>
    
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
              <Button label="Chart of Accounts" icon="pi pi-list" class="action-btn" @click="navigateToChartOfAccounts" />
              <Button label="Trial Balance" icon="pi pi-calculator" class="action-btn btn-secondary" @click="navigateToTrialBalance" />
              <Button label="Financial Statements" icon="pi pi-chart-line" class="action-btn" @click="navigateToFinancialStatements" />
            </div>
          </template>
        </Card>
        <Card>
          <template #header>
            <h3 class="card-title">Recent Journal Entries</h3>
          </template>
          <template #content>
            <DataTable :value="recentEntries" :rows="5" class="compact-table">
              <Column field="date" header="Date" />
              <Column field="reference" header="Reference" />
              <Column field="description" header="Description" />
              <Column field="amount" header="Amount" />
            </DataTable>
          </template>
        </Card>
      </div>
    </template>
  </UnifiedDashboard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const stats = ref({
  totalAccounts: 0,
  journalEntries: 0,
  trialBalance: '0',
  openPeriods: 0
})

const dashboardMetrics = computed(() => [
  {
    id: 'accounts',
    icon: 'pi pi-book',
    value: stats.value.totalAccounts,
    label: 'Total Accounts',
    color: 'var(--primary-500)'
  },
  {
    id: 'entries',
    icon: 'pi pi-pencil',
    value: stats.value.journalEntries,
    label: 'Journal Entries',
    color: 'var(--success-500)'
  },
  {
    id: 'balance',
    icon: 'pi pi-calculator',
    value: `$${stats.value.trialBalance}`,
    label: 'Trial Balance',
    color: 'var(--warning-500)'
  },
  {
    id: 'periods',
    icon: 'pi pi-chart-line',
    value: stats.value.openPeriods,
    label: 'Open Periods',
    color: 'var(--info-500)'
  }
])

const recentEntries = ref([])
const loading = ref(false)

const loadDashboardData = async () => {
  loading.value = true
  try {
    const [statsResponse, entriesResponse] = await Promise.all([
      fetch('http://localhost:8000/api/v1/gl/dashboard/stats'),
      fetch('http://localhost:8000/api/v1/gl/dashboard/recent-entries')
    ])
    
    if (statsResponse.ok) {
      stats.value = await statsResponse.json()
    }
    
    if (entriesResponse.ok) {
      recentEntries.value = await entriesResponse.json()
    }
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboardData()
})

const navigateToJournalEntry = () => router.push('/accounting/journal-entry')
const navigateToChartOfAccounts = () => router.push('/gl/chart-of-accounts')
const navigateToTrialBalance = () => router.push('/gl/trial-balance')
const navigateToFinancialStatements = () => router.push('/gl/financial-statements')
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