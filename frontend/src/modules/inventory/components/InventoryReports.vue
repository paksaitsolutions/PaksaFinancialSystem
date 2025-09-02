<template>
  <div class="inventory-reports">
    <!-- Header -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="text-2xl font-bold text-900 m-0">Inventory Reports & Analytics</h2>
        <p class="text-600 mt-1 mb-0">Comprehensive reporting and analysis tools</p>
      </div>
      <div class="flex gap-2">
        <Button icon="pi pi-refresh" label="Refresh Data" severity="secondary" @click="refreshData" />
        <Button icon="pi pi-cog" label="Settings" severity="secondary" outlined @click="showSettings = true" />
      </div>
    </div>

    <!-- Quick Stats Cards -->
    <div class="grid mb-4">
      <div class="col-12 lg:col-3 md:col-6">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Inventory Turnover</div>
                <div class="text-2xl font-bold text-900">{{ stats.turnoverRatio.toFixed(2) }}</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-arrow-up text-green-500 mr-1"></i>
                  {{ stats.turnoverChange }}% vs last period
                </div>
              </div>
              <div class="bg-blue-100 border-round p-3">
                <i class="pi pi-refresh text-blue-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-3 md:col-6">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Days of Supply</div>
                <div class="text-2xl font-bold text-900">{{ stats.daysOfSupply }}</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-calendar text-orange-500 mr-1"></i>
                  Based on avg consumption
                </div>
              </div>
              <div class="bg-orange-100 border-round p-3">
                <i class="pi pi-calendar text-orange-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-3 md:col-6">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Carrying Cost</div>
                <div class="text-2xl font-bold text-900">{{ formatCurrency(stats.carryingCost) }}</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-percentage text-purple-500 mr-1"></i>
                  {{ stats.carryingCostPercent }}% of inventory value
                </div>
              </div>
              <div class="bg-purple-100 border-round p-3">
                <i class="pi pi-percentage text-purple-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-3 md:col-6">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Stockout Risk</div>
                <div class="text-2xl font-bold text-red-500">{{ stats.stockoutRisk }}%</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-exclamation-triangle text-red-500 mr-1"></i>
                  {{ stats.itemsAtRisk }} items at risk
                </div>
              </div>
              <div class="bg-red-100 border-round p-3">
                <i class="pi pi-exclamation-triangle text-red-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Report Tabs -->
    <TabView v-model:activeIndex="activeTabIndex">
      <!-- Valuation Report -->
      <TabPanel header="Valuation Report">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Inventory Valuation</span>
              <div class="flex gap-2">
                <Dropdown v-model="valuationFilters.method" :options="valuationMethods" optionLabel="label" optionValue="value" placeholder="Valuation Method" />
                <Button icon="pi pi-download" label="Export" severity="secondary" @click="exportValuation" />
              </div>
            </div>
          </template>
          <template #content>
            <DataTable :value="valuationData" responsiveLayout="scroll" class="p-datatable-sm">
              <Column field="category" header="Category" sortable />
              <Column field="items_count" header="Items" sortable>
                <template #body="{ data }">
                  {{ data.items_count.toLocaleString() }}
                </template>
              </Column>
              <Column field="quantity" header="Quantity" sortable>
                <template #body="{ data }">
                  {{ data.quantity.toLocaleString() }}
                </template>
              </Column>
              <Column field="avg_cost" header="Avg Cost" sortable>
                <template #body="{ data }">
                  {{ formatCurrency(data.avg_cost) }}
                </template>
              </Column>
              <Column field="total_value" header="Total Value" sortable>
                <template #body="{ data }">
                  {{ formatCurrency(data.total_value) }}
                </template>
              </Column>
              <Column field="percentage" header="% of Total" sortable>
                <template #body="{ data }">
                  <ProgressBar :value="data.percentage" :showValue="false" style="height: 0.5rem" />
                  <span class="text-sm">{{ data.percentage.toFixed(1) }}%</span>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>

      <!-- ABC Analysis -->
      <TabPanel header="ABC Analysis">
        <div class="grid">
          <div class="col-12 lg:col-8">
            <Card>
              <template #title>ABC Classification</template>
              <template #content>
                <Chart type="doughnut" :data="abcChartData" :options="abcChartOptions" class="h-20rem" />
              </template>
            </Card>
          </div>
          <div class="col-12 lg:col-4">
            <Card>
              <template #title>Classification Summary</template>
              <template #content>
                <div class="space-y-4">
                  <div v-for="item in abcSummary" :key="item.class" class="flex align-items-center justify-content-between p-3 border-round" :class="item.bgClass">
                    <div>
                      <div class="font-semibold text-900">Class {{ item.class }}</div>
                      <div class="text-sm text-600">{{ item.description }}</div>
                    </div>
                    <div class="text-right">
                      <div class="font-bold text-900">{{ item.items }} items</div>
                      <div class="text-sm text-600">{{ item.valuePercent }}% value</div>
                    </div>
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </TabPanel>

      <!-- Movement Analysis -->
      <TabPanel header="Movement Analysis">
        <div class="grid">
          <div class="col-12">
            <Card>
              <template #title>
                <div class="flex justify-content-between align-items-center">
                  <span>Inventory Movement Trends</span>
                  <div class="flex gap-2">
                    <Dropdown v-model="movementFilters.period" :options="periodOptions" optionLabel="label" optionValue="value" placeholder="Period" />
                    <Dropdown v-model="movementFilters.category" :options="categoryOptions" optionLabel="label" optionValue="value" placeholder="Category" showClear />
                  </div>
                </div>
              </template>
              <template #content>
                <Chart type="line" :data="movementChartData" :options="movementChartOptions" class="h-20rem mb-4" />
                
                <DataTable :value="movementData" responsiveLayout="scroll" class="p-datatable-sm">
                  <Column field="item_name" header="Item" sortable />
                  <Column field="sku" header="SKU" sortable />
                  <Column field="total_in" header="Total In" sortable>
                    <template #body="{ data }">
                      <span class="text-green-600 font-semibold">+{{ data.total_in.toLocaleString() }}</span>
                    </template>
                  </Column>
                  <Column field="total_out" header="Total Out" sortable>
                    <template #body="{ data }">
                      <span class="text-red-600 font-semibold">-{{ data.total_out.toLocaleString() }}</span>
                    </template>
                  </Column>
                  <Column field="net_movement" header="Net Movement" sortable>
                    <template #body="{ data }">
                      <span :class="data.net_movement >= 0 ? 'text-green-600' : 'text-red-600'" class="font-semibold">
                        {{ data.net_movement >= 0 ? '+' : '' }}{{ data.net_movement.toLocaleString() }}
                      </span>
                    </template>
                  </Column>
                  <Column field="velocity" header="Velocity" sortable>
                    <template #body="{ data }">
                      <Tag :value="data.velocity" :severity="getVelocitySeverity(data.velocity)" />
                    </template>
                  </Column>
                </DataTable>
              </template>
            </Card>
          </div>
        </div>
      </TabPanel>

      <!-- Aging Report -->
      <TabPanel header="Aging Report">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Inventory Aging Analysis</span>
              <div class="flex gap-2">
                <Dropdown v-model="agingFilters.category" :options="categoryOptions" optionLabel="label" optionValue="value" placeholder="Category" showClear />
                <Button icon="pi pi-download" label="Export" severity="secondary" @click="exportAging" />
              </div>
            </div>
          </template>
          <template #content>
            <div class="grid mb-4">
              <div class="col-12 md:col-3" v-for="bucket in agingBuckets" :key="bucket.label">
                <div class="text-center p-3 border-round" :class="bucket.bgClass">
                  <div class="text-500 font-medium mb-1">{{ bucket.label }}</div>
                  <div class="text-xl font-bold text-900">{{ formatCurrency(bucket.value) }}</div>
                  <div class="text-sm text-500">{{ bucket.items }} items</div>
                </div>
              </div>
            </div>
            
            <DataTable :value="agingData" responsiveLayout="scroll" class="p-datatable-sm">
              <Column field="item_name" header="Item" sortable />
              <Column field="sku" header="SKU" sortable />
              <Column field="quantity" header="Quantity" sortable />
              <Column field="last_movement" header="Last Movement" sortable>
                <template #body="{ data }">
                  {{ formatDate(data.last_movement) }}
                </template>
              </Column>
              <Column field="days_since_movement" header="Days Since Movement" sortable>
                <template #body="{ data }">
                  <Tag :value="`${data.days_since_movement} days`" :severity="getAgingSeverity(data.days_since_movement)" />
                </template>
              </Column>
              <Column field="value" header="Value" sortable>
                <template #body="{ data }">
                  {{ formatCurrency(data.value) }}
                </template>
              </Column>
              <Column field="risk_level" header="Risk Level" sortable>
                <template #body="{ data }">
                  <Tag :value="data.risk_level" :severity="getRiskSeverity(data.risk_level)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>

      <!-- Custom Reports -->
      <TabPanel header="Custom Reports">
        <div class="grid">
          <div class="col-12 md:col-4">
            <Card>
              <template #title>Report Builder</template>
              <template #content>
                <div class="space-y-4">
                  <div class="field">
                    <label class="font-semibold">Report Type</label>
                    <Dropdown v-model="customReport.type" :options="reportTypes" optionLabel="label" optionValue="value" placeholder="Select type" class="w-full" />
                  </div>
                  
                  <div class="field">
                    <label class="font-semibold">Date Range</label>
                    <Calendar v-model="customReport.dateRange" selectionMode="range" placeholder="Select date range" class="w-full" />
                  </div>
                  
                  <div class="field">
                    <label class="font-semibold">Categories</label>
                    <MultiSelect v-model="customReport.categories" :options="categoryOptions" optionLabel="label" optionValue="value" placeholder="Select categories" class="w-full" />
                  </div>
                  
                  <div class="field">
                    <label class="font-semibold">Grouping</label>
                    <Dropdown v-model="customReport.groupBy" :options="groupByOptions" optionLabel="label" optionValue="value" placeholder="Group by" class="w-full" />
                  </div>
                  
                  <Button label="Generate Report" class="w-full" @click="generateCustomReport" :loading="generatingReport" />
                </div>
              </template>
            </Card>
          </div>
          
          <div class="col-12 md:col-8">
            <Card>
              <template #title>Generated Report</template>
              <template #content>
                <div v-if="!customReportData" class="text-center py-6">
                  <i class="pi pi-chart-bar text-4xl text-400 mb-3"></i>
                  <p class="text-500">Configure and generate a custom report</p>
                </div>
                <div v-else>
                  <DataTable :value="customReportData" responsiveLayout="scroll" class="p-datatable-sm">
                    <Column v-for="col in customReportColumns" :key="col.field" :field="col.field" :header="col.header" :sortable="col.sortable" />
                  </DataTable>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </TabPanel>
    </TabView>

    <!-- Settings Dialog -->
    <Dialog v-model:visible="showSettings" modal header="Report Settings" :style="{ width: '500px' }">
      <div class="space-y-4">
        <div class="field">
          <label class="font-semibold">Default Currency</label>
          <Dropdown v-model="settings.currency" :options="currencyOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>
        
        <div class="field">
          <label class="font-semibold">Date Format</label>
          <Dropdown v-model="settings.dateFormat" :options="dateFormatOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>
        
        <div class="field-checkbox">
          <Checkbox id="autoRefresh" v-model="settings.autoRefresh" :binary="true" />
          <label for="autoRefresh" class="ml-2">Auto-refresh data every 5 minutes</label>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showSettings = false" />
        <Button label="Save Settings" @click="saveSettings" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { formatCurrency } from '@/utils/formatters'
