<template>
  <div class="inventory-dashboard">
    <!-- Header -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-3xl font-bold text-900 m-0">Inventory Dashboard</h1>
        <p class="text-600 mt-1 mb-0">Monitor and manage your inventory levels</p>
      </div>
      <div class="flex gap-2">
        <Button icon="pi pi-refresh" label="Refresh" @click="loadDashboardData" :loading="loading" />
        <Button icon="pi pi-plus" label="Add Item" @click="$router.push('/inventory/items/new')" />
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="grid mb-4">
      <div class="col-12 md:col-3">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Total Items</div>
                <div class="text-2xl font-bold text-900">{{ kpis.totalItems.toLocaleString() }}</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-arrow-up text-green-500 mr-1"></i>
                  {{ kpis.totalItemsChange }}% from last month
                </div>
              </div>
              <div class="bg-blue-100 border-round p-3">
                <i class="pi pi-box text-blue-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-3">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Low Stock</div>
                <div class="text-2xl font-bold text-orange-500">{{ kpis.lowStock.toLocaleString() }}</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-exclamation-triangle text-orange-500 mr-1"></i>
                  Requires attention
                </div>
              </div>
              <div class="bg-orange-100 border-round p-3">
                <i class="pi pi-exclamation-triangle text-orange-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-3">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Out of Stock</div>
                <div class="text-2xl font-bold text-red-500">{{ kpis.outOfStock.toLocaleString() }}</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-times-circle text-red-500 mr-1"></i>
                  Immediate action needed
                </div>
              </div>
              <div class="bg-red-100 border-round p-3">
                <i class="pi pi-times-circle text-red-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-3">
        <Card class="h-full">
          <template #content>
            <div class="flex align-items-center">
              <div class="flex-1">
                <div class="text-500 font-medium mb-2">Total Value</div>
                <div class="text-2xl font-bold text-green-500">{{ formatCurrency(kpis.totalValue) }}</div>
                <div class="text-sm text-500 mt-1">
                  <i class="pi pi-arrow-up text-green-500 mr-1"></i>
                  {{ kpis.totalValueChange }}% from last month
                </div>
              </div>
              <div class="bg-green-100 border-round p-3">
                <i class="pi pi-dollar text-green-500 text-2xl"></i>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid mb-4">
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>Inventory Trends</template>
          <template #content>
            <Chart type="line" :data="chartData" :options="chartOptions" class="h-20rem" />
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-4">
        <Card>
          <template #title>Stock Status Distribution</template>
          <template #content>
            <Chart type="doughnut" :data="doughnutData" :options="doughnutOptions" class="h-20rem" />
          </template>
        </Card>
      </div>
    </div>

    <!-- Recent Activity & Alerts -->
    <div class="grid">
      <div class="col-12 lg:col-6">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Recent Transactions</span>
              <Button label="View All" text @click="$router.push('/inventory/transactions')" />
            </div>
          </template>
          <template #content>
            <div v-if="recentTransactions.length === 0" class="text-center py-4">
              <i class="pi pi-inbox text-4xl text-400 mb-3"></i>
              <p class="text-500">No recent transactions</p>
            </div>
            <div v-else>
              <div v-for="transaction in recentTransactions" :key="transaction.id" class="flex align-items-center justify-content-between py-2 border-bottom-1 surface-border">
                <div class="flex align-items-center">
                  <div class="bg-primary-100 border-round p-2 mr-3">
                    <i :class="getTransactionIcon(transaction.type)" class="text-primary"></i>
                  </div>
                  <div>
                    <div class="font-medium text-900">{{ transaction.item_name }}</div>
                    <div class="text-sm text-500">{{ transaction.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) }} • {{ formatDate(new Date(transaction.created_at)) }}</div>
                  </div>
                </div>
                <div class="text-right">
                  <div class="font-medium" :class="transaction.quantity > 0 ? 'text-green-500' : 'text-red-500'">
                    {{ transaction.quantity > 0 ? '+' : '' }}{{ transaction.quantity }}
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-6">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Stock Alerts</span>
              <Button label="Manage" text @click="$router.push('/inventory/alerts')" />
            </div>
          </template>
          <template #content>
            <div v-if="stockAlerts.length === 0" class="text-center py-4">
              <i class="pi pi-check-circle text-4xl text-green-400 mb-3"></i>
              <p class="text-500">All stock levels are healthy</p>
            </div>
            <div v-else>
              <div v-for="alert in stockAlerts" :key="alert.id" class="flex align-items-center justify-content-between py-2 border-bottom-1 surface-border">
                <div class="flex align-items-center">
                  <div class="border-round p-2 mr-3" :class="getAlertClass(alert.severity)">
                    <i :class="getAlertIcon(alert.severity)" :class="getAlertIconColor(alert.severity)"></i>
                  </div>
                  <div>
                    <div class="font-medium text-900">{{ alert.item_name }}</div>
                    <div class="text-sm text-500">{{ alert.message }}</div>
                  </div>
                </div>
                <div class="text-right">
                  <Tag :value="alert.severity" :severity="getTagSeverity(alert.severity)" />
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import Chart from 'primevue/chart'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import { inventoryService } from '@/services/inventoryService'

