<template>
  <div class="reports-view">
    <!-- Header -->
    <div class="reports-header">
      <div class="flex align-items-center">
        <i class="pi pi-file-pdf text-3xl text-primary mr-3"></i>
        <h1 class="reports-title">AI/BI Reports</h1>
      </div>
      <div class="header-actions">
        <Button label="Schedule Report" icon="pi pi-calendar" severity="secondary" @click="showScheduleDialog = true" />
        <Button label="New Report" icon="pi pi-plus" @click="showNewReportDialog = true" />
      </div>
    </div>

    <!-- Filters -->
    <Card class="filters-card">
      <template #content>
        <div class="filters-grid">
          <div class="filter-item">
            <label class="filter-label">Category</label>
            <Dropdown v-model="selectedCategory" :options="categories" optionLabel="label" optionValue="value" placeholder="All Categories" class="w-full" showClear />
          </div>
          <div class="filter-item">
            <label class="filter-label">Status</label>
            <Dropdown v-model="selectedStatus" :options="statuses" optionLabel="label" optionValue="value" placeholder="All Status" class="w-full" showClear />
          </div>
          <div class="filter-item">
            <label class="filter-label">Search</label>
            <InputText v-model="searchQuery" placeholder="Search reports..." class="w-full" />
          </div>
          <div class="filter-item">
            <label class="filter-label">Actions</label>
            <Button label="Export All" icon="pi pi-download" severity="secondary" @click="exportReports" class="w-full" />
          </div>
        </div>
      </template>
    </Card>

    <!-- Reports Grid -->
    <div class="reports-grid">
      <Card v-for="(report, i) in filteredReports" :key="i" class="report-card">
        <template #header>
          <div class="report-header">
            <div class="report-icon">
              <i :class="getReportIcon(report.category)" :style="{ color: getReportColor(report.category) }"></i>
            </div>
            <div class="report-status">
              <Tag :value="report.status" :severity="getStatusSeverity(report.status)" />
            </div>
          </div>
        </template>
        <template #title>
          <h3 class="report-title">{{ report.title }}</h3>
        </template>
        <template #subtitle>
          <span class="report-category">{{ report.category }}</span>
        </template>
        <template #content>
          <div class="report-content">
            <div class="report-meta">
              <div class="meta-item">
                <i class="pi pi-clock text-500"></i>
                <span>Last run: {{ formatDate(report.lastRun) }}</span>
              </div>
              <div class="meta-item">
                <i class="pi pi-eye text-500"></i>
                <span>{{ report.views || 0 }} views</span>
              </div>
            </div>
            <div class="report-tags">
              <Chip v-for="(tag, j) in report.tags" :key="j" :label="tag" class="report-tag" />
            </div>
            <div class="report-description">{{ report.description || 'No description available' }}</div>
          </div>
        </template>
        <template #footer>
          <div class="report-actions">
            <Button label="Run" icon="pi pi-play" size="small" @click="runReport(report)" :loading="report.running" />
            <Button label="View" icon="pi pi-eye" size="small" severity="info" @click="viewReport(report)" />
            <Button label="Edit" icon="pi pi-pencil" size="small" severity="warning" @click="editReport(report)" />
            <Button icon="pi pi-ellipsis-v" size="small" severity="secondary" @click="showReportMenu($event, report)" />
          </div>
        </template>
      </Card>
    </div>

    <!-- Create Report Dialog -->
    <Dialog v-model:visible="showNewReportDialog" modal header="Create New Report" :style="{ width: '50rem' }">
      <div class="report-form">
        <div class="field">
          <label class="block text-900 font-medium mb-2">Report Title *</label>
          <InputText v-model="newReport.title" placeholder="Enter report title" class="w-full" :class="{ 'p-invalid': !newReport.title && submitted }" />
          <small v-if="!newReport.title && submitted" class="p-error">Title is required</small>
        </div>
        
        <div class="field">
          <label class="block text-900 font-medium mb-2">Category *</label>
          <Dropdown v-model="newReport.category" :options="categories" optionLabel="label" optionValue="value" placeholder="Select category" class="w-full" :class="{ 'p-invalid': !newReport.category && submitted }" />
          <small v-if="!newReport.category && submitted" class="p-error">Category is required</small>
        </div>
        
        <div class="field">
          <label class="block text-900 font-medium mb-2">Description</label>
          <Textarea v-model="newReport.description" rows="3" placeholder="Enter report description" class="w-full" />
        </div>
        
        <div class="field">
          <label class="block text-900 font-medium mb-2">Data Sources</label>
          <MultiSelect v-model="newReport.dataSources" :options="dataSources" optionLabel="label" optionValue="value" placeholder="Select data sources" class="w-full" />
        </div>
        
        <div class="field">
          <label class="block text-900 font-medium mb-2">Tags</label>
          <Chips v-model="newReport.tags" placeholder="Add tags" class="w-full" />
        </div>
        
        <div class="field">
          <label class="block text-900 font-medium mb-2">Schedule</label>
          <div class="schedule-options">
            <div class="flex align-items-center mb-2">
              <RadioButton v-model="newReport.schedule.type" inputId="manual" value="manual" />
              <label for="manual" class="ml-2">Manual</label>
            </div>
            <div class="flex align-items-center mb-2">
              <RadioButton v-model="newReport.schedule.type" inputId="daily" value="daily" />
              <label for="daily" class="ml-2">Daily</label>
            </div>
            <div class="flex align-items-center mb-2">
              <RadioButton v-model="newReport.schedule.type" inputId="weekly" value="weekly" />
              <label for="weekly" class="ml-2">Weekly</label>
            </div>
            <div class="flex align-items-center">
              <RadioButton v-model="newReport.schedule.type" inputId="monthly" value="monthly" />
              <label for="monthly" class="ml-2">Monthly</label>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="cancelNewReport" />
        <Button label="Create Report" @click="createNewReport" :loading="creating" />
      </template>
    </Dialog>

    <!-- Schedule Dialog -->
    <Dialog v-model:visible="showScheduleDialog" modal header="Schedule Reports" :style="{ width: '40rem' }">
      <DataTable :value="scheduledReports" responsiveLayout="scroll">
        <Column field="title" header="Report"></Column>
        <Column field="schedule" header="Schedule"></Column>
        <Column field="nextRun" header="Next Run">
          <template #body="{ data }">
            {{ formatDate(data.nextRun) }}
          </template>
        </Column>
        <Column header="Actions">
          <template #body="{ data }">
            <Button icon="pi pi-pause" size="small" severity="warning" @click="pauseSchedule(data)" />
          </template>
        </Column>
      </DataTable>
    </Dialog>

    <!-- Context Menu -->
    <ContextMenu ref="reportMenu" :model="menuItems" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Dialog states
