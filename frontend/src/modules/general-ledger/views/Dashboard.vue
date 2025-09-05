<template>
  <div class="gl-dashboard">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>General Ledger</h1>
        <p class="text-color-secondary">Manage your chart of accounts and journal entries</p>
      </div>
      <Button label="New Journal Entry" icon="pi pi-plus" @click="navigateToJournalEntry" />
    </div>

    <div class="grid">
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-book text-4xl text-blue-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.totalAccounts }}</div>
              <div class="text-color-secondary">Total Accounts</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-pencil text-4xl text-green-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.journalEntries }}</div>
              <div class="text-color-secondary">Journal Entries</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-calculator text-4xl text-orange-500 mb-3"></i>
              <div class="text-2xl font-bold">${{ stats.trialBalance }}</div>
              <div class="text-color-secondary">Trial Balance</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-chart-line text-4xl text-purple-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.openPeriods }}</div>
              <div class="text-color-secondary">Open Periods</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <div class="grid">
      <div class="col-12 lg:col-6">
        <Card>
          <template #title>Quick Actions</template>
          <template #content>
            <div class="quick-actions">
              <Button label="Chart of Accounts" icon="pi pi-list" class="w-full mb-2" @click="navigateToChartOfAccounts" />
              <Button label="Trial Balance" icon="pi pi-calculator" class="w-full mb-2 p-button-secondary" @click="navigateToTrialBalance" />
              <Button label="Financial Statements" icon="pi pi-chart-line" class="w-full p-button-success" @click="navigateToFinancialStatements" />
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-6">
        <Card>
          <template #title>Recent Journal Entries</template>
          <template #content>
            <DataTable :value="recentEntries" :rows="5">
              <Column field="date" header="Date" />
              <Column field="reference" header="Reference" />
              <Column field="description" header="Description" />
              <Column field="amount" header="Amount" />
            </DataTable>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const stats = ref({
  totalAccounts: 156,
  journalEntries: 1247,
  trialBalance: '2,456,789',
  openPeriods: 3
})

const recentEntries = ref([
  { date: '2024-01-15', reference: 'JE001', description: 'Office Rent Payment', amount: '$2,500.00' },
  { date: '2024-01-14', reference: 'JE002', description: 'Sales Revenue', amount: '$15,000.00' },
  { date: '2024-01-13', reference: 'JE003', description: 'Equipment Purchase', amount: '$8,500.00' },
  { date: '2024-01-12', reference: 'JE004', description: 'Utility Expense', amount: '$450.00' },
  { date: '2024-01-11', reference: 'JE005', description: 'Bank Interest', amount: '$125.00' }
])

const navigateToJournalEntry = () => router.push('/accounting/journal-entry')
const navigateToChartOfAccounts = () => router.push('/gl/chart-of-accounts')
const navigateToTrialBalance = () => router.push('/gl/trial-balance')
const navigateToFinancialStatements = () => router.push('/gl/financial-statements')
</script>

<style scoped>
.gl-dashboard {
  padding: 0;
}

.metric-card {
  text-align: center;
}

.quick-actions {
  display: flex;
  flex-direction: column;
}
</style>