import Card from 'primevue/card'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import Calendar from 'primevue/calendar'
import Chart from 'primevue/chart'
import Tag from 'primevue/tag'
import ProgressBar from 'primevue/progressbar'
import Dialog from 'primevue/dialog'
import Checkbox from 'primevue/checkbox'

// Composables
const toast = useToast()

// Data
const activeTabIndex = ref(0)
const showSettings = ref(false)
const generatingReport = ref(false)

// Stats
const stats = ref({
  turnoverRatio: 4.2,
  turnoverChange: 8.5,
  daysOfSupply: 87,
  carryingCost: 142500,
  carryingCostPercent: 5.2,
  stockoutRisk: 12,
  itemsAtRisk: 23
})

// Filters
const valuationFilters = reactive({
  method: 'average'
})

const movementFilters = reactive({
  period: '30d',
  category: null
})

const agingFilters = reactive({
  category: null
})

const customReport = reactive({
  type: null,
  dateRange: null,
  categories: [],
  groupBy: null
})

const settings = reactive({
  currency: 'USD',
  dateFormat: 'MM/DD/YYYY',
  autoRefresh: true
})

// Options
const valuationMethods = [
  { label: 'Average Cost', value: 'average' },
  { label: 'FIFO', value: 'fifo' },
  { label: 'LIFO', value: 'lifo' },
  { label: 'Standard Cost', value: 'standard' }
]