const showNewReportDialog = ref(false)
const showScheduleDialog = ref(false)
const submitted = ref(false)
const creating = ref(false)

// Filter states
const selectedCategory = ref(null)
const selectedStatus = ref(null)
const searchQuery = ref('')

// Menu
const reportMenu = ref()
const selectedReport = ref(null)

// Data
const reports = ref([
  {
    id: 'financial-summary',
    title: 'Financial Summary Report',
    category: 'Financial',
    status: 'Active',
    lastRun: '2023-11-15T10:30:00',
    tags: ['monthly', 'summary', 'executive'],
    description: 'Comprehensive financial overview with key metrics and trends',
    views: 245,
    running: false
  },
  {
    id: 'ai-insights',
    title: 'AI-Powered Business Insights',
    category: 'Analytics',
    status: 'Active',
    lastRun: '2023-11-14T15:45:00',
    tags: ['ai', 'insights', 'predictions'],
    description: 'Machine learning analysis of business patterns and forecasts',
    views: 189,
    running: false
  },
  {
    id: 'expense-analysis',
    title: 'Expense Analysis Dashboard',
    category: 'Financial',
    status: 'Active',
    lastRun: '2023-11-13T09:15:00',
    tags: ['expenses', 'analysis', 'cost-control'],
    description: 'Detailed breakdown of expenses with anomaly detection',
    views: 156,
    running: false
  },
  {
    id: 'customer-segmentation',
    title: 'Customer Segmentation Analysis',
    category: 'Analytics',
    status: 'Draft',
    lastRun: '2023-11-12T14:20:00',
    tags: ['customers', 'segmentation', 'behavior'],
    description: 'AI-driven customer behavior analysis and segmentation',
    views: 78,
    running: false
  },
  {
    id: 'predictive-analytics',
    title: 'Predictive Analytics Report',
    category: 'Analytics',
    status: 'Active',
    lastRun: '2023-11-11T11:05:00',
    tags: ['prediction', 'forecasting', 'trends'],
    description: 'Advanced predictive models for business forecasting',
    views: 203,
    running: false
  },
  {
    id: 'cash-flow-forecast',
    title: 'AI Cash Flow Forecast',
    category: 'Financial',
    status: 'Active',
    lastRun: '2023-11-10T16:30:00',
    tags: ['cash-flow', 'forecast', 'ai'],
    description: 'Intelligent cash flow predictions with scenario analysis',
    views: 167,
    running: false
  }
])

const scheduledReports = ref([
  {
    title: 'Financial Summary Report',
    schedule: 'Daily at 9:00 AM',
    nextRun: '2023-11-16T09:00:00'
  },
  {
    title: 'AI-Powered Business Insights',
    schedule: 'Weekly on Monday',
    nextRun: '2023-11-20T08:00:00'
  }
])

const newReport = ref({
  title: '',
  category: '',
  description: '',
  tags: [],
  dataSources: [],
  schedule: {
    type: 'manual'
  }
})

// Options
const categories = ref([
  { label: 'Financial', value: 'Financial' },
  { label: 'Analytics', value: 'Analytics' },
  { label: 'Operational', value: 'Operational' },
  { label: 'Compliance', value: 'Compliance' }
])

const statuses = ref([
  { label: 'Active', value: 'Active' },
  { label: 'Draft', value: 'Draft' },
  { label: 'Archived', value: 'Archived' }
])

