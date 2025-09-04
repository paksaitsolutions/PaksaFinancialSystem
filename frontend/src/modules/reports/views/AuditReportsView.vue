<template>
  <div class="audit-reports">
    <div class="dashboard-header">
      <h1>Audit Reports</h1>
      <p>Comprehensive audit trails and compliance reports</p>
    </div>

    <div class="summary-cards">
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-shield text-blue"></i>
            <span>Audit Entries</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-blue">{{ totalAuditEntries.toLocaleString() }}</div>
          <div class="summary-date">This Month</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-exclamation-triangle text-orange"></i>
            <span>Exceptions</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-orange">{{ totalExceptions }}</div>
          <div class="summary-date">Requires Review</div>
        </template>
      </Card>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Audit Trail</span>
            <Button label="Export" icon="pi pi-download" class="p-button-text p-button-sm" @click="exportAuditTrail" />
          </div>
        </template>
        <template #content>
          <DataTable :value="auditTrail" :paginator="true" :rows="10" responsiveLayout="scroll">
            <Column field="timestamp" header="Timestamp">
              <template #body="{ data }">
                {{ formatDateTime(data.timestamp) }}
              </template>
            </Column>
            <Column field="user" header="User" />
            <Column field="action" header="Action" />
            <Column field="entity" header="Entity" />
            <Column field="changes" header="Changes">
              <template #body="{ data }">
                <Button label="View" icon="pi pi-eye" class="p-button-text p-button-sm" @click="viewChanges(data)" />
              </template>
            </Column>
            <Column field="ipAddress" header="IP Address" />
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>
          <span>Compliance Reports</span>
        </template>
        <template #content>
          <DataTable :value="complianceReports" responsiveLayout="scroll">
            <Column field="reportName" header="Report" />
            <Column field="standard" header="Standard" />
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column field="lastReview" header="Last Review">
              <template #body="{ data }">
                {{ formatDate(data.lastReview) }}
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button icon="pi pi-eye" size="small" @click="viewReport(data)" />
                  <Button icon="pi pi-print" size="small" @click="printAuditReport(data)" />
                  <SplitButton icon="pi pi-download" @click="downloadReport(data)" :model="getAuditReportExportOptions(data)" size="small" />
                </div>
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

const totalAuditEntries = ref(1247)
const totalExceptions = ref(3)

const auditTrail = ref([
  { 
    id: 1, 
    timestamp: '2023-11-15T14:30:00', 
    user: 'john.doe@company.com', 
    action: 'CREATE', 
    entity: 'Journal Entry', 
    changes: 'Created JE-001', 
    ipAddress: '192.168.1.100' 
  },
  { 
    id: 2, 
    timestamp: '2023-11-15T14:25:00', 
    user: 'jane.smith@company.com', 
    action: 'UPDATE', 
    entity: 'Invoice', 
    changes: 'Updated INV-2023-001', 
    ipAddress: '192.168.1.101' 
  },
  { 
    id: 3, 
    timestamp: '2023-11-15T14:20:00', 
    user: 'admin@company.com', 
    action: 'DELETE', 
    entity: 'User Account', 
    changes: 'Deleted user temp.user', 
    ipAddress: '192.168.1.1' 
  }
])

const complianceReports = ref([
  { 
    id: 1, 
    reportName: 'SOX Compliance Report', 
    standard: 'Sarbanes-Oxley', 
    status: 'Compliant', 
    lastReview: '2023-11-01' 
  },
  { 
    id: 2, 
    reportName: 'GAAP Adherence Report', 
    standard: 'US GAAP', 
    status: 'Compliant', 
    lastReview: '2023-10-31' 
  },
  { 
    id: 3, 
    reportName: 'Internal Controls Assessment', 
    standard: 'COSO Framework', 
    status: 'Review Required', 
    lastReview: '2023-10-15' 
  }
])

const formatDate = (dateString: string) => new Date(dateString).toLocaleDateString()
const formatDateTime = (dateString: string) => new Date(dateString).toLocaleString()

const getStatusSeverity = (status: string) => {
  const severities = {
    Compliant: 'success',
    'Review Required': 'warning',
    'Non-Compliant': 'danger'
  }
  return severities[status] || 'info'
}

const viewChanges = (auditEntry: any) => {
  console.log('Viewing changes for:', auditEntry.id)
}

const viewReport = (report: any) => {
  console.log('Viewing report:', report.reportName)
}

const { exportToCSV, exportToPDF, printReport } = useReportExport()

const downloadReport = (report: any) => {
  const data = [{
    'Report Name': report.reportName,
    'Standard': report.standard,
    'Status': report.status,
    'Last Review': formatDate(report.lastReview)
  }]
  exportToPDF(report.reportName, data, report.reportName.replace(/\s+/g, '_'))
}

const printAuditReport = (report: any) => {
  const data = [{
    'Report Name': report.reportName,
    'Standard': report.standard,
    'Status': report.status,
    'Last Review': formatDate(report.lastReview)
  }]
  printReport(report.reportName, data)
}

const exportAuditTrail = () => {
  const data = auditTrail.value.map(entry => ({
    'Timestamp': formatDateTime(entry.timestamp),
    'User': entry.user,
    'Action': entry.action,
    'Entity': entry.entity,
    'Changes': entry.changes,
    'IP Address': entry.ipAddress
  }))
  exportToCSV(data, 'Audit_Trail')
}

const getAuditReportExportOptions = (report: any) => [
  {
    label: 'Export to PDF',
    icon: 'pi pi-file-pdf',
    command: () => downloadReport(report)
  },
  {
    label: 'Export to Excel',
    icon: 'pi pi-file-excel',
    command: () => exportToCSV([{
      'Report Name': report.reportName,
      'Standard': report.standard,
      'Status': report.status,
      'Last Review': formatDate(report.lastReview)
    }], report.reportName.replace(/\s+/g, '_'))
  }
]

onMounted(() => {
  // Load data
})
</script>

<style scoped>
.audit-reports {
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
.text-orange { color: #f59e0b; }

@media (max-width: 768px) {
  .audit-reports {
    padding: 1rem;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>