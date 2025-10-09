<template>
  <div class="reports-view">
    <div class="grid">
      <div class="col-12 md:col-6 lg:col-4">
        <Card class="report-card" @click="generateReport('stock-levels')">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-chart-bar mr-2 text-blue-500"></i>
              Stock Levels Report
            </div>
          </template>
          <template #content>
            <p class="text-600">Current inventory levels by item and location</p>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:col-4">
        <Card class="report-card" @click="generateReport('low-stock')">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-exclamation-triangle mr-2 text-orange-500"></i>
              Low Stock Alert
            </div>
          </template>
          <template #content>
            <p class="text-600">Items below reorder point</p>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:col-4">
        <Card class="report-card" @click="generateReport('valuation')">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-dollar mr-2 text-green-500"></i>
              Inventory Valuation
            </div>
          </template>
          <template #content>
            <p class="text-600">Total inventory value by category</p>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:col-4">
        <Card class="report-card" @click="generateReport('movement')">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-arrows-h mr-2 text-purple-500"></i>
              Movement Report
            </div>
          </template>
          <template #content>
            <p class="text-600">Inventory transactions and movements</p>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:col-4">
        <Card class="report-card" @click="generateReport('aging')">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-clock mr-2 text-red-500"></i>
              Aging Report
            </div>
          </template>
          <template #content>
            <p class="text-600">Inventory aging analysis</p>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:col-4">
        <Card class="report-card" @click="generateReport('abc-analysis')">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-chart-pie mr-2 text-teal-500"></i>
              ABC Analysis
            </div>
          </template>
          <template #content>
            <p class="text-600">Item classification by value</p>
          </template>
        </Card>
      </div>
    </div>

    <Dialog v-model:visible="showReportDialog" modal :header="selectedReport?.title" :style="{ width: '80vw', height: '80vh' }">
      <div v-if="reportLoading" class="flex justify-content-center align-items-center" style="height: 400px;">
        <ProgressSpinner />
      </div>
      <div v-else-if="reportData">
        <DataTable :value="reportData" :paginator="true" :rows="20" responsiveLayout="scroll">
          <Column v-for="col in reportColumns" :key="col.field" :field="col.field" :header="col.header" />
        </DataTable>
      </div>
      
      <template #footer>
        <Button label="Export PDF" icon="pi pi-file-pdf" severity="danger" @click="exportReport('pdf')" />
        <Button label="Export Excel" icon="pi pi-file-excel" severity="success" @click="exportReport('excel')" />
        <Button label="Close" severity="secondary" @click="showReportDialog = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const showReportDialog = ref(false)
const reportLoading = ref(false)
const reportData = ref(null)
const reportColumns = ref([])
const selectedReport = ref(null)

const reports = {
  'stock-levels': {
    title: 'Stock Levels Report',
    columns: [
      { field: 'item_code', header: 'Item Code' },
      { field: 'item_name', header: 'Item Name' },
      { field: 'location', header: 'Location' },
      { field: 'quantity', header: 'Quantity' },
      { field: 'unit_cost', header: 'Unit Cost' },
      { field: 'total_value', header: 'Total Value' }
    ]
  },
  'low-stock': {
    title: 'Low Stock Alert',
    columns: [
      { field: 'item_code', header: 'Item Code' },
      { field: 'item_name', header: 'Item Name' },
      { field: 'current_stock', header: 'Current Stock' },
      { field: 'reorder_point', header: 'Reorder Point' },
      { field: 'shortage', header: 'Shortage' }
    ]
  },
  'valuation': {
    title: 'Inventory Valuation',
    columns: [
      { field: 'category', header: 'Category' },
      { field: 'item_count', header: 'Items' },
      { field: 'total_quantity', header: 'Total Quantity' },
      { field: 'total_value', header: 'Total Value' }
    ]
  },
  'movement': {
    title: 'Movement Report',
    columns: [
      { field: 'date', header: 'Date' },
      { field: 'item_code', header: 'Item Code' },
      { field: 'transaction_type', header: 'Type' },
      { field: 'quantity', header: 'Quantity' },
      { field: 'reference', header: 'Reference' }
    ]
  },
  'aging': {
    title: 'Aging Report',
    columns: [
      { field: 'item_code', header: 'Item Code' },
      { field: 'item_name', header: 'Item Name' },
      { field: 'last_movement', header: 'Last Movement' },
      { field: 'days_since', header: 'Days Since' },
      { field: 'quantity', header: 'Quantity' }
    ]
  },
  'abc-analysis': {
    title: 'ABC Analysis',
    columns: [
      { field: 'item_code', header: 'Item Code' },
      { field: 'item_name', header: 'Item Name' },
      { field: 'annual_usage', header: 'Annual Usage' },
      { field: 'unit_cost', header: 'Unit Cost' },
      { field: 'annual_value', header: 'Annual Value' },
      { field: 'classification', header: 'ABC Class' }
    ]
  }
}

const generateReport = async (reportType: string) => {
  selectedReport.value = reports[reportType]
  reportColumns.value = selectedReport.value.columns
  showReportDialog.value = true
  reportLoading.value = true
  
  try {
    // Simulate API call for report data
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Mock data based on report type
    reportData.value = generateMockData(reportType)
    
    toast.add({ 
      severity: 'success', 
      summary: 'Report Generated', 
      detail: `${selectedReport.value.title} generated successfully` 
    })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to generate report' })
  } finally {
    reportLoading.value = false
  }
}

const generateMockData = (reportType: string) => {
  switch (reportType) {
    case 'stock-levels':
      return [
        { item_code: 'WDG-001', item_name: 'Widget Pro Max', location: 'Main Warehouse', quantity: 150, unit_cost: 25.99, total_value: 3898.50 },
        { item_code: 'CMP-002', item_name: 'Component X', location: 'Main Warehouse', quantity: 8, unit_cost: 45.50, total_value: 364.00 }
      ]
    case 'low-stock':
      return [
        { item_code: 'CMP-002', item_name: 'Component X', current_stock: 8, reorder_point: 20, shortage: 12 }
      ]
    default:
      return []
  }
}

const exportReport = (format: string) => {
  toast.add({ 
    severity: 'info', 
    summary: 'Export', 
    detail: `Exporting report as ${format.toUpperCase()}...` 
  })
}
</script>

<style scoped>
.reports-view {
  padding: 1.5rem;
}

.report-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

:deep(.p-card-title) {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

:deep(.p-card-content) {
  padding-top: 0;
}
</style>