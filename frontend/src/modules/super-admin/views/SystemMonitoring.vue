<template>
  <div class="system-monitoring">
    <div class="dashboard-header">
      <h1>System Monitoring</h1>
      <p>Real-time system performance and health monitoring</p>
    </div>

    <div class="summary-cards">
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-server text-green"></i>
            <span>System Status</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-green">{{ systemStatus }}</div>
          <div class="summary-date">All systems operational</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-chart-line text-blue"></i>
            <span>CPU Usage</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-blue">{{ cpuUsage }}%</div>
          <div class="summary-date">Current load</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-database text-orange"></i>
            <span>Memory Usage</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-orange">{{ memoryUsage }}%</div>
          <div class="summary-date">{{ memoryUsed }} / {{ memoryTotal }}</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-users text-purple"></i>
            <span>Active Users</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-purple">{{ activeUsers }}</div>
          <div class="summary-date">Currently online</div>
        </template>
      </Card>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>System Metrics</span>
            <Button label="Refresh" icon="pi pi-refresh" class="p-button-text p-button-sm" @click="refreshMetrics" />
          </div>
        </template>
        <template #content>
          <DataTable :value="systemMetrics" responsiveLayout="scroll">
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
      
      <Card class="content-card">
        <template #title>
          <span>System Alerts</span>
        </template>
        <template #content>
          <DataTable :value="systemAlerts" responsiveLayout="scroll">
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
                <Button icon="pi pi-check" class="p-button-rounded p-button-text" @click="acknowledgeAlert(data)" />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const systemStatus = ref('Healthy')
const cpuUsage = ref(45)
const memoryUsage = ref(68)
const memoryUsed = ref('6.8 GB')
const memoryTotal = ref('10 GB')
const activeUsers = ref(127)

const systemMetrics = ref([
  { metric: 'Database Connections', current: '45/100', threshold: '80', status: 'Normal', lastUpdated: new Date().toISOString() },
  { metric: 'API Response Time', current: '120ms', threshold: '500ms', status: 'Normal', lastUpdated: new Date().toISOString() },
  { metric: 'Disk Usage', current: '75%', threshold: '90%', status: 'Warning', lastUpdated: new Date().toISOString() },
  { metric: 'Network Latency', current: '25ms', threshold: '100ms', status: 'Normal', lastUpdated: new Date().toISOString() }
])

const systemAlerts = ref([
  { id: 1, severity: 'Warning', message: 'High disk usage detected', component: 'Storage', timestamp: new Date().toISOString() },
  { id: 2, severity: 'Info', message: 'Scheduled backup completed', component: 'Backup', timestamp: new Date().toISOString() },
  { id: 3, severity: 'Critical', message: 'Database connection pool exhausted', component: 'Database', timestamp: new Date().toISOString() }
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

const refreshMetrics = () => {
  // Simulate metric updates
  cpuUsage.value = Math.floor(Math.random() * 100)
  memoryUsage.value = Math.floor(Math.random() * 100)
  activeUsers.value = Math.floor(Math.random() * 200) + 50
}

const acknowledgeAlert = (alert: any) => {
  console.log('Acknowledging alert:', alert.id)
}

onMounted(() => {
  refreshInterval = setInterval(refreshMetrics, 30000) // Refresh every 30 seconds
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.system-monitoring {
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
.text-blue { color: #3b82f6; }
.text-orange { color: #f59e0b; }
.text-purple { color: #8b5cf6; }

@media (max-width: 768px) {
  .system-monitoring {
    padding: 1rem;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>