const dataSources = ref([
  { label: 'General Ledger', value: 'gl' },
  { label: 'Accounts Payable', value: 'ap' },
  { label: 'Accounts Receivable', value: 'ar' },
  { label: 'Cash Management', value: 'cash' },
  { label: 'Inventory', value: 'inventory' },
  { label: 'Payroll', value: 'payroll' }
])

const menuItems = ref([
  {
    label: 'Duplicate',
    icon: 'pi pi-copy',
    command: () => duplicateReport(selectedReport.value)
  },
  {
    label: 'Export',
    icon: 'pi pi-download',
    command: () => exportReport(selectedReport.value)
  },
  {
    label: 'Archive',
    icon: 'pi pi-archive',
    command: () => archiveReport(selectedReport.value)
  },
  {
    separator: true
  },
  {
    label: 'Delete',
    icon: 'pi pi-trash',
    command: () => deleteReport(selectedReport.value)
  }
])

// Computed
const filteredReports = computed(() => {
  let filtered = reports.value
  
  if (selectedCategory.value) {
    filtered = filtered.filter(r => r.category === selectedCategory.value)
  }
  
  if (selectedStatus.value) {
    filtered = filtered.filter(r => r.status === selectedStatus.value)
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(r => 
      r.title.toLowerCase().includes(query) ||
      r.description.toLowerCase().includes(query) ||
      r.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }
  
  return filtered
})

// Methods
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getReportIcon = (category: string) => {
  const icons = {
    Financial: 'pi pi-chart-line',
    Analytics: 'pi pi-chart-bar',
    Operational: 'pi pi-cog',
    Compliance: 'pi pi-shield'
  }
  return icons[category] || 'pi pi-file'
}

const getReportColor = (category: string) => {
  const colors = {
    Financial: '#2196F3',
    Analytics: '#4CAF50',
    Operational: '#FF9800',
    Compliance: '#9C27B0'
  }
  return colors[category] || '#6c757d'
}

const getStatusSeverity = (status: string) => {
  const severities = {
    Active: 'success',
    Draft: 'warning',
    Archived: 'secondary'
  }
  return severities[status] || 'info'
}

const runReport = async (report: any) => {
  report.running = true
  try {
    // Simulate report execution
    await new Promise(resolve => setTimeout(resolve, 2000))
    report.lastRun = new Date().toISOString()
    report.views = (report.views || 0) + 1
  } finally {
    report.running = false
  }
}

const viewReport = (report: any) => {
  router.push(`/ai-bi/reports/${report.id}`)
}

const editReport = (report: any) => {
  router.push(`/ai-bi/reports/${report.id}/edit`)
}

const showReportMenu = (event: any, report: any) => {
  selectedReport.value = report
  reportMenu.value.show(event)
}

const duplicateReport = (report: any) => {
  const duplicate = {
    ...report,
    id: `${report.id}-copy-${Date.now()}`,
    title: `${report.title} (Copy)`,
    status: 'Draft',
    views: 0
  }
  reports.value.unshift(duplicate)
}

const exportReport = (report: any) => {
  // Simulate export
  const data = JSON.stringify(report, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${report.title}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const archiveReport = (report: any) => {
  report.status = 'Archived'
}

const deleteReport = (report: any) => {
  if (confirm(`Are you sure you want to delete "${report.title}"?`)) {
    const index = reports.value.findIndex(r => r.id === report.id)
    if (index > -1) {
      reports.value.splice(index, 1)
    }
  }
}

const exportReports = () => {
  const data = JSON.stringify(filteredReports.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'reports.json'
  a.click()
  URL.revokeObjectURL(url)
}

const createNewReport = async () => {
  submitted.value = true
  
  if (!newReport.value.title || !newReport.value.category) {
    return
  }
  
  creating.value = true
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const report = {
      id: `report-${Date.now()}`,
      title: newReport.value.title,
      category: newReport.value.category,
      status: 'Draft',
      description: newReport.value.description,
      tags: newReport.value.tags,
      lastRun: new Date().toISOString(),
      views: 0,
      running: false
    }
    
    reports.value.unshift(report)
    cancelNewReport()
  } finally {
    creating.value = false
  }
}

const cancelNewReport = () => {
  newReport.value = {
    title: '',
    category: '',
    description: '',
    tags: [],
    dataSources: [],
    schedule: { type: 'manual' }
  }
  submitted.value = false
  showNewReportDialog.value = false
}

const pauseSchedule = (report: any) => {
  console.log('Pausing schedule for:', report.title)
}

onMounted(() => {
  // Initialize component
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

.filters-card {
  margin-bottom: 2rem;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-label {
  font-weight: 600;
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.report-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--surface-50);
}

.report-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: var(--surface-100);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.report-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
}

.report-category {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.report-content {
  padding: 1rem;
}

.report-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.report-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.report-tag {
  font-size: 0.75rem;
}

.report-description {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  line-height: 1.4;
}

.report-actions {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  border-top: 1px solid var(--surface-border);
}

.report-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.schedule-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .reports-grid {
    grid-template-columns: 1fr;
  }
  
  .report-actions {
    flex-wrap: wrap;
  }
}
</style>
