<template>
  <div class="aged-reports">
    <div class="dashboard-header">
      <h1>Aged Receivables & Payables</h1>
      <p>Track outstanding receivables and payables by aging periods</p>
    </div>

    <div class="summary-cards">
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-credit-card text-green"></i>
            <span>Total Receivables</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-green">${{ totalReceivables.toLocaleString() }}</div>
          <div class="summary-date">as of {{ formatDate(new Date()) }}</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-money-bill text-red"></i>
            <span>Total Payables</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-red">${{ totalPayables.toLocaleString() }}</div>
          <div class="summary-date">as of {{ formatDate(new Date()) }}</div>
        </template>
      </Card>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Aged Receivables</span>
            <div class="flex gap-2">
              <Button icon="pi pi-print" size="small" @click="printReceivables" />
              <SplitButton label="Export" icon="pi pi-download" @click="exportReceivablesToPDF" :model="receivablesExportOptions" size="small" />
            </div>
          </div>
        </template>
        <template #content>
          <DataTable :value="agedReceivables" responsiveLayout="scroll">
            <Column field="customer" header="Customer" />
            <Column field="current" header="Current">
              <template #body="{ data }">
                <span class="text-green">${{ data.current.toLocaleString() }}</span>
              </template>
            </Column>
            <Column field="days30" header="1-30 Days">
              <template #body="{ data }">
                <span class="text-orange">${{ data.days30.toLocaleString() }}</span>
              </template>
            </Column>
            <Column field="days60" header="31-60 Days">
              <template #body="{ data }">
                <span class="text-red">${{ data.days60.toLocaleString() }}</span>
              </template>
            </Column>
            <Column field="days90" header="60+ Days">
              <template #body="{ data }">
                <span class="text-red font-bold">${{ data.days90.toLocaleString() }}</span>
              </template>
            </Column>
            <Column field="total" header="Total">
              <template #body="{ data }">
                <span class="font-bold">${{ data.total.toLocaleString() }}</span>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Aged Payables</span>
            <div class="flex gap-2">
              <Button icon="pi pi-print" size="small" @click="printPayables" />
              <SplitButton label="Export" icon="pi pi-download" @click="exportPayablesToPDF" :model="payablesExportOptions" size="small" />
            </div>
          </div>
        </template>
        <template #content>
          <DataTable :value="agedPayables" responsiveLayout="scroll">
            <Column field="vendor" header="Vendor" />
            <Column field="current" header="Current">
              <template #body="{ data }">
                <span class="text-green">${{ data.current.toLocaleString() }}</span>
              </template>
            </Column>
            <Column field="days30" header="1-30 Days">
              <template #body="{ data }">
                <span class="text-orange">${{ data.days30.toLocaleString() }}</span>
              </template>
            </Column>
            <Column field="days60" header="31-60 Days">
              <template #body="{ data }">
                <span class="text-red">${{ data.days60.toLocaleString() }}</span>
              </template>
            </Column>
            <Column field="days90" header="60+ Days">
              <template #body="{ data }">
                <span class="text-red font-bold">${{ data.days90.toLocaleString() }}</span>
              </template>
            </Column>
            <Column field="total" header="Total">
              <template #body="{ data }">
                <span class="font-bold">${{ data.total.toLocaleString() }}</span>
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
import { reportsService } from '@/modules/reports/services/reportsService'

const toast = useToast()
const loading = ref(false)
const agedReceivables = ref([])
const agedPayables = ref([])

const totalReceivables = computed(() => 
  agedReceivables.value.reduce((sum, item) => sum + item.total, 0)
)

const totalPayables = computed(() => 
  agedPayables.value.reduce((sum, item) => sum + item.total, 0)
)

const formatDate = (date: Date) => date.toLocaleDateString()

const exportReceivablesToPDF = () => {
  toast.add({
    severity: 'info',
    summary: 'Export Started',
    detail: 'Exporting Aged Receivables to PDF...',
    life: 3000
  })
}

const exportPayablesToPDF = () => {
  toast.add({
    severity: 'info',
    summary: 'Export Started',
    detail: 'Exporting Aged Payables to PDF...',
    life: 3000
  })
}

const printReceivables = () => {
  toast.add({
    severity: 'info',
    summary: 'Print Started',
    detail: 'Printing Aged Receivables...',
    life: 3000
  })
}

const printPayables = () => {
  toast.add({
    severity: 'info',
    summary: 'Print Started',
    detail: 'Printing Aged Payables...',
    life: 3000
  })
}

const receivablesData = computed(() => agedReceivables.value.map(item => ({
  Customer: item.customer,
  Current: item.current,
  '1-30 Days': item.days30,
  '31-60 Days': item.days60,
  '60+ Days': item.days90,
  Total: item.total
})))

const payablesData = computed(() => agedPayables.value.map(item => ({
  Vendor: item.vendor,
  Current: item.current,
  '1-30 Days': item.days30,
  '31-60 Days': item.days60,
  '60+ Days': item.days90,
  Total: item.total
})))

const receivablesExportOptions = [
  {
    label: 'Export to PDF',
    icon: 'pi pi-file-pdf',
    command: () => exportReceivablesToPDF()
  },
  {
    label: 'Export to Excel',
    icon: 'pi pi-file-excel',
    command: () => toast.add({ severity: 'info', summary: 'Export', detail: 'Exporting to Excel...', life: 3000 })
  }
]

const payablesExportOptions = [
  {
    label: 'Export to PDF',
    icon: 'pi pi-file-pdf',
    command: () => exportPayablesToPDF()
  },
  {
    label: 'Export to Excel',
    icon: 'pi pi-file-excel',
    command: () => toast.add({ severity: 'info', summary: 'Export', detail: 'Exporting to Excel...', life: 3000 })
  }
]

const loadAgingReports = async () => {
  loading.value = true
  try {
    const [arData, apData] = await Promise.all([
      reportsService.getARAging(),
      reportsService.getAPAging()
    ])
    
    agedReceivables.value = arData.aging_buckets.map(bucket => ({
      customer: bucket.customer,
      current: bucket.current,
      days30: bucket.days_30,
      days60: bucket.days_60,
      days90: bucket.days_90,
      total: bucket.total
    }))
    
    agedPayables.value = apData.aging_buckets.map(bucket => ({
      vendor: bucket.vendor,
      current: bucket.current,
      days30: bucket.days_30,
      days60: bucket.days_60,
      days90: bucket.days_90,
      total: bucket.total
    }))
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load aging reports',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadAgingReports()
})
</script>

<style scoped>
.aged-reports {
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

.dashboard-header p {
  color: #6b7280;
  margin: 0;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  height: 100%;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.summary-amount {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.summary-date {
  font-size: 0.75rem;
  color: #6b7280;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

.content-card {
  height: fit-content;
}

.card-title-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.text-green { color: #10b981; }
.text-orange { color: #f59e0b; }
.text-red { color: #ef4444; }

@media (max-width: 768px) {
  .aged-reports {
    padding: 1rem;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>