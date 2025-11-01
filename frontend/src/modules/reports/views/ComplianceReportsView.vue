<template>
  <div class="compliance-dashboard">
    <!-- Dashboard Header -->
    <div class="dashboard-header">
      <div class="flex align-items-center">
        <i class="pi pi-shield text-3xl text-primary mr-3"></i>
        <h1 class="dashboard-title">Compliance Management</h1>
      </div>
      <div class="header-actions">
        <button class="p-button p-button-secondary">
          <i class="pi pi-download"></i> Export All
        </button>
        <button class="p-button">
          <i class="pi pi-plus"></i> New Assessment
        </button>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid mb-6">
      <div class="kpi-card p-card">
        <div class="p-card-body">
          <div class="kpi-content">
            <div class="kpi-icon">
              <i class="pi pi-chart-line" style="color: #10b981;"></i>
            </div>
            <div class="kpi-details">
              <h3>{{ dashboardStats.complianceScore }}%</h3>
              <p>Compliance Score</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card p-card">
        <div class="p-card-body">
          <div class="kpi-content">
            <div class="kpi-icon">
              <i class="pi pi-file-check" style="color: #3b82f6;"></i>
            </div>
            <div class="kpi-details">
              <h3>{{ dashboardStats.activeReports }}</h3>
              <p>Active Reports</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card p-card">
        <div class="p-card-body">
          <div class="kpi-content">
            <div class="kpi-icon">
              <i class="pi pi-exclamation-triangle" style="color: #f59e0b;"></i>
            </div>
            <div class="kpi-details">
              <h3>{{ dashboardStats.risksHigh + dashboardStats.risksMedium }}</h3>
              <p>Open Risks</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="kpi-card p-card">
        <div class="p-card-body">
          <div class="kpi-content">
            <div class="kpi-icon">
              <i class="pi pi-shield" style="color: #8b5cf6;"></i>
            </div>
            <div class="kpi-details">
              <h3>{{ dashboardStats.policiesActive }}</h3>
              <p>Active Policies</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Compliance Reports -->
    <div class="section-header mb-4">
      <h2>Compliance Reports</h2>
    </div>
    <div class="reports-grid mb-6" v-if="!loading">
      <div v-for="report in complianceReports" :key="report.id" class="report-card p-card">
        <div class="p-card-header">
          <div class="report-header">
            <i :class="report.icon" :style="{ color: report.color }" class="text-2xl"></i>
            <span :class="'p-tag p-tag-' + getStatusSeverity(report.status)">{{ report.status }}</span>
          </div>
        </div>
        <div class="p-card-title">
          <h3>{{ report.name }}</h3>
        </div>
        <div class="p-card-content">
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
        </div>
        <div class="p-card-footer">
          <div class="report-actions">
            <button class="p-button p-button-sm" @click="runReport(report)" :disabled="report.running">
              <i class="pi pi-play"></i> Generate
            </button>
            <button class="p-button p-button-info p-button-sm" @click="viewReport(report)">
              <i class="pi pi-eye"></i> View
            </button>
            <button class="p-button p-button-secondary p-button-sm" @click="exportReport(report)">
              <i class="pi pi-download"></i> Export
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Risk Management -->
    <div class="section-header mb-4">
      <h2>Risk Assessment</h2>
    </div>
    <div class="risks-grid mb-6">
      <div v-for="risk in complianceRisks" :key="risk.id" class="risk-card p-card">
        <div class="p-card-content">
          <div class="risk-header">
            <div class="risk-title">
              <h4>{{ risk.title }}</h4>
              <span :class="'p-tag p-tag-' + getRiskSeverity(risk.severity)">{{ risk.severity }}</span>
            </div>
            <div class="risk-category">
              <span class="p-tag p-tag-info">{{ risk.category }}</span>
            </div>
          </div>
          <p class="risk-description">{{ risk.description }}</p>
          <div class="risk-details">
            <div class="detail-item">
              <strong>Impact:</strong> {{ risk.impact }}
            </div>
            <div class="detail-item">
              <strong>Mitigation:</strong> {{ risk.mitigation }}
            </div>
            <div class="detail-item">
              <strong>Due:</strong> {{ formatDate(risk.dueDate) }}
            </div>
          </div>
        </div>
        <div class="p-card-footer">
          <div class="risk-actions">
            <button class="p-button p-button-sm">
              <i class="pi pi-check"></i> Resolve
            </button>
            <button class="p-button p-button-info p-button-sm">
              <i class="pi pi-eye"></i> Details
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Policies -->
    <div class="section-header mb-4">
      <h2>Compliance Policies</h2>
    </div>
    <div class="policies-grid">
      <div v-for="policy in compliancePolicies" :key="policy.id" class="policy-card p-card">
        <div class="p-card-content">
          <div class="policy-header">
            <h4>{{ policy.name }}</h4>
            <div class="policy-compliance">
              <span class="compliance-score">{{ policy.compliance }}%</span>
              <span class="p-tag p-tag-success">{{ policy.status }}</span>
            </div>
          </div>
          <p class="policy-description">{{ policy.description }}</p>
          <div class="policy-meta">
            <div class="meta-item">
              <i class="pi pi-users"></i>
              <span>{{ policy.affectedUsers }} users</span>
            </div>
            <div class="meta-item">
              <i class="pi pi-calendar"></i>
              <span>Next review: {{ formatDate(policy.nextReview) }}</span>
            </div>
          </div>
        </div>
        <div class="p-card-footer">
          <div class="policy-actions">
            <button class="p-button p-button-sm">
              <i class="pi pi-eye"></i> Review
            </button>
            <button class="p-button p-button-info p-button-sm">
              <i class="pi pi-pencil"></i> Edit
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="loading" class="flex justify-content-center align-items-center" style="height: 200px;">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem;"></i>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const complianceReports = ref([])
const complianceRisks = ref([])
const compliancePolicies = ref([])
const dashboardStats = ref({})
const loading = ref(false)

