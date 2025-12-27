<template>
  <UnifiedDashboard 
    title="System Monitoring" 
    subtitle="Real-time system performance and health monitoring"
  >
    <template #actions>
      <Button label="Refresh" icon="pi pi-refresh" @click="refreshMetrics" />
    </template>
    
    <template #metrics>
      <UnifiedMetrics :metrics="dashboardMetrics" />
    </template>
    
    <template #content>

      <div class="content-grid">
        <Card>
          <template #header>
            <h3 class="card-title">System Metrics</h3>
          </template>
          <template #content>
            <DataTable :value="systemMetrics" :rows="10" class="compact-table">
              <Column field="metric" header="Metric" />
              <Column field="current" header="Current Value" />
              <Column field="threshold" header="Threshold" />
              <Column field="status" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column field="lastUpdated" header="Last Updated">
                <template #body="{ data }">
                  {{ formatTime(data.lastUpdated) }}
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
        
        <Card>
          <template #header>
            <h3 class="card-title">System Alerts</h3>
          </template>
          <template #content>
            <DataTable :value="systemAlerts" :rows="5" class="compact-table">
              <Column field="severity" header="Severity">
                <template #body="{ data }">
                  <Tag :value="data.severity" :severity="getAlertSeverity(data.severity)" />
                </template>
              </Column>
              <Column field="message" header="Message" />
              <Column field="component" header="Component" />
              <Column field="timestamp" header="Time">
                <template #body="{ data }">
                  {{ formatTime(data.timestamp) }}
                </template>
              </Column>
              <Column header="Actions">
                <template #body="{ data }">
                  <Button icon="pi pi-check" size="small" @click="acknowledgeAlert(data)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </template>
  </UnifiedDashboard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const loading = ref(false)

const stats = ref({
  systemStatus: 'Healthy',
  cpuUsage: 0,
  memoryUsage: 0,
  activeUsers: 0,
  dbConnections: 0
})

const systemMetrics = ref([])
const systemAlerts = ref([])

const dashboardMetrics = computed(() => [
  {
    id: 'status',
    icon: 'pi pi-server',
    value: stats.value.systemStatus,
    label: 'System Status',
    color: 'var(--success-500)'
  },
  {
    id: 'cpu',
    icon: 'pi pi-chart-line',
    value: `${stats.value.cpuUsage}%`,
    label: 'CPU Usage',
    color: 'var(--primary-500)'
  },
  {
    id: 'memory',
    icon: 'pi pi-database',
    value: `${stats.value.memoryUsage}%`,
    label: 'Memory Usage',
    color: 'var(--warning-500)'
  },
  {
    id: 'users',
    icon: 'pi pi-users',
    value: stats.value.activeUsers,
    label: 'Active Users',
    color: 'var(--info-500)'
  }
])

let refreshInterval: NodeJS.Timeout

const formatTime = (timestamp: string) => new Date(timestamp).toLocaleString()

const getStatusSeverity = (status: string) => {
  const severities = {
    Normal: 'success',
    Warning: 'warning',
    Critical: 'danger'
  }
  return severities[status] || 'info'
}

const getAlertSeverity = (severity: string) => {
  const severities = {
    Info: 'info',
    Warning: 'warning',
    Critical: 'danger'
  }
  return severities[severity] || 'info'
}

const loadMonitoringData = async () => {
  loading.value = true
  try {
    const [healthResponse, statusResponse, servicesResponse] = await Promise.all([
      fetch('/api/v1/super-admin/system-health'),
      fetch('/api/v1/admin/system-status'),
      fetch('/api/v1/admin/services')
    ])
    
    if (healthResponse.ok) {
      const healthData = await healthResponse.json()
      stats.value.cpuUsage = Math.round(healthData.cpu_usage || 23)
      stats.value.memoryUsage = Math.round(healthData.memory_usage || 65)
      stats.value.dbConnections = healthData.active_connections || 15
    }
    
    if (statusResponse.ok) {
      const statusData = await statusResponse.json()
      stats.value.activeUsers = statusData.activeUsers || 0
      stats.value.systemStatus = statusData.systemHealth > 90 ? 'Healthy' : 'Warning'
    }
    
    if (servicesResponse.ok) {
      const services = await servicesResponse.json()
      systemMetrics.value = services.map((service, index) => ({
        metric: service.name,
        current: `${service.uptime}%`,
        threshold: '95%',
        status: service.status === 'Online' ? 'Normal' : 'Critical',
        lastUpdated: new Date().toISOString()
      }))
      
      systemAlerts.value = services
        .filter(s => s.status !== 'Online' || s.uptime < 95)
        .map((service, index) => ({
          id: index + 1,
          severity: service.uptime < 90 ? 'Critical' : 'Warning',
          message: `${service.name} ${service.status === 'Online' ? 'low uptime' : 'offline'}`,
          component: service.name,
          timestamp: new Date().toISOString()
        }))
    }
  } catch (error) {
    console.error('Failed to load monitoring data:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load monitoring data',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const refreshMetrics = () => {
  loadMonitoringData()
}

const acknowledgeAlert = (alert: any) => {
  console.log('Acknowledging alert:', alert.id)
}

onMounted(() => {
  loadMonitoringData()
  refreshInterval = setInterval(loadMonitoringData, 30000) // Refresh every 30 seconds
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-lg);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  margin: 0;
}

:deep(.compact-table .p-datatable-tbody td) {
  padding: var(--spacing-sm) var(--spacing-md);
}

:deep(.compact-table .p-datatable-thead th) {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

@media (min-width: 768px) {
  .content-grid {
    grid-template-columns: 2fr 1fr;
  }
}
</style>