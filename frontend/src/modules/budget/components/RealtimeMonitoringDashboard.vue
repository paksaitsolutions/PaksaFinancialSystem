<template>
  <div class="realtime-monitoring-dashboard">
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <span>Real-time Budget Monitoring</span>
          <div class="flex align-items-center gap-2">
            <i class="pi pi-circle-fill text-green-500 text-xs"></i>
            <span class="text-sm text-500">Live</span>
          </div>
        </div>
      </template>
      <template #content>
        <div class="monitoring-controls mb-4">
          <div class="grid">
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Refresh Interval</label>
                <Dropdown 
                  v-model="refreshInterval"
                  :options="intervalOptions"
                  optionLabel="label"
                  optionValue="value"
                  class="w-full"
                />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Alert Threshold</label>
                <InputNumber 
                  v-model="alertThreshold"
                  suffix="%"
                  :min="0"
                  :max="100"
                  class="w-full"
                />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Actions</label>
                <div class="flex gap-2">
                  <Button 
                    :label="isMonitoring ? 'Stop' : 'Start'" 
                    :icon="isMonitoring ? 'pi pi-pause' : 'pi pi-play'"
                    :class="isMonitoring ? 'p-button-danger' : 'p-button-success'"
                    @click="toggleMonitoring"
                  />
                  <Button 
                    label="Refresh Now" 
                    icon="pi pi-refresh"
                    class="p-button-outlined"
                    @click="refreshData"
                    :loading="refreshing"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="monitoring-alerts mb-4" v-if="alerts.length > 0">
          <h4 class="text-red-500">
            <i class="pi pi-exclamation-triangle mr-2"></i>
            Active Alerts ({{ alerts.length }})
          </h4>
          <div class="grid">
            <div v-for="alert in alerts" :key="alert.id" class="col-12 md:col-6">
              <Message :severity="alert.severity" :closable="false">
                <div>
                  <div class="font-medium">{{ alert.title }}</div>
                  <div class="text-sm">{{ alert.message }}</div>
                  <div class="text-xs text-500 mt-1">{{ formatTime(alert.timestamp) }}</div>
                </div>
              </Message>
            </div>
          </div>
        </div>
        
        <div class="monitoring-metrics">
          <div class="grid">
            <div class="col-12 md:col-3">
              <Card class="text-center h-full">
                <template #content>
                  <div class="text-3xl font-bold text-primary">
                    {{ monitoringData.activeBudgets }}
                  </div>
                  <div class="text-sm text-500">Active Budgets</div>
                  <div class="text-xs text-500 mt-1">
                    Last updated: {{ formatTime(monitoringData.lastUpdate) }}
                  </div>
                </template>
              </Card>
            </div>
            <div class="col-12 md:col-3">
              <Card class="text-center h-full">
                <template #content>
                  <div class="text-3xl font-bold text-orange-500">
                    {{ monitoringData.budgetsAtRisk }}
                  </div>
                  <div class="text-sm text-500">Budgets at Risk</div>
                  <div class="text-xs text-500 mt-1">
                    > {{ alertThreshold }}% utilized
                  </div>
                </template>
              </Card>
            </div>
            <div class="col-12 md:col-3">
              <Card class="text-center h-full">
                <template #content>
                  <div class="text-3xl font-bold text-red-500">
                    {{ monitoringData.overBudget }}
                  </div>
                  <div class="text-sm text-500">Over Budget</div>
                  <div class="text-xs text-500 mt-1">
                    Exceeded allocation
                  </div>
                </template>
              </Card>
            </div>
            <div class="col-12 md:col-3">
              <Card class="text-center h-full">
                <template #content>
                  <div class="text-3xl font-bold text-green-500">
                    {{ formatCurrency(monitoringData.totalRemaining) }}
                  </div>
                  <div class="text-sm text-500">Total Remaining</div>
                  <div class="text-xs text-500 mt-1">
                    Across all budgets
                  </div>
                </template>
              </Card>
            </div>
          </div>
        </div>
        
        <div class="budget-status-table mt-4">
          <h4>Budget Status Overview</h4>
          <DataTable :value="monitoringData.budgetStatus" class="p-datatable-sm">
            <Column field="name" header="Budget Name" :sortable="true" />
            <Column field="department" header="Department" :sortable="true" />
            <Column field="allocated" header="Allocated" :sortable="true">
              <template #body="{ data }">
                {{ formatCurrency(data.allocated) }}
              </template>
            </Column>
            <Column field="spent" header="Spent" :sortable="true">
              <template #body="{ data }">
                {{ formatCurrency(data.spent) }}
              </template>
            </Column>
            <Column field="utilization" header="Utilization" :sortable="true">
              <template #body="{ data }">
                <div class="flex align-items-center gap-2">
                  <ProgressBar 
                    :value="data.utilization" 
                    :showValue="false"
                    :class="getUtilizationClass(data.utilization)"
                    style="width: 100px; height: 8px"
                  />
                  <span class="text-sm font-medium" :class="getUtilizationTextClass(data.utilization)">
                    {{ data.utilization }}%
                  </span>
                </div>
              </template>
            </Column>
            <Column field="status" header="Status" :sortable="true">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
          </DataTable>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Alert {
  id: number
  title: string
  message: string
  severity: string
  timestamp: Date
}

