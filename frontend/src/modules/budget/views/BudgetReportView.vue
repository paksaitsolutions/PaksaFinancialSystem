<template>
  <v-container fluid>
    <v-row>
      <!-- Report Filters -->
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-title>Report Filters</v-card-title>
          <v-card-text>
            <v-row>
              <!-- Date Range -->
              <v-col cols="12" sm="4">
                <v-menu
                  v-model="dateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ on, attrs }">
                    <v-text-field
                      v-model="dateRange"
                      label="Date Range"
                      prepend-icon="mdi-calendar"
                      readonly
                      v-bind="attrs"
                      v-on="on"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="dateRange"
                    range
                    @input="dateMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>

              <!-- Budget Type -->
              <v-col cols="12" sm="4">
                <v-select
                  v-model="filters.type"
                  :items="Object.values(BudgetType)"
                  label="Budget Type"
                  clearable
                ></v-select>
              </v-col>

              <!-- Status -->
              <v-col cols="12" sm="4">
                <v-select
                  v-model="filters.status"
                  :items="Object.values(BudgetStatus)"
                  label="Status"
                  clearable
                ></v-select>
              </v-col>

              <!-- Department -->
              <v-col cols="12" sm="4">
                <v-select
                  v-model="filters.department"
                  :items="departments"
                  item-text="name"
                  item-value="id"
                  label="Department"
                  clearable
                ></v-select>
              </v-col>

              <!-- Project -->
              <v-col cols="12" sm="4">
                <v-select
                  v-model="filters.project"
                  :items="projects"
                  item-text="name"
                  item-value="id"
                  label="Project"
                  clearable
                ></v-select>
              </v-col>

              <!-- Account -->
              <v-col cols="12" sm="4">
                <v-select
                  v-model="filters.account"
                  :items="accounts"
                  item-text="name"
                  item-value="id"
                  label="Account"
                  clearable
                ></v-select>
              </v-col>

              <!-- Export Options -->
              <v-col cols="12" class="text-right">
                <v-btn
                  color="primary"
                  class="mr-2"
                  @click="generatePDF"
                >
                  <v-icon left>mdi-file-pdf</v-icon>
                  Export PDF
                </v-btn>
                <v-btn
                  color="success"
                  @click="exportExcel"
                >
                  <v-icon left>mdi-microsoft-excel</v-icon>
                  Export Excel
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Main Report Content -->
      <v-col cols="12">
        <v-card>
          <v-card-title>
            Budget Report
            <v-spacer></v-spacer>
            <v-btn
              icon
              @click="toggleChartType"
            >
              <v-icon>{{ chartIcon }}</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <apexchart
              v-if="chartType === 'bar'"
              type="bar"
              :options="barChartOptions"
              :series="barChartSeries"
              height="400"
            ></apexchart>
            <apexchart
              v-else
              type="line"
              :options="lineChartOptions"
              :series="lineChartSeries"
              height="400"
            ></apexchart>

            <v-data-table
              :headers="reportHeaders"
              :items="filteredReport"
              :items-per-page="10"
              class="elevation-1 mt-4"
            >
              <template v-slot:item.amount="{ item }">
                ${{ formatCurrency(item.amount) }}
              </template>
              <template v-slot:item.variance="{ item }">
                <span :class="getVarianceClass(item.variance)">
                  {{ formatCurrency(item.variance) }}
                </span>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBudgetStore } from '../../store/budget'
import { useApi } from '../../composables/useApi'
import { BudgetStatus, BudgetType } from '../types/budget'

const api = useApi()
const budgetStore = useBudgetStore()

// State
const dateMenu = ref(false)
const dateRange = ref([] as string[])
const chartType = ref<'bar' | 'line'>('bar')
const filters = ref({
  type: null as BudgetType | null,
  status: null as BudgetStatus | null,
  department: null as number | null,
  project: null as number | null,
  account: null as number | null
})

// Computed
const chartIcon = computed(() => chartType.value === 'bar' ? 'mdi-chart-line' : 'mdi-chart-bar')
const departments = ref([])
const projects = ref([])
const accounts = ref([])

const filteredReport = computed(() => {
  return budgetStore.budgets
    .filter(b => {
      const dateMatch = !dateRange.value.length || 
        (new Date(b.start_date) >= new Date(dateRange.value[0]) && 
         new Date(b.end_date) <= new Date(dateRange.value[1]))
      return dateMatch &&
        (!filters.value.type || b.budget_type === filters.value.type) &&
        (!filters.value.status || b.status === filters.value.status) &&
        (!filters.value.department || b.allocations.some(a => a.department_id === filters.value.department)) &&
        (!filters.value.project || b.allocations.some(a => a.project_id === filters.value.project)) &&
        (!filters.value.account || b.lines.some(l => l.account_id === filters.value.account))
    })
    .map(b => ({
      ...b,
      variance: calculateVariance(b)
    }))
})

const barChartSeries = computed(() => [{
  name: 'Budget Amount',
  data: filteredReport.value.map(b => b.total_amount)
}])

const barChartOptions = {
  xaxis: {
    categories: filteredReport.value.map(b => b.name)
  },
  colors: ['#4CAF50'],
  dataLabels: {
    enabled: true
  }
}

const lineChartSeries = computed(() => [{
  name: 'Budget Amount',
  data: filteredReport.value.map(b => b.total_amount)
}])

const lineChartOptions = {
  xaxis: {
    type: 'datetime',
    categories: filteredReport.value.map(b => new Date(b.start_date).getTime())
  },
  colors: ['#4CAF50'],
  dataLabels: {
    enabled: true
  }
}

const reportHeaders = [
  { text: 'Budget Name', value: 'name' },
  { text: 'Type', value: 'budget_type' },
  { text: 'Status', value: 'status' },
  { text: 'Start Date', value: 'start_date' },
  { text: 'End Date', value: 'end_date' },
  { text: 'Amount', value: 'amount', align: 'right' },
  { text: 'Variance', value: 'variance', align: 'right' }
]

// Methods
const toggleChartType = () => {
  chartType.value = chartType.value === 'bar' ? 'line' : 'bar'
}

const calculateVariance = (budget: any) => {
  // TODO: Implement actual variance calculation logic
  // This is a placeholder
  return 0
}

const getVarianceClass = (variance: number) => {
  return variance > 0 ? 'positive-amount' : variance < 0 ? 'negative-amount' : ''
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const generatePDF = async () => {
  try {
    const response = await api.post('/budget/report/pdf', {
      dateRange: dateRange.value,
      filters: filters.value
    })
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    window.open(url)
  } catch (err) {
    console.error('Error generating PDF:', err)
  }
}

const exportExcel = async () => {
  try {
    const response = await api.post('/budget/report/excel', {
      dateRange: dateRange.value,
      filters: filters.value
    })
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'budget_report.xlsx'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Error exporting Excel:', err)
  }
}

// Lifecycle
onMounted(async () => {
  try {
    // Fetch reference data
    const [deptRes, projRes, acctRes] = await Promise.all([
      api.get('/department'),
      api.get('/project'),
      api.get('/account')
    ])
    departments.value = deptRes.data
    projects.value = projRes.data
    accounts.value = acctRes.data
  } catch (err) {
    console.error('Error fetching reference data:', err)
  }
})
</script>

<style scoped>
.positive-amount {
  color: #4CAF50;
}

.negative-amount {
  color: #F44336;
}
</style>
