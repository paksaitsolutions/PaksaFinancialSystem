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
import { useReportExport } from '@/composables/useReportExport'

const agedReceivables = ref([
  { customer: 'ABC Corp', current: 15000, days30: 5000, days60: 2000, days90: 1000, total: 23000 },
  { customer: 'XYZ Ltd', current: 8000, days30: 3000, days60: 0, days90: 500, total: 11500 },
  { customer: 'Tech Solutions', current: 12000, days30: 0, days60: 1500, days90: 0, total: 13500 }
])

const agedPayables = ref([
  { vendor: 'Office Supplies Co', current: 2500, days30: 1000, days60: 0, days90: 0, total: 3500 },
  { vendor: 'Utility Company', current: 800, days30: 0, days60: 0, days90: 0, total: 800 },
  { vendor: 'Equipment Rental', current: 0, days30: 1200, days60: 0, days90: 0, total: 1200 }
])

const totalReceivables = computed(() => 
  agedReceivables.value.reduce((sum, item) => sum + item.total, 0)
)

const totalPayables = computed(() => 
  agedPayables.value.reduce((sum, item) => sum + item.total, 0)
)

const formatDate = (date: Date) => date.toLocaleDateString()

const { exportToCSV, exportToPDF, printReport, getExportOptions } = useReportExport()

const exportReceivablesToPDF = () => {
  const data = agedReceivables.value.map(item => ({
    Customer: item.customer,
    Current: `$${item.current}`,
    '1-30 Days': `$${item.days30}`,
    '31-60 Days': `$${item.days60}`,
    '60+ Days': `$${item.days90}`,
    Total: `$${item.total}`
  }))
  exportToPDF('Aged Receivables Report', data, 'Aged_Receivables_Report')
}

const exportPayablesToPDF = () => {
  const data = agedPayables.value.map(item => ({
    Vendor: item.vendor,
    Current: `$${item.current}`,
    '1-30 Days': `$${item.days30}`,
    '31-60 Days': `$${item.days60}`,
    '60+ Days': `$${item.days90}`,
    Total: `$${item.total}`
  }))
  exportToPDF('Aged Payables Report', data, 'Aged_Payables_Report')
}

const printReceivables = () => {
  const data = agedReceivables.value.map(item => ({
    Customer: item.customer,
    Current: `$${item.current}`,
    '1-30 Days': `$${item.days30}`,
    '31-60 Days': `$${item.days60}`,
    '60+ Days': `$${item.days90}`,
    Total: `$${item.total}`
  }))
  printReport('Aged Receivables Report', data)
}

const printPayables = () => {
  const data = agedPayables.value.map(item => ({
    Vendor: item.vendor,
    Current: `$${item.current}`,
    '1-30 Days': `$${item.days30}`,
    '31-60 Days': `$${item.days60}`,
    '60+ Days': `$${item.days90}`,
    Total: `$${item.total}`
  }))
  printReport('Aged Payables Report', data)
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

const receivablesExportOptions = computed(() => 
  getExportOptions('Aged Receivables Report', receivablesData.value, 'Aged_Receivables_Report')
)

const payablesExportOptions = computed(() => 
  getExportOptions('Aged Payables Report', payablesData.value, 'Aged_Payables_Report')
)

onMounted(() => {
  // Load data
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