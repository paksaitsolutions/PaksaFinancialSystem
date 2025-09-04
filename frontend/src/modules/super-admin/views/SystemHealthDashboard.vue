<template>
  <div class="system-health">
    <div class="dashboard-header">
      <h1>System Health Dashboard</h1>
      <p>Real-time system health monitoring and diagnostics</p>
    </div>

    <div class="summary-cards">
      <Card class="summary-card" :class="getHealthClass(overallHealth)">
        <template #title>
          <div class="card-title">
            <i class="pi pi-heart text-red"></i>
            <span>Overall Health</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount">{{ overallHealth }}%</div>
          <div class="summary-date">{{ getHealthStatus(overallHealth) }}</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-server text-blue"></i>
            <span>Services</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-blue">{{ runningServices }}/{{ totalServices }}</div>
          <div class="summary-date">Services running</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-clock text-green"></i>
            <span>Uptime</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-green">{{ uptime }}</div>
          <div class="summary-date">{{ uptimePercent }}% availability</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-exclamation-triangle text-orange"></i>
            <span>Active Alerts</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-orange">{{ activeAlerts }}</div>
          <div class="summary-date">Require attention</div>
        </template>
      </Card>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Service Status</span>
            <Button label="Refresh All" icon="pi pi-refresh" class="p-button-text p-button-sm" @click="refreshServices" />
          </div>
        </template>
        <template #content>
          <DataTable :value="services" responsiveLayout="scroll">
            <Column field="name" header="Service" />
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getServiceSeverity(data.status)" />
              </template>
            </Column>
            <Column field="health" header="Health">
              <template #body="{ data }">
                <div class="health-bar">
                  <div class="health-fill" :style="{ width: data.health + '%', backgroundColor: getHealthColor(data.health) }"></div>
                  <span class="health-text">{{ data.health }}%</span>
                </div>
              </template>
            </Column>
            <Column field="responseTime" header="Response Time" />
            <Column field="lastCheck" header="Last Check">
              <template #body="{ data }">
                {{ formatTime(data.lastCheck) }}
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button icon="pi pi-play" class="p-button-rounded p-button-text" @click="startService(data)" v-if="data.status === 'Stopped'" />
                  <Button icon="pi pi-stop" class="p-button-rounded p-button-text" @click="stopService(data)" v-if="data.status === 'Running'" />
                  <Button icon="pi pi-refresh" class="p-button-rounded p-button-text" @click="restartService(data)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>System Resources</template>
        <template #content>
          <div class="resource-metrics">
            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-label">CPU Usage</span>
                <span class="metric-value">{{ cpuUsage }}%</span>
              </div>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: cpuUsage + '%', backgroundColor: getMetricColor(cpuUsage) }"></div>
              </div>
            </div>
            
            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-label">Memory Usage</span>
                <span class="metric-value">{{ memoryUsage }}%</span>
              </div>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: memoryUsage + '%', backgroundColor: getMetricColor(memoryUsage) }"></div>
              </div>
            </div>
            
            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-label">Disk Usage</span>
                <span class="metric-value">{{ diskUsage }}%</span>
              </div>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: diskUsage + '%', backgroundColor: getMetricColor(diskUsage) }"></div>
              </div>
            </div>
            
            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-label">Network I/O</span>
                <span class="metric-value">{{ networkIO }} MB/s</span>
              </div>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: (networkIO / 100) * 100 + '%', backgroundColor: '#3b82f6' }"></div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <div class="alerts-section">
      <Card class="content-card">
        <template #title>Recent Health Alerts</template>
        <template #content>
          <DataTable :value="healthAlerts" responsiveLayout="scroll">
            <Column field="severity" header="Severity">
              <template #body="{ data }">
                <Tag :value="data.severity" :severity="getAlertSeverity(data.severity)" />
              </template>
            </Column>
            <Column field="message" header="Message" />
            <Column field="service" header="Service" />
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

const overallHealth = ref(92)
const runningServices = ref(8)
const totalServices = ref(10)
const uptime = ref('15d 7h 23m')
const uptimePercent = ref(99.8)
const activeAlerts = ref(2)
const cpuUsage = ref(45)
const memoryUsage = ref(68)
const diskUsage = ref(75)
const networkIO = ref(23)

