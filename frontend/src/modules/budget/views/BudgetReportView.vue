<template>
  <div class="budget-reports">
    <div class="dashboard-header">
      <h1>Budget Reports</h1>
      <p>Generate comprehensive budget reports and variance analysis.</p>
    </div>

    <div class="reports-content">
      <!-- Report Filters -->
      <Card class="filter-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-filter"></i>
            <span>Report Filters</span>
          </div>
        </template>
        <template #content>
          <div class="grid">
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Report Type</label>
                <Dropdown v-model="selectedReport" :options="reportTypes" option-label="label" option-value="value" @change="generateReport" />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Period</label>
                <Dropdown v-model="selectedPeriod" :options="periodOptions" option-label="label" option-value="value" />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Budget Type</label>
                <Dropdown v-model="selectedType" :options="budgetTypes" option-label="label" option-value="value" />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>&nbsp;</label>
                <Button label="Generate Report" icon="pi pi-file-pdf" @click="generateReport" class="w-full" />
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Budget vs Actual Report -->
      <Card v-if="selectedReport === 'budget_vs_actual'" class="report-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Budget vs Actual Report</span>
            <Button label="Export PDF" icon="pi pi-download" size="small" @click="exportReport" />
          </div>
        </template>
        <template #content>
          <div class="report-summary">
            <div class="summary-cards">
              <div class="summary-item">
                <label>Total Budget</label>
                <span class="amount budget">{{ formatCurrency(reportData.totalBudget) }}</span>
              </div>
              <div class="summary-item">
                <label>Total Actual</label>
                <span class="amount actual">{{ formatCurrency(reportData.totalActual) }}</span>
              </div>
              <div class="summary-item">
                <label>Variance</label>
                <span class="amount variance" :class="reportData.variance >= 0 ? 'positive' : 'negative'">
                  {{ formatCurrency(reportData.variance) }}
                </span>
              </div>
              <div class="summary-item">
                <label>Variance %</label>
                <span class="percentage" :class="reportData.variancePercent >= 0 ? 'positive' : 'negative'">
                  {{ reportData.variancePercent.toFixed(1) }}%
                </span>
              </div>
            </div>
          </div>

          <div class="chart-section">
            <Chart type="bar" :data="chartData" :options="chartOptions" />
          </div>

          <div class="detailed-table">
            <DataTable :value="reportData.details" responsive-layout="scroll" :exportFilename="'budget-vs-actual-report'">
              <Column field="category" header="Category" sortable />
              <Column field="budget" header="Budget" sortable>
                <template #body="{ data }">
                  <span class="amount budget">{{ formatCurrency(data.budget) }}</span>
                </template>
              </Column>
              <Column field="actual" header="Actual" sortable>
                <template #body="{ data }">
                  <span class="amount actual">{{ formatCurrency(data.actual) }}</span>
                </template>
              </Column>
              <Column field="variance" header="Variance" sortable>
                <template #body="{ data }">
                  <span class="amount variance" :class="data.variance >= 0 ? 'positive' : 'negative'">
                    {{ formatCurrency(data.variance) }}
                  </span>
                </template>
              </Column>
              <Column field="variancePercent" header="Variance %" sortable>
                <template #body="{ data }">
                  <span class="percentage" :class="data.variancePercent >= 0 ? 'positive' : 'negative'">
                    {{ data.variancePercent.toFixed(1) }}%
                  </span>
                </template>
              </Column>
              <Column field="status" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getVarianceStatus(data.variancePercent)" />
                </template>
              </Column>
            </DataTable>
          </div>
        </template>
      </Card>

      <!-- Budget Summary Report -->
      <Card v-if="selectedReport === 'budget_summary'" class="report-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Budget Summary Report</span>
            <Button label="Export PDF" icon="pi pi-download" size="small" @click="exportReport" />
          </div>
        </template>
        <template #content>
          <div class="summary-grid">
            <div class="summary-section">
              <h4>By Budget Type</h4>
              <Chart type="doughnut" :data="typeChartData" :options="pieChartOptions" />
            </div>
            <div class="summary-section">
              <h4>By Status</h4>
              <Chart type="doughnut" :data="statusChartData" :options="pieChartOptions" />
            </div>
          </div>
          
          <DataTable :value="budgetSummary" responsive-layout="scroll">
            <Column field="name" header="Budget Name" sortable />
            <Column field="type" header="Type">
              <template #body="{ data }">
                <Tag :value="data.type" :severity="getTypeSeverity(data.type)" />
              </template>
            </Column>
            <Column field="amount" header="Amount" sortable>
              <template #body="{ data }">
                {{ formatCurrency(data.amount) }}
              </template>
            </Column>
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column field="utilization" header="Utilization">
              <template #body="{ data }">
                <ProgressBar :value="data.utilization" :class="getUtilizationClass(data.utilization)" />
                <span class="utilization-text">{{ data.utilization }}%</span>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'



const toast = useToast()

const selectedReport = ref('budget_vs_actual')
const selectedPeriod = ref('current_year')
const selectedType = ref(null)

const reportTypes = [
  { label: 'Budget vs Actual', value: 'budget_vs_actual' },
  { label: 'Budget Summary', value: 'budget_summary' },
  { label: 'Variance Analysis', value: 'variance_analysis' },
  { label: 'Utilization Report', value: 'utilization' }
]

