<template>
  <div class="reports-view">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="loading-header">
        <div class="skeleton-header"></div>
      </div>
      <div class="loading-stats">
        <div v-for="i in 4" :key="i" class="skeleton-stat"></div>
      </div>
      <div class="loading-modules">
        <div v-for="i in 6" :key="i" class="skeleton-module"></div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <Card>
        <template #content>
          <div class="error-content">
            <i class="pi pi-exclamation-triangle text-4xl text-red-500 mb-3"></i>
            <h3>Error Loading Reports</h3>
            <p>{{ error }}</p>
            <Button label="Retry" icon="pi pi-refresh" @click="onMounted" />
          </div>
        </template>
      </Card>
    </div>

    <!-- Main Content -->
    <div v-else>
    <!-- Header -->
    <div class="reports-header">
      <div class="flex align-items-center">
        <i class="pi pi-file-pdf text-3xl text-primary mr-3"></i>
        <h1 class="reports-title">All Reports</h1>
      </div>
      <div class="header-actions">
        <Button label="Schedule Report" icon="pi pi-calendar" severity="secondary" @click="showScheduleDialog = true" />
        <Button label="Create Report" icon="pi pi-plus" @click="showCreateDialog = true" />
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="stats-grid">
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <i class="pi pi-file text-2xl text-blue-500"></i>
            <div class="stat-info">
              <div class="stat-value">{{ totalReports }}</div>
              <div class="stat-label">Total Reports</div>
            </div>
          </div>
        </template>
      </Card>
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <i class="pi pi-clock text-2xl text-green-500"></i>
            <div class="stat-info">
              <div class="stat-value">{{ scheduledReports }}</div>
              <div class="stat-label">Scheduled</div>
            </div>
          </div>
        </template>
      </Card>
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <i class="pi pi-chart-line text-2xl text-orange-500"></i>
            <div class="stat-info">
              <div class="stat-value">{{ reportsThisMonth }}</div>
              <div class="stat-label">This Month</div>
            </div>
          </div>
        </template>
      </Card>
      <Card class="stat-card">
        <template #content>
          <div class="stat-content">
            <i class="pi pi-users text-2xl text-purple-500"></i>
            <div class="stat-info">
              <div class="stat-value">{{ activeUsers }}</div>
              <div class="stat-label">Active Users</div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Module-wise Reports -->
    <div class="modules-grid">
      <Card v-for="module in modules" :key="module.id" class="module-card">
        <template #header>
          <div class="module-header">
            <div class="module-icon">
              <i :class="module.icon" :style="{ color: module.color }"></i>
            </div>
            <div class="module-info">
              <h3 class="module-title">{{ module.name }}</h3>
              <span class="module-count">{{ module.reports.length }} reports</span>
            </div>
          </div>
        </template>
        <template #content>
          <div class="module-content">
            <div class="reports-list">
              <div v-for="report in module.reports.slice(0, 5)" :key="report.id" class="report-item">
                <div class="report-info">
                  <span class="report-name">{{ report.name }}</span>
                  <span class="report-type">{{ report.type }}</span>
                </div>
                <div class="report-actions">
                  <Button icon="pi pi-play" size="small" @click="runReport(report)" :loading="report.running" />
                  <Button icon="pi pi-eye" size="small" severity="info" @click="viewReport(report)" />
                </div>
              </div>
            </div>
            <div v-if="module.reports.length > 5" class="show-more">
              <Button :label="`View all ${module.reports.length} reports`" severity="secondary" size="small" @click="viewModuleReports(module)" />
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Recent Activity -->
    <Card class="activity-card">
      <template #header>
        <h3 class="p-4 m-0">Recent Report Activity</h3>
      </template>
      <template #content>
        <DataTable :value="recentActivity" responsiveLayout="scroll" :paginator="true" :rows="10">
          <Column field="timestamp" header="Time">
            <template #body="{ data }">
              {{ formatTime(data.timestamp) }}
            </template>
          </Column>
          <Column field="user" header="User"></Column>
          <Column field="action" header="Action">
            <template #body="{ data }">
              <Tag :value="data.action" :severity="getActionSeverity(data.action)" />
            </template>
          </Column>
          <Column field="report" header="Report"></Column>
          <Column field="module" header="Module">
            <template #body="{ data }">
              <Chip :label="data.module" />
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

    <!-- Create Report Dialog -->
    <Dialog v-model:visible="showCreateDialog" modal header="Create New Report" :style="{ width: '50rem' }">
      <div class="create-form">
        <div class="field">
          <label class="block text-900 font-medium mb-2">Report Name *</label>
          <InputText v-model="newReport.name" placeholder="Enter report name" class="w-full" />
        </div>
        <div class="field">
          <label class="block text-900 font-medium mb-2">Module *</label>
          <Dropdown v-model="newReport.module" :options="moduleOptions" optionLabel="label" optionValue="value" placeholder="Select module" class="w-full" />
        </div>
        <div class="field">
          <label class="block text-900 font-medium mb-2">Report Type *</label>
          <Dropdown v-model="newReport.type" :options="reportTypes" optionLabel="label" optionValue="value" placeholder="Select type" class="w-full" />
        </div>
        <div class="field">
          <label class="block text-900 font-medium mb-2">Description</label>
          <Textarea v-model="newReport.description" rows="3" placeholder="Enter description" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showCreateDialog = false" />
        <Button label="Create Report" @click="createReport" :loading="creating" />
      </template>
    </Dialog>

    <!-- Schedule Dialog -->
    <Dialog v-model:visible="showScheduleDialog" modal header="Scheduled Reports" :style="{ width: '60rem' }">
      <DataTable :value="scheduledReportsList" responsiveLayout="scroll">
        <Column field="name" header="Report Name"></Column>
        <Column field="module" header="Module"></Column>
        <Column field="schedule" header="Schedule"></Column>
        <Column field="nextRun" header="Next Run">
          <template #body="{ data }">
            {{ formatTime(data.nextRun) }}
          </template>
        </Column>
        <Column header="Actions">
          <template #body="{ data }">
            <div class="flex gap-2">
              <Button icon="pi pi-pause" size="small" severity="warning" @click="pauseSchedule(data)" />
              <Button icon="pi pi-pencil" size="small" severity="info" @click="editSchedule(data)" />
            </div>
          </template>
        </Column>
      </DataTable>
    </Dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Textarea from 'primevue/textarea'
