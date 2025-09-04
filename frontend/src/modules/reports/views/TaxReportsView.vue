<template>
  <div class="tax-reports">
    <div class="dashboard-header">
      <h1>Tax Reports</h1>
      <p>Generate and manage tax compliance reports</p>
    </div>

    <div class="summary-cards">
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-calculator text-blue"></i>
            <span>Sales Tax Collected</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-blue">${{ salesTaxCollected.toLocaleString() }}</div>
          <div class="summary-date">Current Period</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-money-bill text-green"></i>
            <span>Income Tax Liability</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-green">${{ incomeTaxLiability.toLocaleString() }}</div>
          <div class="summary-date">Estimated</div>
        </template>
      </Card>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Available Tax Reports</span>
            <Button label="Generate All" icon="pi pi-play" class="p-button-sm" @click="generateAllReports" />
          </div>
        </template>
        <template #content>
          <DataTable :value="taxReports" responsiveLayout="scroll">
            <Column field="name" header="Report Name" />
            <Column field="period" header="Period" />
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column field="lastGenerated" header="Last Generated">
              <template #body="{ data }">
                {{ formatDate(data.lastGenerated) }}
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button icon="pi pi-play" size="small" @click="generateReport(data)" />
                  <Button icon="pi pi-print" size="small" @click="printTaxReport(data)" />
                  <SplitButton icon="pi pi-download" @click="downloadReport(data)" :model="getTaxReportExportOptions(data)" size="small" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>
          <span>Tax Summary by Jurisdiction</span>
        </template>
        <template #content>
          <DataTable :value="taxByJurisdiction" responsiveLayout="scroll">
            <Column field="jurisdiction" header="Jurisdiction" />
            <Column field="taxType" header="Tax Type" />
            <Column field="rate" header="Rate">
              <template #body="{ data }">
                {{ data.rate }}%
              </template>
            </Column>
            <Column field="taxableAmount" header="Taxable Amount">
              <template #body="{ data }">
                ${{ data.taxableAmount.toLocaleString() }}
              </template>
            </Column>
            <Column field="taxAmount" header="Tax Amount">
              <template #body="{ data }">
                <span class="font-bold">${{ data.taxAmount.toLocaleString() }}</span>
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

const salesTaxCollected = ref(15420)
const incomeTaxLiability = ref(45600)

const taxReports = ref([
  { id: 1, name: 'Sales Tax Return', period: 'Q4 2023', status: 'Ready', lastGenerated: '2023-11-15' },
  { id: 2, name: 'Income Tax Return', period: '2023', status: 'Draft', lastGenerated: '2023-11-10' },
  { id: 3, name: 'Payroll Tax Report', period: 'November 2023', status: 'Filed', lastGenerated: '2023-11-01' },
  { id: 4, name: 'VAT Return', period: 'Q4 2023', status: 'Pending', lastGenerated: '2023-10-31' }
])

const taxByJurisdiction = ref([
  { jurisdiction: 'Federal', taxType: 'Income Tax', rate: 21, taxableAmount: 150000, taxAmount: 31500 },
  { jurisdiction: 'State', taxType: 'Sales Tax', rate: 8.5, taxableAmount: 85000, taxAmount: 7225 },
  { jurisdiction: 'Local', taxType: 'Property Tax', rate: 1.2, taxableAmount: 500000, taxAmount: 6000 }
])

const formatDate = (dateString: string) => new Date(dateString).toLocaleDateString()

const getStatusSeverity = (status: string) => {
  const severities = {
    Ready: 'success',
    Draft: 'warning',
    Filed: 'info',
    Pending: 'secondary'
  }
  return severities[status] || 'info'
}

const { exportToCSV, exportToPDF, printReport } = useReportExport()

const generateReport = (report: any) => {
  console.log('Generating report:', report.name)
}

const downloadReport = (report: any) => {
  const data = [{
    'Report Name': report.name,
    'Period': report.period,
    'Status': report.status,
    'Last Generated': formatDate(report.lastGenerated)
  }]
  exportToPDF(report.name, data, report.name.replace(/\s+/g, '_'))
}

const printTaxReport = (report: any) => {
  const data = [{
    'Report Name': report.name,
    'Period': report.period,
    'Status': report.status,
    'Last Generated': formatDate(report.lastGenerated)
  }]
  printReport(report.name, data)
}

const exportTaxReportToExcel = (report: any) => {
  const data = [{
    'Report Name': report.name,
    'Period': report.period,
    'Status': report.status,
    'Last Generated': formatDate(report.lastGenerated)
  }]
  exportToCSV(data, report.name.replace(/\s+/g, '_'))
}

const generateAllReports = () => {
  const data = taxReports.value.map(report => ({
    'Report Name': report.name,
    'Period': report.period,
    'Status': report.status,
    'Last Generated': formatDate(report.lastGenerated)
  }))
  exportToCSV(data, 'All_Tax_Reports')
}

const getTaxReportExportOptions = (report: any) => [
  {
    label: 'Export to PDF',
    icon: 'pi pi-file-pdf',
    command: () => downloadReport(report)
  },
  {
    label: 'Export to Excel',
    icon: 'pi pi-file-excel',
    command: () => exportTaxReportToExcel(report)
  }
]

onMounted(() => {
  // Load data
})
</script>

<style scoped>
.tax-reports {
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

.text-blue { color: #3b82f6; }
.text-green { color: #10b981; }

@media (max-width: 768px) {
  .tax-reports {
    padding: 1rem;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>