const periodOptions = [
  { label: 'Current Year', value: 'current_year' },
  { label: 'Last Year', value: 'last_year' },
  { label: 'Q1 2024', value: 'q1_2024' },
  { label: 'Q2 2024', value: 'q2_2024' }
]

const budgetTypes = [
  { label: 'All Types', value: null },
  { label: 'Operational', value: 'OPERATIONAL' },
  { label: 'Capital', value: 'CAPITAL' },
  { label: 'Project', value: 'PROJECT' },
  { label: 'Department', value: 'DEPARTMENT' }
]

const reportData = ref({
  totalBudget: 500000,
  totalActual: 375000,
  variance: 125000,
  variancePercent: 25,
  details: [
    { category: 'Marketing', budget: 120000, actual: 95000, variance: 25000, variancePercent: 20.8, status: 'Under Budget' },
    { category: 'Operations', budget: 150000, actual: 140000, variance: 10000, variancePercent: 6.7, status: 'Under Budget' },
    { category: 'IT', budget: 100000, actual: 85000, variance: 15000, variancePercent: 15, status: 'Under Budget' },
    { category: 'HR', budget: 80000, actual: 55000, variance: 25000, variancePercent: 31.3, status: 'Under Budget' },
    { category: 'Facilities', budget: 50000, actual: 60000, variance: -10000, variancePercent: -20, status: 'Over Budget' }
  ]
})

const budgetSummary = ref([
  { name: 'Marketing Q1', type: 'OPERATIONAL', amount: 50000, status: 'APPROVED', utilization: 75 },
  { name: 'IT Infrastructure', type: 'CAPITAL', amount: 100000, status: 'APPROVED', utilization: 60 },
  { name: 'HR Training', type: 'DEPARTMENT', amount: 25000, status: 'APPROVED', utilization: 45 },
  { name: 'New Product', type: 'PROJECT', amount: 75000, status: 'PENDING_APPROVAL', utilization: 0 }
])

const chartData = ref({
  labels: ['Marketing', 'Operations', 'IT', 'HR', 'Facilities'],
  datasets: [
    {
      label: 'Budget',
      backgroundColor: '#42A5F5',
      data: [120000, 150000, 100000, 80000, 50000]
    },
    {
      label: 'Actual',
      backgroundColor: '#FFA726',
      data: [95000, 140000, 85000, 55000, 60000]
    }
  ]
})

const chartOptions = ref({
  responsive: true,
  plugins: { legend: { position: 'top' } },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { callback: (value) => '$' + value.toLocaleString() }
    }
  }
})

const typeChartData = ref({
  labels: ['Operational', 'Capital', 'Project', 'Department'],
  datasets: [{
    data: [200000, 150000, 100000, 50000],
    backgroundColor: ['#42A5F5', '#FFA726', '#66BB6A', '#AB47BC']
  }]
})

const statusChartData = ref({
  labels: ['Approved', 'Pending', 'Draft'],
  datasets: [{
    data: [350000, 100000, 50000],
    backgroundColor: ['#66BB6A', '#FFA726', '#78909C']
  }]
})

const pieChartOptions = ref({
  responsive: true,
  plugins: { legend: { position: 'bottom' } }
})

const formatCurrency = (amount) => 
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

const getVarianceStatus = (percent) => {
  if (percent < -10) return 'danger'
  if (percent < 0) return 'warning'
  return 'success'
}

const getTypeSeverity = (type) => {
  switch (type) {
    case 'OPERATIONAL': return 'info'
    case 'CAPITAL': return 'warning'
    case 'PROJECT': return 'success'
    case 'DEPARTMENT': return 'secondary'
    default: return 'info'
  }
}

const getStatusSeverity = (status) => {
  switch (status) {
    case 'APPROVED': return 'success'
    case 'PENDING_APPROVAL': return 'warning'
    case 'DRAFT': return 'secondary'
    default: return 'info'
  }
}

const getUtilizationClass = (utilization) => {
  if (utilization > 90) return 'progress-danger'
  if (utilization > 75) return 'progress-warning'
  return 'progress-success'
}

const generateReport = () => {
  console.log('Generate report clicked')
  toast.add({ severity: 'info', summary: 'Generating Report', detail: 'Report is being generated...' })
}

const exportReport = () => {
  console.log('Export report clicked')
  toast.add({ severity: 'success', summary: 'Export Started', detail: 'Report export has been initiated' })
}

onMounted(() => {
  generateReport()
})
</script>

<style scoped>
.budget-reports {
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

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.card-title-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.filter-card {
  margin-bottom: 2rem;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.report-summary {
  margin-bottom: 2rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
}

.summary-item label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 600;
}

.amount {
  font-weight: 600;
  font-size: 1.125rem;
}

.amount.budget { color: #3b82f6; }
.amount.actual { color: #f59e0b; }
.amount.variance.positive { color: #10b981; }
.amount.variance.negative { color: #ef4444; }

.percentage.positive { color: #10b981; font-weight: 600; }
.percentage.negative { color: #ef4444; font-weight: 600; }

.chart-section {
  margin: 2rem 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.summary-section h4 {
  margin-bottom: 1rem;
  text-align: center;
}

.utilization-text {
  margin-left: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.progress-success :deep(.p-progressbar-value) { background: #10b981; }
.progress-warning :deep(.p-progressbar-value) { background: #f59e0b; }
.progress-danger :deep(.p-progressbar-value) { background: #ef4444; }
</style>