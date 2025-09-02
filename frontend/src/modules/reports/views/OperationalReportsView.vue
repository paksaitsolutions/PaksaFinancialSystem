<template>
  <div class="operational-reports">
    <div class="reports-header">
      <div class="flex align-items-center">
        <i class="pi pi-cog text-3xl text-primary mr-3"></i>
        <h1 class="reports-title">Operational Reports</h1>
      </div>
      <div class="header-actions">
        <Button label="Export All" icon="pi pi-download" severity="secondary" />
        <Button label="New Report" icon="pi pi-plus" />
      </div>
    </div>

    <div class="reports-grid">
      <Card v-for="report in operationalReports" :key="report.id" class="report-card">
        <template #header>
          <div class="report-header">
            <i :class="report.icon" :style="{ color: report.color }" class="text-2xl"></i>
            <Tag :value="report.status" :severity="getStatusSeverity(report.status)" />
          </div>
        </template>
        <template #title>
          <h3>{{ report.name }}</h3>
        </template>
        <template #subtitle>
          <span>{{ report.category }}</span>
        </template>
        <template #content>
          <p class="report-description">{{ report.description }}</p>
          <div class="report-meta">
            <div class="meta-item">
              <i class="pi pi-clock"></i>
              <span>Last run: {{ formatDate(report.lastRun) }}</span>
            </div>
            <div class="meta-item">
              <i class="pi pi-calendar"></i>
              <span>{{ report.frequency }}</span>
            </div>
          </div>
        </template>
        <template #footer>
          <div class="report-actions">
            <Button label="Run" icon="pi pi-play" @click="runReport(report)" :loading="report.running" />
            <Button label="View" icon="pi pi-eye" severity="info" @click="viewReport(report)" />
            <Button label="Schedule" icon="pi pi-calendar" severity="secondary" @click="scheduleReport(report)" />
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

const operationalReports = ref([
  {
    id: 'inventory-turnover',
    name: 'Inventory Turnover',
    category: 'Inventory Management',
    description: 'Analysis of inventory movement and turnover rates',
    icon: 'pi pi-box',
    color: '#2196F3',
    status: 'Active',
    frequency: 'Weekly',
    lastRun: '2023-11-15T10:30:00',
    running: false
  },
  {
    id: 'vendor-performance',
    name: 'Vendor Performance',
    category: 'Vendor Management',
    description: 'Evaluation of vendor delivery and quality metrics',
    icon: 'pi pi-users',
    color: '#4CAF50',
    status: 'Active',
    frequency: 'Monthly',
    lastRun: '2023-11-14T09:15:00',
    running: false
  },
  {
    id: 'employee-productivity',
    name: 'Employee Productivity',
    category: 'Human Resources',
    description: 'Analysis of employee performance and productivity metrics',
    icon: 'pi pi-chart-bar',
    color: '#FF9800',
    status: 'Active',
    frequency: 'Monthly',
    lastRun: '2023-11-13T14:20:00',
    running: false
  },
  {
    id: 'process-efficiency',
    name: 'Process Efficiency',
    category: 'Operations',
    description: 'Operational process efficiency and bottleneck analysis',
    icon: 'pi pi-cog',
    color: '#9C27B0',
    status: 'Draft',
    frequency: 'Quarterly',
    lastRun: '2023-11-10T11:30:00',
    running: false
  },
  {
    id: 'cost-analysis',
    name: 'Cost Analysis Report',
    category: 'Financial Operations',
    description: 'Detailed analysis of operational costs and efficiency',
    icon: 'pi pi-dollar',
    color: '#607D8B',
    status: 'Active',
    frequency: 'Monthly',
    lastRun: '2023-11-12T16:45:00',
    running: false
  },
  {
    id: 'quality-metrics',
    name: 'Quality Metrics',
    category: 'Quality Control',
    description: 'Quality control metrics and performance indicators',
    icon: 'pi pi-star',
    color: '#795548',
    status: 'Active',
    frequency: 'Weekly',
    lastRun: '2023-11-15T08:00:00',
    running: false
  }
])

const runReport = async (report: any) => {
  report.running = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    report.lastRun = new Date().toISOString()
  } finally {
    report.running = false
  }
}

const viewReport = (report: any) => {
  console.log('Viewing report:', report.name)
}

const scheduleReport = (report: any) => {
  console.log('Scheduling report:', report.name)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const getStatusSeverity = (status: string) => {
  const severities = {
    Active: 'success',
    Draft: 'warning',
    Archived: 'secondary'
  }
  return severities[status] || 'info'
}
</script>

<style scoped>
.operational-reports {
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