const router = useRouter()
const toast = useToast()
const loading = ref(false)

// KPI Data
const kpis = ref({
  totalItems: 0,
  totalItemsChange: 0,
  lowStock: 0,
  outOfStock: 0,
  totalValue: 0,
  totalValueChange: 0
})

// Chart Data
const chartData = ref({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  datasets: [
    {
      label: 'Stock Value',
      data: [2100000, 2250000, 2180000, 2420000, 2650000, 2847392],
      borderColor: '#3B82F6',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4,
      fill: true
    },
    {
      label: 'Items Count',
      data: [1150, 1180, 1165, 1200, 1230, 1247],
      borderColor: '#10B981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      tension: 0.4,
      yAxisID: 'y1'
    }
  ]
})

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      type: 'linear',
      display: true,
      position: 'left',
      ticks: {
        callback: function(value) {
          return '$' + (value / 1000000).toFixed(1) + 'M'
        }
      }
    },
    y1: {
      type: 'linear',
      display: true,
      position: 'right',
      grid: {
        drawOnChartArea: false,
      },
    }
  },
  plugins: {
    legend: {
      display: true,
      position: 'top'
    }
  }
})

const doughnutData = ref({
  labels: ['In Stock', 'Low Stock', 'Out of Stock'],
  datasets: [
    {
      data: [1219, 23, 5],
      backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
      borderWidth: 0
    }
  ]
})

const doughnutOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
})

// Recent Transactions
const recentTransactions = ref([])

// Stock Alerts
const stockAlerts = ref([])

// Methods
const loadDashboardData = async () => {
  loading.value = true
  try {
    const [kpiData, movementsData, transactionsData, alertsData] = await Promise.all([
      inventoryService.getDashboardKPIs(),
      inventoryService.getStockMovements(6),
      inventoryService.getRecentTransactions(5),
      inventoryService.getStockAlerts()
    ])
    
    kpis.value = {
      totalItems: kpiData.total_items,
      totalItemsChange: kpiData.total_items_change,
      lowStock: kpiData.low_stock_count,
      outOfStock: kpiData.out_of_stock_count,
      totalValue: kpiData.total_value,
      totalValueChange: kpiData.total_value_change
    }
    
    // Update chart data
    chartData.value = {
      labels: movementsData.map(m => new Date(m.date).toLocaleDateString('en-US', { month: 'short' })),
      datasets: [
        {
          label: 'Stock In',
          data: movementsData.map(m => m.stock_in),
          borderColor: '#10B981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Stock Out',
          data: movementsData.map(m => m.stock_out),
          borderColor: '#EF4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4
        }
      ]
    }
    
    // Update doughnut data
    const totalItems = kpiData.total_items
    const inStock = totalItems - kpiData.low_stock_count - kpiData.out_of_stock_count
    doughnutData.value = {
      labels: ['In Stock', 'Low Stock', 'Out of Stock'],
      datasets: [{
        data: [inStock, kpiData.low_stock_count, kpiData.out_of_stock_count],
        backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
        borderWidth: 0
      }]
    }
    
    recentTransactions.value = transactionsData
    stockAlerts.value = alertsData
    
  } catch (error) {
    console.error('Error loading dashboard data:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load dashboard data',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

const formatDate = (date) => {
  return new Intl.RelativeTimeFormat('en', { numeric: 'auto' }).format(
    Math.ceil((date - new Date()) / (1000 * 60 * 60)),
    'hour'
  )
}

const getTransactionIcon = (type) => {
  const icons = {
    'stock_in': 'pi pi-arrow-down',
    'stock_out': 'pi pi-arrow-up',
    'adjustment': 'pi pi-pencil',
    'transfer': 'pi pi-arrow-right'
  }
  return icons[type] || 'pi pi-circle'
}

const getAlertClass = (severity) => {
  const classes = {
    low: 'bg-blue-100',
    medium: 'bg-orange-100',
    high: 'bg-red-100',
    critical: 'bg-red-200'
  }
  return classes[severity] || 'bg-gray-100'
}

const getAlertIcon = (severity) => {
  const icons = {
    low: 'pi pi-info-circle',
    medium: 'pi pi-exclamation-triangle',
    high: 'pi pi-exclamation-triangle',
    critical: 'pi pi-times-circle'
  }
  return icons[severity] || 'pi pi-info'
}

const getAlertIconColor = (severity) => {
  const colors = {
    low: 'text-blue-500',
    medium: 'text-orange-500',
    high: 'text-red-500',
    critical: 'text-red-600'
  }
  return colors[severity] || 'text-gray-500'
}

const getTagSeverity = (severity) => {
  const severities = {
    low: 'info',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return severities[severity] || 'info'
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.inventory-dashboard {
  padding: 1.5rem;
}
</style>