const periodOptions = [
  { label: 'Last 7 Days', value: '7d' },
  { label: 'Last 30 Days', value: '30d' },
  { label: 'Last 90 Days', value: '90d' },
  { label: 'Last Year', value: '1y' }
]

const categoryOptions = [
  { label: 'Electronics', value: 'electronics' },
  { label: 'Components', value: 'components' },
  { label: 'Accessories', value: 'accessories' }
]

const reportTypes = [
  { label: 'Stock Movement', value: 'movement' },
  { label: 'Valuation Summary', value: 'valuation' },
  { label: 'Turnover Analysis', value: 'turnover' },
  { label: 'Reorder Report', value: 'reorder' }
]

const groupByOptions = [
  { label: 'Category', value: 'category' },
  { label: 'Location', value: 'location' },
  { label: 'Supplier', value: 'supplier' },
  { label: 'Date', value: 'date' }
]

const currencyOptions = [
  { label: 'USD ($)', value: 'USD' },
  { label: 'EUR (€)', value: 'EUR' },
  { label: 'GBP (£)', value: 'GBP' }
]

const dateFormatOptions = [
  { label: 'MM/DD/YYYY', value: 'MM/DD/YYYY' },
  { label: 'DD/MM/YYYY', value: 'DD/MM/YYYY' },
  { label: 'YYYY-MM-DD', value: 'YYYY-MM-DD' }
]

