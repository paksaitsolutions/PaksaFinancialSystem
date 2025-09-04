<template>
  <div class="platform-analytics">
    <div class="dashboard-header">
      <h1>Platform Analytics</h1>
      <p>Comprehensive analytics and insights across all tenants</p>
    </div>

    <div class="summary-cards">
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-building text-blue"></i>
            <span>Total Tenants</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-blue">{{ totalTenants }}</div>
          <div class="summary-change text-green">+{{ tenantGrowth }}% this month</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-users text-green"></i>
            <span>Total Users</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-green">{{ totalUsers }}</div>
          <div class="summary-change text-green">+{{ userGrowth }}% this month</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-dollar text-orange"></i>
            <span>Monthly Revenue</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-orange">${{ monthlyRevenue.toLocaleString() }}</div>
          <div class="summary-change text-green">+{{ revenueGrowth }}% vs last month</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-chart-line text-purple"></i>
            <span>System Uptime</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-purple">{{ systemUptime }}%</div>
          <div class="summary-change text-green">{{ uptimeDays }} days</div>
        </template>
      </Card>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Tenant Analytics</span>
            <Dropdown v-model="selectedPeriod" :options="periods" @change="loadAnalytics" />
          </div>
        </template>
        <template #content>
          <DataTable :value="tenantAnalytics" responsiveLayout="scroll">
            <Column field="tenantName" header="Tenant" />
            <Column field="plan" header="Plan">
              <template #body="{ data }">
                <Tag :value="data.plan" :severity="getPlanSeverity(data.plan)" />
              </template>
            </Column>
            <Column field="users" header="Users" />
            <Column field="transactions" header="Transactions" />
            <Column field="revenue" header="Revenue">
              <template #body="{ data }">
                ${{ data.revenue.toLocaleString() }}
              </template>
            </Column>
            <Column field="lastActive" header="Last Active">
              <template #body="{ data }">
                {{ formatDate(data.lastActive) }}
              </template>
            </Column>
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>Usage Statistics</template>
        <template #content>
          <div class="usage-stats">
            <div class="stat-item">
              <div class="stat-label">API Calls (24h)</div>
              <div class="stat-value">{{ apiCalls.toLocaleString() }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Storage Used</div>
              <div class="stat-value">{{ storageUsed }} GB</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Database Size</div>
              <div class="stat-value">{{ databaseSize }} GB</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Backup Size</div>
              <div class="stat-value">{{ backupSize }} GB</div>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const selectedPeriod = ref('Last 30 Days')
const totalTenants = ref(45)
const tenantGrowth = ref(12)
const totalUsers = ref(1247)
const userGrowth = ref(18)
const monthlyRevenue = ref(89500)
const revenueGrowth = ref(15)
const systemUptime = ref(99.9)
const uptimeDays = ref(127)
const apiCalls = ref(2847392)
const storageUsed = ref(245)
const databaseSize = ref(89)
const backupSize = ref(156)

const periods = ref(['Last 7 Days', 'Last 30 Days', 'Last 90 Days', 'Last Year'])

const tenantAnalytics = ref([
  { tenantName: 'Acme Corp', plan: 'Enterprise', users: 45, transactions: 1250, revenue: 15000, lastActive: '2023-11-15', status: 'Active' },
  { tenantName: 'Tech Solutions', plan: 'Professional', users: 25, transactions: 890, revenue: 7500, lastActive: '2023-11-14', status: 'Active' },
  { tenantName: 'Small Business Inc', plan: 'Basic', users: 8, transactions: 340, revenue: 2900, lastActive: '2023-11-13', status: 'Trial' },
  { tenantName: 'Global Enterprises', plan: 'Enterprise', users: 120, transactions: 3400, revenue: 25000, lastActive: '2023-11-15', status: 'Active' }
])

const formatDate = (dateString: string) => new Date(dateString).toLocaleDateString()

const getPlanSeverity = (plan: string) => {
  const severities = {
    Enterprise: 'success',
    Professional: 'warning',
    Basic: 'info'
  }
  return severities[plan] || 'secondary'
}

const getStatusSeverity = (status: string) => {
  const severities = {
    Active: 'success',
    Trial: 'warning',
    Suspended: 'danger'
  }
  return severities[status] || 'secondary'
}

const loadAnalytics = () => {
  console.log('Loading analytics for period:', selectedPeriod.value)
}

onMounted(() => {
  loadAnalytics()
})
</script>

<style scoped>
.platform-analytics {
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

.summary-change {
  font-size: 0.875rem;
  font-weight: 600;
}

.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
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

.usage-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 8px;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
}

.text-blue { color: #3b82f6; }
.text-green { color: #10b981; }
.text-orange { color: #f59e0b; }
.text-purple { color: #8b5cf6; }

@media (max-width: 768px) {
  .platform-analytics {
    padding: 1rem;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
  
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .usage-stats {
    grid-template-columns: 1fr;
  }
}
</style>