const fetchData = async () => {
  try {
    loading.value = true
    
    // Fetch all compliance data
    const [reportsRes, risksRes, policiesRes, statsRes] = await Promise.all([
      fetch('/api/v1/compliance/reports'),
      fetch('/api/v1/compliance/risks'),
      fetch('/api/v1/compliance/policies'),
      fetch('/api/v1/compliance/dashboard/stats')
    ])
    
    complianceReports.value = await reportsRes.json()
    complianceRisks.value = await risksRes.json()
    compliancePolicies.value = await policiesRes.json()
    dashboardStats.value = await statsRes.json()
    
  } catch (error) {
    console.error('Failed to fetch compliance data:', error)
    // Set default values
    complianceReports.value = []
    complianceRisks.value = []
    compliancePolicies.value = []
    dashboardStats.value = { complianceScore: 0, activeReports: 0, risksHigh: 0, risksMedium: 0, policiesActive: 0 }
    
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load compliance data',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const getRiskSeverity = (severity: string) => {
  const severities = {
    HIGH: 'danger',
    MEDIUM: 'warning', 
    LOW: 'success'
  }
  return severities[severity] || 'info'
}

onMounted(() => {
  fetchData()
})

const runReport = async (report: any) => {
  report.running = true
  try {
    const response = await fetch(`/api/v1/compliance/reports/${report.id}/run`, {
      method: 'POST'
    })
    const result = await response.json()
    
    if (result.success) {
      toast.add({
        severity: 'success',
        summary: 'Report Generated',
        detail: result.message,
        life: 3000
      })
      
      // Update status after successful run
      if (report.status === 'Pending') {
        report.status = 'Active'
      }
    }
  } catch (error) {
    console.error('Failed to run report:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to generate report',
      life: 3000
    })
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
.compliance-dashboard {
  padding: 1.5rem;
  background: var(--surface-ground);
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--surface-card);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.kpi-card {
  background: linear-gradient(135deg, var(--surface-card) 0%, var(--surface-50) 100%);
}

.kpi-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.kpi-icon {
  font-size: 2rem;
  padding: 0.5rem;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
}

.kpi-details h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.kpi-details p {
  margin: 0;
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.risks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1rem;
}

.policies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1rem;
}

.report-card, .risk-card, .policy-card {
  transition: transform 0.2s;
}

.report-card:hover, .risk-card:hover, .policy-card:hover {
  transform: translateY(-2px);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--surface-50);
}

.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.risk-title {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.risk-title h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.risk-description {
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.risk-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 1rem;
}

.detail-item {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

.risk-actions {
  display: flex;
  gap: 0.5rem;
}

.policy-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.policy-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.policy-compliance {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.compliance-score {
  font-weight: 600;
  color: var(--primary-color);
}

.policy-description {
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.policy-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

.policy-actions {
  display: flex;
  gap: 0.5rem;
}

.report-actions {
  display: flex;
  gap: 0.5rem;
}
</style>