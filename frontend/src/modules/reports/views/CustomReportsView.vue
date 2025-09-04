<template>
  <div class="custom-reports">
    <div class="reports-header">
      <div class="flex align-items-center">
        <i class="pi pi-wrench text-3xl text-primary mr-3"></i>
        <h1 class="reports-title">Custom Reports</h1>
      </div>
      <div class="header-actions">
        <Button label="Report Builder" icon="pi pi-plus" @click="showBuilder = true" />
      </div>
    </div>

    <div class="reports-grid">
      <Card v-for="report in customReports" :key="report.id" class="report-card">
        <template #header>
          <div class="report-header">
            <i :class="report.icon" :style="{ color: report.color }" class="text-2xl"></i>
            <Tag :value="report.type" severity="info" />
          </div>
        </template>
        <template #title>
          <h3>{{ report.name }}</h3>
        </template>
        <template #content>
          <p class="report-description">{{ report.description }}</p>
          <div class="report-meta">
            <div class="meta-item">
              <i class="pi pi-user"></i>
              <span>Created by: {{ report.createdBy }}</span>
            </div>
            <div class="meta-item">
              <i class="pi pi-calendar"></i>
              <span>{{ formatDate(report.createdDate) }}</span>
            </div>
          </div>
        </template>
        <template #footer>
          <div class="report-actions">
            <Button label="Run" icon="pi pi-play" @click="runReport(report)" :loading="report.running" />
            <Button icon="pi pi-print" @click="printCustomReport(report)" />
            <SplitButton label="Export" icon="pi pi-download" @click="exportCustomReport(report)" :model="getCustomReportExportOptions(report)" />
          </div>
        </template>
      </Card>
    </div>

    <Dialog v-model:visible="showBuilder" modal header="Report Builder" :style="{ width: '80rem' }">
      <div class="builder-content">
        <div class="builder-sidebar">
          <h4>Data Sources</h4>
          <div class="data-sources">
            <div v-for="source in dataSources" :key="source.id" class="source-item">
              <Checkbox v-model="selectedSources" :inputId="source.id" :value="source.id" />
              <label :for="source.id">{{ source.name }}</label>
            </div>
          </div>
        </div>
        <div class="builder-main">
          <h4>Report Configuration</h4>
          <div class="config-form">
            <div class="field">
              <label>Report Name</label>
              <InputText v-model="reportConfig.name" class="w-full" />
            </div>
            <div class="field">
              <label>Description</label>
              <Textarea v-model="reportConfig.description" rows="3" class="w-full" />
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showBuilder = false" />
        <Button label="Create Report" @click="createCustomReport" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useReportExport } from '@/composables/useReportExport'

const showBuilder = ref(false)
const selectedSources = ref([])

const customReports = ref([
  {
    id: 'custom-1',
    name: 'Monthly Revenue Analysis',
    description: 'Custom analysis of monthly revenue trends by product category',
    icon: 'pi pi-chart-line',
    color: '#2196F3',
    type: 'Analytics',
    createdBy: 'John Doe',
    createdDate: '2023-11-01',
    running: false
  },
  {
    id: 'custom-2',
    name: 'Vendor Payment Summary',
    description: 'Customized vendor payment report with aging analysis',
    icon: 'pi pi-users',
    color: '#4CAF50',
    type: 'Financial',
    createdBy: 'Jane Smith',
    createdDate: '2023-10-15',
    running: false
  }
])

const dataSources = ref([
  { id: 'gl', name: 'General Ledger' },
  { id: 'ap', name: 'Accounts Payable' },
  { id: 'ar', name: 'Accounts Receivable' },
  { id: 'inventory', name: 'Inventory' },
  { id: 'payroll', name: 'Payroll' }
])

const reportConfig = ref({
  name: '',
  description: ''
})

const formErrors = ref({
  name: '',
  sources: ''
})

const validateForm = () => {
  formErrors.value = { name: '', sources: '' }
  let isValid = true

  if (!reportConfig.value.name.trim()) {
    formErrors.value.name = 'Report name is required'
    isValid = false
  }

  if (selectedSources.value.length === 0) {
    formErrors.value.sources = 'At least one data source must be selected'
    isValid = false
  }

  return isValid
}

const runReport = async (report: any) => {
  report.running = true
  await new Promise(resolve => setTimeout(resolve, 2000))
  report.running = false
}

const createCustomReport = () => {
  if (!validateForm()) {
    return
  }

  customReports.value.push({
    id: `custom-${Date.now()}`,
    name: reportConfig.value.name,
    description: reportConfig.value.description,
    icon: 'pi pi-file',
    color: '#6c757d',
    type: 'Custom',
    createdBy: 'Current User',
    createdDate: new Date().toISOString().split('T')[0],
    running: false
  })
  
  reportConfig.value = { name: '', description: '' }
  selectedSources.value = []
  formErrors.value = { name: '', sources: '' }
  showBuilder.value = false
}

const { exportToCSV, exportToPDF, printReport } = useReportExport()

const exportCustomReport = (report: any) => {
  const data = [{
    'Report Name': report.name,
    'Type': report.type,
    'Created By': report.createdBy,
    'Created Date': formatDate(report.createdDate),
    'Description': report.description
  }]
  exportToPDF(report.name, data, report.name.replace(/\s+/g, '_'))
}

const printCustomReport = (report: any) => {
  const data = [{
    'Report Name': report.name,
    'Type': report.type,
    'Created By': report.createdBy,
    'Created Date': formatDate(report.createdDate),
    'Description': report.description
  }]
  printReport(report.name, data)
}

const getCustomReportExportOptions = (report: any) => [
  {
    label: 'Export to PDF',
    icon: 'pi pi-file-pdf',
    command: () => exportCustomReport(report)
  },
  {
    label: 'Export to Excel',
    icon: 'pi pi-file-excel',
    command: () => exportToCSV([{
      'Report Name': report.name,
      'Type': report.type,
      'Created By': report.createdBy,
      'Created Date': formatDate(report.createdDate),
      'Description': report.description
    }], report.name.replace(/\s+/g, '_'))
  }
]

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}
</script>

<style scoped>
.custom-reports {
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

.builder-content {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  min-height: 400px;
}

.builder-sidebar {
  border-right: 1px solid var(--surface-border);
  padding-right: 1rem;
}

.data-sources {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.source-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.config-form {
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
</style>