const services = ref([
  { name: 'Web Server', status: 'Running', health: 98, responseTime: '45ms', lastCheck: new Date().toISOString() },
  { name: 'Database', status: 'Running', health: 95, responseTime: '12ms', lastCheck: new Date().toISOString() },
  { name: 'API Gateway', status: 'Running', health: 89, responseTime: '78ms', lastCheck: new Date().toISOString() },
  { name: 'Cache Server', status: 'Running', health: 92, responseTime: '5ms', lastCheck: new Date().toISOString() },
  { name: 'File Storage', status: 'Warning', health: 75, responseTime: '156ms', lastCheck: new Date().toISOString() },
  { name: 'Email Service', status: 'Stopped', health: 0, responseTime: 'N/A', lastCheck: new Date().toISOString() }
])

const healthAlerts = ref([
  { id: 1, severity: 'Warning', message: 'High disk usage detected on primary server', service: 'File Storage', timestamp: new Date().toISOString() },
  { id: 2, severity: 'Critical', message: 'Email service is down', service: 'Email Service', timestamp: new Date().toISOString() },
  { id: 3, severity: 'Info', message: 'Scheduled maintenance completed', service: 'Database', timestamp: new Date().toISOString() }
])

let refreshInterval: NodeJS.Timeout

const formatTime = (timestamp: string) => new Date(timestamp).toLocaleString()

const getHealthClass = (health: number) => {
  if (health >= 90) return 'health-excellent'
  if (health >= 70) return 'health-good'
  if (health >= 50) return 'health-warning'
  return 'health-critical'
}

const getHealthStatus = (health: number) => {
  if (health >= 90) return 'Excellent'
  if (health >= 70) return 'Good'
  if (health >= 50) return 'Warning'
  return 'Critical'
}

const getHealthColor = (health: number) => {
  if (health >= 90) return '#10b981'
  if (health >= 70) return '#f59e0b'
  return '#ef4444'
}

const getMetricColor = (value: number) => {
  if (value >= 80) return '#ef4444'
  if (value >= 60) return '#f59e0b'
  return '#10b981'
}

const getServiceSeverity = (status: string) => {
  const severities = {
    Running: 'success',
    Warning: 'warning',
    Stopped: 'danger'
  }
  return severities[status] || 'secondary'
}

const getAlertSeverity = (severity: string) => {
  const severities = {
    Info: 'info',
    Warning: 'warning',
    Critical: 'danger'
  }
  return severities[severity] || 'info'
}

const refreshServices = () => {
  console.log('Refreshing all services')
}

const startService = (service: any) => {
  console.log('Starting service:', service.name)
}

const stopService = (service: any) => {
  console.log('Stopping service:', service.name)
}

const restartService = (service: any) => {
  console.log('Restarting service:', service.name)
}

const acknowledgeAlert = (alert: any) => {
  console.log('Acknowledging alert:', alert.id)
}

onMounted(() => {
  refreshInterval = setInterval(() => {
    // Simulate real-time updates
    cpuUsage.value = Math.floor(Math.random() * 100)
    memoryUsage.value = Math.floor(Math.random() * 100)
    networkIO.value = Math.floor(Math.random() * 50)
  }, 5000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.system-health {
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

.health-excellent {
  border-left: 4px solid #10b981;
}

.health-good {
  border-left: 4px solid #f59e0b;
}

.health-warning {
  border-left: 4px solid #f59e0b;
}

.health-critical {
  border-left: 4px solid #ef4444;
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
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.alerts-section {
  margin-top: 2rem;
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

.health-bar {
  position: relative;
  width: 100%;
  height: 20px;
  background: #f3f4f6;
  border-radius: 10px;
  overflow: hidden;
}

.health-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.health-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.5);
}

.resource-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-weight: 600;
  color: #374151;
}

.metric-value {
  font-weight: 700;
  color: #1f2937;
}

.metric-bar {
  width: 100%;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.text-red { color: #ef4444; }
.text-blue { color: #3b82f6; }
.text-green { color: #10b981; }
.text-orange { color: #f59e0b; }

@media (max-width: 768px) {
  .system-health {
    padding: 1rem;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
  
  .main-content {
    grid-template-columns: 1fr;
  }
}
</style>