import Tag from 'primevue/tag'
import Chip from 'primevue/chip'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const toast = useToast()

// Dialog states
const showCreateDialog = ref(false)
const showScheduleDialog = ref(false)
const creating = ref(false)
const loading = ref(true)
const error = ref('')

// Form data
const newReport = ref({
  name: '',
  module: '',
  type: '',
  description: ''
})

// Module data with all reports
const modules = ref([
  {
    id: 'general-ledger',
    name: 'General Ledger',
    icon: 'pi pi-book',
    color: '#2196F3',
    reports: [
      { id: 'trial-balance', name: 'Trial Balance', type: 'Financial', running: false },
      { id: 'chart-accounts', name: 'Chart of Accounts', type: 'Reference', running: false },
      { id: 'journal-entries', name: 'Journal Entries', type: 'Transaction', running: false },
      { id: 'gl-summary', name: 'GL Summary', type: 'Summary', running: false },
      { id: 'account-balances', name: 'Account Balances', type: 'Financial', running: false },
      { id: 'period-close', name: 'Period Close Report', type: 'Process', running: false }
    ]
  },
  {
    id: 'accounts-payable',
    name: 'Accounts Payable',
    icon: 'pi pi-shopping-cart',
    color: '#4CAF50',
    reports: [
      { id: 'ap-aging', name: 'AP Aging Report', type: 'Aging', running: false },
      { id: 'vendor-summary', name: 'Vendor Summary', type: 'Summary', running: false },
      { id: 'payment-history', name: 'Payment History', type: 'Transaction', running: false },
      { id: 'outstanding-bills', name: 'Outstanding Bills', type: 'Outstanding', running: false },
      { id: 'vendor-performance', name: 'Vendor Performance', type: 'Analytics', running: false }
    ]
  },
  {
    id: 'accounts-receivable',
    name: 'Accounts Receivable',
    icon: 'pi pi-credit-card',
    color: '#FF9800',
    reports: [
      { id: 'ar-aging', name: 'AR Aging Report', type: 'Aging', running: false },
      { id: 'customer-summary', name: 'Customer Summary', type: 'Summary', running: false },
      { id: 'invoice-history', name: 'Invoice History', type: 'Transaction', running: false },
      { id: 'collections-report', name: 'Collections Report', type: 'Collections', running: false },
      { id: 'customer-analysis', name: 'Customer Analysis', type: 'Analytics', running: false }
    ]
  },
  {
    id: 'cash-management',
    name: 'Cash Management',
    icon: 'pi pi-wallet',
    color: '#9C27B0',
    reports: [
      { id: 'cash-flow', name: 'Cash Flow Statement', type: 'Financial', running: false },
      { id: 'bank-reconciliation', name: 'Bank Reconciliation', type: 'Reconciliation', running: false },
      { id: 'cash-position', name: 'Cash Position', type: 'Position', running: false },
      { id: 'transaction-summary', name: 'Transaction Summary', type: 'Summary', running: false }
    ]
  },
  {
    id: 'inventory',
    name: 'Inventory',
    icon: 'pi pi-box',
    color: '#607D8B',
    reports: [
      { id: 'inventory-valuation', name: 'Inventory Valuation', type: 'Valuation', running: false },
      { id: 'stock-movement', name: 'Stock Movement', type: 'Movement', running: false },
      { id: 'reorder-report', name: 'Reorder Report', type: 'Planning', running: false },
      { id: 'abc-analysis', name: 'ABC Analysis', type: 'Analytics', running: false }
    ]
  },
  {
    id: 'payroll',
    name: 'Payroll',
    icon: 'pi pi-users',
    color: '#795548',
    reports: [
      { id: 'payroll-summary', name: 'Payroll Summary', type: 'Summary', running: false },
      { id: 'employee-earnings', name: 'Employee Earnings', type: 'Earnings', running: false },
      { id: 'tax-report', name: 'Tax Report', type: 'Tax', running: false },
      { id: 'benefits-report', name: 'Benefits Report', type: 'Benefits', running: false }
    ]
  },
  {
    id: 'budget',
    name: 'Budget Management',
    icon: 'pi pi-calculator',
    color: '#E91E63',
    reports: [
      { id: 'budget-variance', name: 'Budget Variance', type: 'Variance', running: false },
      { id: 'budget-summary', name: 'Budget Summary', type: 'Summary', running: false },
      { id: 'forecast-report', name: 'Forecast Report', type: 'Forecast', running: false }
    ]
  },
  {
    id: 'tax',
    name: 'Tax Management',
    icon: 'pi pi-percentage',
    color: '#FF5722',
    reports: [
      { id: 'tax-liability', name: 'Tax Liability Report', type: 'Liability', running: false },
      { id: 'tax-compliance', name: 'Tax Compliance', type: 'Compliance', running: false },
      { id: 'tax-returns', name: 'Tax Returns', type: 'Returns', running: false }
    ]
  }
])