interface MonitoringData {
  activeBudgets: number
  budgetsAtRisk: number
  overBudget: number
  totalRemaining: number
  lastUpdate: Date
  budgetStatus: any[]
}

const isMonitoring = ref(false)
const refreshing = ref(false)
const refreshInterval = ref(30)
const alertThreshold = ref(85)
const monitoringTimer = ref<NodeJS.Timeout | null>(null)

const intervalOptions = [
  { label: '10 seconds', value: 10 },
  { label: '30 seconds', value: 30 },
  { label: '1 minute', value: 60 },
  { label: '5 minutes', value: 300 }
]

const alerts = ref<Alert[]>([
  {
    id: 1,
    title: 'Budget Threshold Exceeded',
    message: 'Marketing Q1 budget has exceeded 90% utilization',
    severity: 'warn',
    timestamp: new Date()
  },
  {
    id: 2,
    title: 'Budget Overspend Alert',
    message: 'IT Equipment budget is 105% utilized',
    severity: 'error',
    timestamp: new Date()
  }
])

const monitoringData = ref<MonitoringData>({
  activeBudgets: 12,
  budgetsAtRisk: 3,
  overBudget: 1,
  totalRemaining: 485000,
  lastUpdate: new Date(),
  budgetStatus: [
    {
      name: 'Marketing Q1',
      department: 'Marketing',
      allocated: 100000,
      spent: 92000,
      utilization: 92,
      status: 'At Risk'
    },
    {
      name: 'IT Equipment',
      department: 'IT',
      allocated: 50000,
      spent: 52500,
      utilization: 105,
      status: 'Over Budget'
    },
    {
      name: 'HR Training',
      department: 'HR',
      allocated: 25000,
      spent: 15000,
      utilization: 60,
      status: 'On Track'
    },
    {
      name: 'Operations Q1',
      department: 'Operations',
      allocated: 150000,
      spent: 120000,
      utilization: 80,
      status: 'On Track'
    }
  ]
})

const toggleMonitoring = () => {
  isMonitoring.value = !isMonitoring.value
  
  if (isMonitoring.value) {
    startMonitoring()
  } else {
    stopMonitoring()
  }
}

const startMonitoring = () => {
  monitoringTimer.value = setInterval(() => {
    refreshData()
  }, refreshInterval.value * 1000)
}

const stopMonitoring = () => {
  if (monitoringTimer.value) {
    clearInterval(monitoringTimer.value)
    monitoringTimer.value = null
  }
}

const refreshData = async () => {
  refreshing.value = true
  try {
    // Mock data refresh
    await new Promise(resolve => setTimeout(resolve, 1000))
    monitoringData.value.lastUpdate = new Date()
    
    // Simulate some data changes
    monitoringData.value.budgetStatus.forEach(budget => {
      if (Math.random() > 0.8) {
        budget.spent += Math.random() * 1000
        budget.utilization = Math.round((budget.spent / budget.allocated) * 100)
        
        if (budget.utilization > 100) {
          budget.status = 'Over Budget'
        } else if (budget.utilization > alertThreshold.value) {
          budget.status = 'At Risk'
        } else {
          budget.status = 'On Track'
        }
      }
    })
  } finally {
    refreshing.value = false
  }
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString()
}

const getUtilizationClass = (utilization: number) => {
  if (utilization > 100) return 'p-progressbar-danger'
  if (utilization > alertThreshold.value) return 'p-progressbar-warning'
  return 'p-progressbar-success'
}

const getUtilizationTextClass = (utilization: number) => {
  if (utilization > 100) return 'text-red-500'
  if (utilization > alertThreshold.value) return 'text-orange-500'
  return 'text-green-500'
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'On Track': return 'success'
    case 'At Risk': return 'warning'
    case 'Over Budget': return 'danger'
    default: return 'info'
  }
}

onMounted(() => {
  refreshData()
})

onUnmounted(() => {
  stopMonitoring()
})
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color-secondary);
}

:deep(.p-progressbar-danger .p-progressbar-value) {
  background: var(--red-500);
}

:deep(.p-progressbar-warning .p-progressbar-value) {
  background: var(--orange-500);
}

:deep(.p-progressbar-success .p-progressbar-value) {
  background: var(--green-500);
}
</style>