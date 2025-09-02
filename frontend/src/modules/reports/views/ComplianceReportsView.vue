<template>
  <div class="compliance-reports">
    <div class="reports-header">
      <div class="flex align-items-center">
        <i class="pi pi-shield text-3xl text-primary mr-3"></i>
        <h1 class="reports-title">Compliance Reports</h1>
      </div>
      <div class="header-actions">
        <Button label="Export All" icon="pi pi-download" severity="secondary" />
        <Button label="New Report" icon="pi pi-plus" />
      </div>
    </div>

    <div class="reports-grid">
      <Card v-for="report in complianceReports" :key="report.id" class="report-card">
        <template #header>
          <div class="report-header">
            <i :class="report.icon" :style="{ color: report.color }" class="text-2xl"></i>
            <Tag :value="report.status" :severity="getStatusSeverity(report.status)" />
          </div>
        </template>
        <template #title>
          <h3>{{ report.name }}</h3>
        </template>
        <template #content>
          <p class="report-description">{{ report.description }}</p>
          <div class="report-meta">
            <div class="meta-item">
              <i class="pi pi-calendar"></i>
              <span>Due: {{ formatDate(report.dueDate) }}</span>
            </div>
            <div class="meta-item">
              <i class="pi pi-flag"></i>
              <span>{{ report.priority }}</span>
            </div>
          </div>
        </template>
        <template #footer>
          <div class="report-actions">
            <Button label="Generate" icon="pi pi-play" @click="runReport(report)" :loading="report.running" />
            <Button label="View" icon="pi pi-eye" severity="info" @click="viewReport(report)" />
            <Button label="Export" icon="pi pi-download" severity="secondary" @click="exportReport(report)" />
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Tag from 'primevue/tag'

const complianceReports = ref([
  {
    id: 'tax-compliance',
    name: 'Tax Compliance Report',
    description: 'Comprehensive tax compliance status and requirements',
    icon: 'pi pi-percentage',
    color: '#F44336',
    status: 'Active',
    dueDate: '2023-12-31',
    priority: 'High',
    running: false
  },
  {
    id: 'audit-trail',
    name: 'Audit Trail Report',
    description: 'Complete audit trail of all financial transactions',
    icon: 'pi pi-search',
    color: '#2196F3',
    status: 'Active',
    dueDate: '2023-11-30',
    priority: 'Medium',
    running: false
  },
  {
    id: 'regulatory-filing',
    name: 'Regulatory Filing',
    description: 'Required regulatory submissions and filings',
    icon: 'pi pi-file',
    color: '#FF9800',
    status: 'Pending',
    dueDate: '2023-12-15',
    priority: 'High',
    running: false
  },
  {
    id: 'internal-controls',
    name: 'Internal Controls Assessment',
    description: 'Evaluation of internal control effectiveness',
    icon: 'pi pi-shield',
    color: '#4CAF50',
    status: 'Draft',
    dueDate: '2024-01-15',
    priority: 'Medium',
    running: false
  }
])

const runReport = async (report: any) => {
  report.running = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    // Update status after successful run
    if (report.status === 'Pending') {
      report.status = 'Active'
    }
  } finally {
    report.running = false
  }
}

const viewReport = (report: any) => {
  console.log('Viewing report:', report.name)
}

const exportReport = (report: any) => {
  console.log('Exporting report:', report.name)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const getStatusSeverity = (status: string) => {
  const severities = {
    Active: 'success',
    Pending: 'warning',
    Draft: 'info',
    Overdue: 'danger'
  }
  return severities[status] || 'secondary'
}
</script>

<style scoped>
.compliance-reports {
  padding: 1.5rem;
  background: var(--surface-ground);
  min-height: 100vh;
}

.reports-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--surface-card);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.reports-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.report-card {
  transition: transform 0.2s;
}

.report-card:hover {
  transform: translateY(-2px);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--surface-50);
}

.report-description {
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
}

.report-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.report-actions {
  display: flex;
  gap: 0.5rem;
}
</style>