// Mock Data
const valuationData = ref([
  { category: 'Electronics', items_count: 45, quantity: 1250, avg_cost: 125.50, total_value: 156875, percentage: 45.2 },
  { category: 'Components', items_count: 78, quantity: 2340, avg_cost: 45.25, total_value: 105885, percentage: 30.5 },
  { category: 'Accessories', items_count: 23, quantity: 890, avg_cost: 25.75, total_value: 22917.5, percentage: 6.6 },
  { category: 'Raw Materials', items_count: 34, quantity: 1560, avg_cost: 35.80, total_value: 55848, percentage: 16.1 }
])

const abcSummary = ref([
  { class: 'A', description: 'High value items', items: 25, valuePercent: 70, bgClass: 'bg-green-50' },
  { class: 'B', description: 'Medium value items', items: 45, valuePercent: 25, bgClass: 'bg-orange-50' },
  { class: 'C', description: 'Low value items', items: 110, valuePercent: 5, bgClass: 'bg-red-50' }
])

const movementData = ref([
  { item_name: 'Widget Pro Max', sku: 'WDG-001', total_in: 150, total_out: 125, net_movement: 25, velocity: 'High' },
  { item_name: 'Component X', sku: 'CMP-002', total_in: 75, total_out: 80, net_movement: -5, velocity: 'Medium' },
  { item_name: 'Assembly Kit', sku: 'ASM-003', total_in: 25, total_out: 15, net_movement: 10, velocity: 'Low' }
])

