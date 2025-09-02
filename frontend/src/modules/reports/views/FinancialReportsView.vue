<template>
  <div class="financial-reports">
    <div class="reports-header">
      <div class="flex align-items-center">
        <i class="pi pi-chart-line text-3xl text-primary mr-3"></i>
        <h1 class="reports-title">Financial Reports</h1>
      </div>
      <div class="header-actions">
        <Button label="Export All" icon="pi pi-download" severity="secondary" @click="exportAll" />
        <Button label="New Report" icon="pi pi-plus" @click="showCreateDialog = true" />
      </div>
    </div>

    <div class="reports-grid">
      <Card v-for="report in financialReports" :key="report.id" class="report-card">
        <template #header>
          <div class="report-header">
            <i :class="report.icon" :style="{ color: report.color }" class="text-2xl"></i>
            <Tag :value="report.status" :severity="getStatusSeverity(report.status)" />
          </div>
        </template>
        <template #title>
          <h3>{{ report.name }}</h3>
        </template>
        <template #subtitle>
          <span>{{ report.category }}</span>
        </template>
        <template #content>
          <p class="report-description">{{ report.description }}</p>
          <div class="report-meta">
            <div class="meta-item">
              <i class="pi pi-clock"></i>
              <span>Last run: {{ formatDate(report.lastRun) }}</span>
            </div>
            <div class="meta-item">
              <i class="pi pi-calendar"></i>
              <span>{{ report.frequency }}</span>
            </div>
          </div>
        </template>
        <template #footer>
          <div class="report-actions">
            <Button label="Run" icon="pi pi-play" @click="runReport(report)" :loading="report.running" />
            <Button label="View" icon="pi pi-eye" severity="info" @click="viewReport(report)" />
            <Button label="Schedule" icon="pi pi-calendar" severity="secondary" @click="scheduleReport(report)" />
          </div>
        </template>
      </Card>
    </div>

    <Dialog v-model:visible="showCreateDialog" modal header="Create Financial Report" :style="{ width: '40rem' }">
      <div class="create-form">
        <div class="field">
          <label>Report Name</label>
          <InputText v-model="newReport.name" class="w-full" />
        </div>
        <div class="field">
          <label>Category</label>
          <Dropdown v-model="newReport.category" :options="categories" class="w-full" />
        </div>
        <div class="field">
          <label>Description</label>
          <Textarea v-model="newReport.description" rows="3" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showCreateDialog = false" />
        <Button label="Create" @click="createReport" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Textarea from 'primevue/textarea'
import Tag from 'primevue/tag'
import { useToast } from 'primevue/usetoast'

const showCreateDialog = ref(false)
const toast = useToast()

const financialReports = ref([
  {
    id: 'balance-sheet',
    name: 'Balance Sheet',
    category: 'Financial Statements',
    description: 'Statement of financial position showing assets, liabilities, and equity',
    icon: 'pi pi-chart-bar',
    color: '#2196F3',
    status: 'Active',
    lastRun: '2023-11-15T10:30:00',
    frequency: 'Monthly',
    running: false
  },
  {
    id: 'income-statement',
    name: 'Income Statement',
    category: 'Financial Statements',
    description: 'Profit and loss statement showing revenues and expenses',
    icon: 'pi pi-trending-up',
    color: '#4CAF50',
    status: 'Active',
    lastRun: '2023-11-15T09:15:00',
    frequency: 'Monthly',
    running: false
  },
  {
    id: 'cash-flow',
    name: 'Cash Flow Statement',
    category: 'Financial Statements',
    description: 'Statement showing cash inflows and outflows',
    icon: 'pi pi-wallet',
    color: '#FF9800',
    status: 'Active',
    lastRun: '2023-11-14T16:45:00',
    frequency: 'Monthly',
    running: false
  },
  {
    id: 'trial-balance',
    name: 'Trial Balance',
    category: 'General Ledger',
    description: 'List of all accounts with their debit and credit balances',
    icon: 'pi pi-list',
    color: '#9C27B0',
    status: 'Active',
    lastRun: '2023-11-15T08:00:00',
    frequency: 'Daily',
    running: false
  },
  {
    id: 'budget-variance',
    name: 'Budget vs Actual',
    category: 'Budget Analysis',
    description: 'Comparison of budgeted amounts with actual results',
    icon: 'pi pi-chart-pie',
    color: '#607D8B',
    status: 'Active',
    lastRun: '2023-11-13T14:20:00',
    frequency: 'Weekly',
    running: false
  },
  {
    id: 'financial-ratios',
    name: 'Financial Ratios',
    category: 'Analysis',
    description: 'Key financial ratios and performance indicators',
    icon: 'pi pi-calculator',
    color: '#795548',
    status: 'Draft',
    lastRun: '2023-11-10T11:30:00',
    frequency: 'Monthly',
    running: false
  }
])

const newReport = ref({
  name: '',
  category: '',
  description: ''
})

const categories = ref([
  'Financial Statements',
  'General Ledger',
  'Budget Analysis',
  'Analysis',
  'Compliance'
])

const runReport = async (report: any) => {
  report.running = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    report.lastRun = new Date().toISOString()
    toast.add({
      severity: 'success',
      summary: 'Report Generated',
      detail: `${report.name} has been generated successfully`,
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Generation Failed',
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

const scheduleReport = (report: any) => {
  console.log('Scheduling report:', report.name)
}

const createReport = () => {
  financialReports.value.push({
    id: `report-${Date.now()}`,
    name: newReport.value.name,
    category: newReport.value.category,
    description: newReport.value.description,
    icon: 'pi pi-file',
    color: '#6c757d',
    status: 'Draft',
    lastRun: new Date().toISOString(),
    frequency: 'Manual',
    running: false
  })
  
  newReport.value = { name: '', category: '', description: '' }
  showCreateDialog.value = false
}

const exportAll = () => {
  console.log('Exporting all financial reports')
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const getStatusSeverity = (status: string) => {
  const severities = {
    Active: 'success',
    Draft: 'warning',
    Archived: 'secondary'
  }
  return severities[status] || 'info'
}
</script>

<style scoped>
.financial-reports {
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

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.report-card {
  transition: transform 0.2s;
}

.report-card:hover {
  transform: translateY(-2px);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--surface-50);
}

.report-description {
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
}

.report-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.report-actions {
  display: flex;
  gap: 0.5rem;
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

.field label {
  font-weight: 600;
  color: var(--text-color-secondary);
}

@media (max-width: 768px) {
  .financial-reports {
    padding: 1rem;
  }
  
  .reports-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .reports-grid {
    grid-template-columns: 1fr;
  }
  
  .report-actions {
    flex-direction: column;
  }
}
</style>