<template>
  <ResponsiveContainer>
    <Card>
      <template #header>
        <h2 class="p-4 m-0">Asset Reports</h2>
      </template>
      
      <template #content>
        <div v-if="reportData" class="grid">
          <!-- Summary Cards -->
          <div class="col-12 md:col-3">
            <Card class="bg-primary text-white">
              <template #content>
                <div class="text-center">
                  <div class="text-3xl font-bold">{{ reportData?.total_assets || 0 }}</div>
                  <div class="text-sm opacity-90">Total Assets</div>
                </div>
              </template>
            </Card>
          </div>
          
          <div class="col-12 md:col-3">
            <Card class="bg-green-500 text-white">
              <template #content>
                <div class="text-center">
                  <div class="text-3xl font-bold">{{ formatCurrency(reportData?.total_cost || 0) }}</div>
                  <div class="text-sm opacity-90">Total Cost</div>
                </div>
              </template>
            </Card>
          </div>
          
          <div class="col-12 md:col-3">
            <Card class="bg-orange-500 text-white">
              <template #content>
                <div class="text-center">
                  <div class="text-3xl font-bold">{{ formatCurrency(reportData?.total_accumulated_depreciation || 0) }}</div>
                  <div class="text-sm opacity-90">Total Depreciation</div>
                </div>
              </template>
            </Card>
          </div>
          
          <div class="col-12 md:col-3">
            <Card class="bg-blue-500 text-white">
              <template #content>
                <div class="text-center">
                  <div class="text-3xl font-bold">{{ formatCurrency(reportData?.total_book_value || 0) }}</div>
                  <div class="text-sm opacity-90">Total Book Value</div>
                </div>
              </template>
            </Card>
          </div>
        </div>
        
        <div class="grid mt-6">
          <!-- Assets by Category -->
          <div class="col-12 md:col-6">
            <Card>
              <template #header>
                <h3 class="p-4 m-0">Assets by Category</h3>
              </template>
              <template #content>
                <DataTable :value="reportData?.assets_by_category || []" responsiveLayout="scroll">
                  <Column field="category" header="Category"></Column>
                  <Column field="count" header="Count"></Column>
                  <Column field="total_cost" header="Total Cost">
                    <template #body="{ data }">
                      {{ formatCurrency(data.total_cost) }}
                    </template>
                  </Column>
                </DataTable>
              </template>
            </Card>
          </div>
          
          <!-- Assets by Status -->
          <div class="col-12 md:col-6">
            <Card>
              <template #header>
                <h3 class="p-4 m-0">Assets by Status</h3>
              </template>
              <template #content>
                <DataTable :value="reportData?.assets_by_status || []" responsiveLayout="scroll">
                  <Column field="status" header="Status">
                    <template #body="{ data }">
                      <Tag :value="data.status.replace('_', ' ').toUpperCase()" :severity="getStatusSeverity(data.status)" />
                    </template>
                  </Column>
                  <Column field="count" header="Count"></Column>
                </DataTable>
              </template>
            </Card>
          </div>
        </div>
        
        <div class="mt-4">
          <Button 
            label="Refresh Report" 
            icon="pi pi-refresh" 
            @click="loadReport" 
            :loading="loading"
            class="mr-2"
          />
          <Button 
            label="Export Report" 
            icon="pi pi-download" 
            @click="exportReport" 
            severity="secondary"
          />
        </div>
      </template>
    </Card>
  </ResponsiveContainer>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const loading = ref(false)
const reportData = ref(null)

const loadMockData = () => {
  reportData.value = {
    total_assets: 25,
    total_cost: 125000,
    total_accumulated_depreciation: 35000,
    total_book_value: 90000,
    assets_by_category: [
      { category: 'IT Equipment', count: 10, total_cost: 50000 },
      { category: 'Office Furniture', count: 8, total_cost: 25000 },
      { category: 'Vehicles', count: 4, total_cost: 40000 },
      { category: 'Machinery', count: 3, total_cost: 10000 }
    ],
    assets_by_status: [
      { status: 'active', count: 22 },
      { status: 'under_maintenance', count: 2 },
      { status: 'disposed', count: 1 }
    ]
  }
}

const loadReport = async () => {
  try {
    loading.value = true
    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 500))
    loadMockData()
  } catch (error) {
    console.error('Error loading report:', error)
    loadMockData()
  } finally {
    loading.value = false
  }
}

const exportReport = () => {
  console.log('Exporting asset report...')
}

const getStatusSeverity = (status) => {
  const severities = {
    active: 'success',
    disposed: 'danger',
    under_maintenance: 'warning',
    retired: 'secondary'
  }
  return severities[status] || 'info'
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount || 0)
}

onMounted(() => {
  loadReport()
})
</script>