const recentActivity = ref([
  {
    timestamp: new Date(),
    user: 'John Doe',
    action: 'Generated',
    report: 'Trial Balance',
    module: 'General Ledger',
    status: 'Completed'
  },
  {
    timestamp: new Date(Date.now() - 300000),
    user: 'Jane Smith',
    action: 'Scheduled',
    report: 'AP Aging Report',
    module: 'Accounts Payable',
    status: 'Active'
  },
  {
    timestamp: new Date(Date.now() - 600000),
    user: 'Mike Johnson',
    action: 'Exported',
    report: 'Cash Flow Statement',
    module: 'Cash Management',
    status: 'Completed'
  }
])

const scheduledReportsList = ref([
  {
    name: 'Trial Balance',
    module: 'General Ledger',
    schedule: 'Daily at 9:00 AM',
    nextRun: new Date(Date.now() + 86400000)
  },
  {
    name: 'AP Aging Report',
    module: 'Accounts Payable',
    schedule: 'Weekly on Monday',
    nextRun: new Date(Date.now() + 604800000)
  }
])

// Options
const moduleOptions = computed(() => 
  modules.value.map(m => ({ label: m.name, value: m.id }))
)

const reportTypes = ref([
  { label: 'Financial', value: 'Financial' },
  { label: 'Summary', value: 'Summary' },
  { label: 'Transaction', value: 'Transaction' },
  { label: 'Analytics', value: 'Analytics' },
  { label: 'Compliance', value: 'Compliance' }
])

// Computed stats
const totalReports = computed(() => 
  modules.value.reduce((sum, module) => sum + module.reports.length, 0)
)

