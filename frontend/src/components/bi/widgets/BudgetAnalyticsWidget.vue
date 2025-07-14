<template>
  <v-card>
    <v-card-title>
      <div class="d-flex justify-space-between align-center w-100">
        <div>
          <h3>Budget Analytics</h3>
          <v-chip
            v-if="selectedDepartment"
            small
            class="mr-2"
          >
            {{ selectedDepartment }}
          </v-chip>
          <v-chip
            v-if="selectedProject"
            small
          >
            {{ selectedProject }}
          </v-chip>
        </div>
        <div>
          <v-btn
            icon
            @click="refreshData"
          >
            <v-icon>mdi-refresh</v-icon>
          </v-btn>
        </div>
      </div>
    </v-card-title>

    <v-card-text>
      <!-- Filters -->
      <v-row class="mb-4">
        <v-col cols="12" sm="4">
          <v-select
            v-model="selectedDepartment"
            :items="departments"
            item-text="name"
            item-value="id"
            label="Department"
            clearable
          ></v-select>
        </v-col>

        <v-col cols="12" sm="4">
          <v-select
            v-model="selectedProject"
            :items="projects"
            item-text="name"
            item-value="id"
            label="Project"
            clearable
          ></v-select>
        </v-col>

        <v-col cols="12" sm="4">
          <v-select
            v-model="selectedPeriod"
            :items="periods"
            label="Period"
          ></v-select>
        </v-col>
      </v-row>

      <!-- Budget Performance Grid -->
      <v-row>
        <v-col cols="12" md="6">
          <apexchart
            type="bar"
            :options="performanceChartOptions"
            :series="performanceChartSeries"
            height="300"
          ></apexchart>
        </v-col>

        <v-col cols="12" md="6">
          <apexchart
            type="radialBar"
            :options="varianceChartOptions"
            :series="varianceChartSeries"
            height="300"
          ></apexchart>
        </v-col>
      </v-row>

      <!-- Budget Breakdown Table -->
      <v-row>
        <v-col cols="12">
          <v-data-table
            :headers="breakdownHeaders"
            :items="breakdownData"
            :items-per-page="10"
            class="elevation-1"
          >
            <template v-slot:item.amount="{ item }">
              ${{ formatCurrency(item.amount) }}
            </template>
            <template v-slot:item.variance="{ item }">
              <v-chip
                :color="getVarianceColor(item.variance)"
                small
              >
                {{ formatCurrency(item.variance) }}
              </v-chip>
            </template>
          </v-data-table>
        </v-col>
      </v-row>

      <!-- AI Insights -->
      <v-row>
        <v-col cols="12">
          <v-card class="mt-4">
            <v-card-title>AI Insights</v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item
                  v-for="insight in aiInsights"
                  :key="insight.id"
                >
                  <v-list-item-icon>
                    <v-icon :color="insight.color">{{ insight.icon }}</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ insight.title }}</v-list-item-title>
                    <v-list-item-subtitle>{{ insight.description }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBudgetStore } from '@/stores/budget'
import { useApi } from '@/composables/useApi'

const api = useApi()
const budgetStore = useBudgetStore()

// State
const selectedDepartment = ref(null)
const selectedProject = ref(null)
const selectedPeriod = ref('current_month')
const departments = ref([])
const projects = ref([])
const periods = [
  'current_month',
  'last_month',
  'current_quarter',
  'last_quarter',
  'current_year',
  'last_year'
]

// Computed
const performanceChartSeries = computed(() => [{
  name: 'Budgeted',
  data: analytics.value.budgetedAmounts
}, {
  name: 'Actual',
  data: analytics.value.actualAmounts
}])

const performanceChartOptions = {
  xaxis: {
    categories: analytics.value.categories
  },
  colors: ['#4CAF50', '#2196F3'],
  dataLabels: {
    enabled: true
  }
}

const varianceChartSeries = computed(() => {
  return analytics.value.variancePercentages
})

const varianceChartOptions = {
  plotOptions: {
    radialBar: {
      dataLabels: {
        name: {
          fontSize: '22px'
        },
        value: {
          fontSize: '16px'
        },
        total: {
          show: true,
          label: 'Variance',
          fontSize: '22px'
        }
      }
    }
  },
  labels: analytics.value.categories
}

const breakdownHeaders = [
  { text: 'Category', value: 'category' },
  { text: 'Budgeted', value: 'budgeted', align: 'right' },
  { text: 'Actual', value: 'actual', align: 'right' },
  { text: 'Variance', value: 'variance', align: 'right' }
]

// Methods
const getVarianceColor = (variance: number) => {
  if (variance > 0) return 'success'
  if (variance < 0) return 'error'
  return 'grey'
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const fetchAnalytics = async () => {
  try {
    const response = await api.post('/budget/analytics', {
      department_id: selectedDepartment.value,
      project_id: selectedProject.value,
      period: selectedPeriod.value
    })
    analytics.value = response.data
  } catch (err) {
    console.error('Error fetching budget analytics:', err)
  }
}

const fetchReferenceData = async () => {
  try {
    const [deptRes, projRes] = await Promise.all([
      api.get('/department'),
      api.get('/project')
    ])
    departments.value = deptRes.data
    projects.value = projRes.data
  } catch (err) {
    console.error('Error fetching reference data:', err)
  }
}

const refreshData = () => {
  fetchAnalytics()
}

// Lifecycle
onMounted(async () => {
  await fetchReferenceData()
  refreshData()
})
</script>