const agingData = ref([
  { item_name: 'Old Widget', sku: 'OLD-001', quantity: 50, last_movement: new Date('2023-08-15'), days_since_movement: 120, value: 2500, risk_level: 'High' },
  { item_name: 'Legacy Part', sku: 'LEG-002', quantity: 25, last_movement: new Date('2023-10-01'), days_since_movement: 75, value: 1250, risk_level: 'Medium' }
])

const agingBuckets = ref([
  { label: '0-30 Days', value: 125000, items: 45, bgClass: 'bg-green-50' },
  { label: '31-60 Days', value: 75000, items: 28, bgClass: 'bg-orange-50' },
  { label: '61-90 Days', value: 35000, items: 15, bgClass: 'bg-red-50' },
  { label: '90+ Days', value: 15000, items: 8, bgClass: 'bg-red-100' }
])

const customReportData = ref(null)
const customReportColumns = ref([])

// Chart Data
const abcChartData = ref({
  labels: ['Class A', 'Class B', 'Class C'],
  datasets: [{
    data: [70, 25, 5],
    backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
    borderWidth: 0
  }]
})

const abcChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
})

const movementChartData = ref({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    {
      label: 'Stock In',
      data: [1200, 1350, 1100, 1450, 1600, 1400],
      borderColor: '#10B981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      tension: 0.4
    },
    {
      label: 'Stock Out',
      data: [1100, 1200, 1250, 1300, 1450, 1350],
      borderColor: '#EF4444',
      backgroundColor: 'rgba(239, 68, 68, 0.1)',
      tension: 0.4
    }
  ]
})

const movementChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true
    }
  },
  plugins: {
    legend: {
      position: 'top'
    }
  }
})

// Methods
const refreshData = () => {
  toast.add({ severity: 'info', summary: 'Refreshing', detail: 'Data refreshed successfully' })
}

const exportValuation = () => {
  toast.add({ severity: 'success', summary: 'Export', detail: 'Valuation report exported successfully' })
}

const exportAging = () => {
  toast.add({ severity: 'success', summary: 'Export', detail: 'Aging report exported successfully' })
}

const generateCustomReport = async () => {
  generatingReport.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Mock generated report data
    customReportData.value = [
      { category: 'Electronics', total_value: 156875, items: 45 },
      { category: 'Components', total_value: 105885, items: 78 }
    ]
    
    customReportColumns.value = [
      { field: 'category', header: 'Category', sortable: true },
      { field: 'total_value', header: 'Total Value', sortable: true },
      { field: 'items', header: 'Items', sortable: true }
    ]
    
    toast.add({ severity: 'success', summary: 'Success', detail: 'Custom report generated successfully' })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to generate report' })
  } finally {
    generatingReport.value = false
  }
}

const saveSettings = () => {
  toast.add({ severity: 'success', summary: 'Success', detail: 'Settings saved successfully' })
  showSettings.value = false
}

const formatDate = (date) => {
  return new Intl.DateTimeFormat('en-US').format(new Date(date))
}

const getVelocitySeverity = (velocity) => {
  const severities = {
    'High': 'success',
    'Medium': 'warning',
    'Low': 'danger'
  }
  return severities[velocity] || 'info'
}

const getAgingSeverity = (days) => {
  if (days <= 30) return 'success'
  if (days <= 60) return 'warning'
  if (days <= 90) return 'danger'
  return 'danger'
}

const getRiskSeverity = (risk) => {
  const severities = {
    'Low': 'success',
    'Medium': 'warning',
    'High': 'danger'
  }
  return severities[risk] || 'info'
}

onMounted(() => {
  // Load initial data
})
</script>

<style scoped>
.inventory-reports {
  padding: 1.5rem;
}

.space-y-4 > * + * {
  margin-top: 1rem;
}

:deep(.p-tabview-nav) {
  background: var(--surface-50);
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.75rem;
}

:deep(.p-progressbar) {
  height: 0.5rem;
}
</style>