const scheduledReports = computed(() => scheduledReportsList.value.length)
const reportsThisMonth = computed(() => 47) // Mock data
const activeUsers = computed(() => 12) // Mock data

// Methods
const runReport = async (report: any) => {
  report.running = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    // Add to recent activity
    recentActivity.value.unshift({
      timestamp: new Date(),
      user: 'Current User',
      action: 'Generated',
      report: report.name,
      module: 'Module',
      status: 'Completed'
    })
    toast.add({
      severity: 'success',
      summary: 'Report Generated',
      detail: `${report.name} has been generated successfully`,
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Report Failed',
      detail: `Failed to generate ${report.name}`,
      life: 3000
    })
  } finally {
    report.running = false
  }
}

const viewReport = (report: any) => {
  console.log('Viewing report:', report.name)
}

const viewModuleReports = (module: any) => {
  router.push(`/reports/${module.id}`)
}

const createReport = async () => {
  creating.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    showCreateDialog.value = false
    newReport.value = { name: '', module: '', type: '', description: '' }
    toast.add({
      severity: 'success',
      summary: 'Report Created',
      detail: 'New report has been created successfully',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Creation Failed',
      detail: 'Failed to create report',
      life: 3000
    })
  } finally {
    creating.value = false
  }
}

const pauseSchedule = (report: any) => {
  console.log('Pausing schedule for:', report.name)
}

const editSchedule = (report: any) => {
  console.log('Editing schedule for:', report.name)
}

const formatTime = (timestamp: Date) => {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(timestamp))
}

const getActionSeverity = (action: string) => {
  const severities = {
    Generated: 'success',
    Scheduled: 'info',
    Exported: 'warning',
    Failed: 'danger'
  }
  return severities[action] || 'secondary'
}

const getStatusSeverity = (status: string) => {
  const severities = {
    Completed: 'success',
    Active: 'info',
    Failed: 'danger',
    Pending: 'warning'
  }
  return severities[status] || 'secondary'
}

onMounted(async () => {
  try {
    loading.value = true
    // Simulate loading data
    await new Promise(resolve => setTimeout(resolve, 1000))
    // Data is already loaded in refs, this simulates API call
  } catch (err) {
    error.value = 'Failed to load reports data'
    console.error('Error loading reports:', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.reports-view {
  padding: 1.5rem;
  background: var(--surface-ground);
  min-height: 100vh;
}

.reports-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--surface-card);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.reports-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
}

.stat-label {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.module-card {
  transition: transform 0.2s;
}

.module-card:hover {
  transform: translateY(-2px);
}

.module-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--surface-50);
}

.module-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: var(--surface-100);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.module-info {
  display: flex;
  flex-direction: column;
}

.module-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
}

.module-count {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.module-content {
  padding: 1rem;
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.report-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--surface-50);
  border-radius: 6px;
  border: 1px solid var(--surface-border);
}

.report-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.report-name {
  font-weight: 500;
  color: var(--text-color);
}

.report-type {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

.report-actions {
  display: flex;
  gap: 0.5rem;
}

.show-more {
  text-align: center;
  padding-top: 0.5rem;
  border-top: 1px solid var(--surface-border);
}

.activity-card {
  margin-bottom: 2rem;
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Loading States */
.loading-container {
  padding: 1.5rem;
}

.loading-header {
  margin-bottom: 2rem;
}

.skeleton-header {
  height: 80px;
  background: linear-gradient(90deg, var(--surface-200) 25%, var(--surface-100) 50%, var(--surface-200) 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
}

.loading-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.skeleton-stat {
  height: 120px;
  background: linear-gradient(90deg, var(--surface-200) 25%, var(--surface-100) 50%, var(--surface-200) 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
}

.loading-modules {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.skeleton-module {
  height: 300px;
  background: linear-gradient(90deg, var(--surface-200) 25%, var(--surface-100) 50%, var(--surface-200) 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 8px;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.error-container {
  padding: 2rem;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.error-content {
  text-align: center;
  padding: 2rem;
}

.error-content h3 {
  margin: 1rem 0;
  color: var(--text-color);
}

.error-content p {
  color: var(--text-color-secondary);
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  .reports-view {
    padding: 1rem;
  }
  
  .reports-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .modules-grid {
    grid-template-columns: 1fr;
  }
  
  .loading-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .loading-modules {
    grid-template-columns: 1fr;
  }
}
</style>