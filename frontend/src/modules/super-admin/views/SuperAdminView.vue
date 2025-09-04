<template>
  <div class="super-admin">
    <div class="page-header">
      <h1>Super Admin Dashboard</h1>
    </div>

    <TabView v-model:activeIndex="activeTab">
      <TabPanel header="System Overview">
        <div class="grid">
          <div class="col-12 md:col-3">
            <Card>
              <template #content>
                <div class="stat-card">
                  <div class="stat-value">{{ stats.totalTenants }}</div>
                  <div class="stat-label">Total Tenants</div>
                </div>
              </template>
            </Card>
          </div>
          <div class="col-12 md:col-3">
            <Card>
              <template #content>
                <div class="stat-card">
                  <div class="stat-value">{{ stats.activeUsers }}</div>
                  <div class="stat-label">Active Users</div>
                </div>
              </template>
            </Card>
          </div>
          <div class="col-12 md:col-3">
            <Card>
              <template #content>
                <div class="stat-card">
                  <div class="stat-value">${{ stats.monthlyRevenue.toLocaleString() }}</div>
                  <div class="stat-label">Monthly Revenue</div>
                </div>
              </template>
            </Card>
          </div>
          <div class="col-12 md:col-3">
            <Card>
              <template #content>
                <div class="stat-card">
                  <div class="stat-value">{{ stats.systemHealth }}%</div>
                  <div class="stat-label">System Health</div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </TabPanel>
      
      <TabPanel header="Tenant Management">
        <Card>
          <template #title>Tenant Directory</template>
          <template #content>
            <DataTable :value="tenants" paginator :rows="10">
              <Column field="name" header="Tenant" sortable />
              <Column field="plan" header="Plan" sortable />
              <Column field="users" header="Users" sortable />
              <Column field="status" header="Status" sortable>
                <template #body="slotProps">
                  <Tag :value="slotProps.data.status" :severity="slotProps.data.status === 'Active' ? 'success' : 'danger'" />
                </template>
              </Column>
              <Column header="Actions">
                <template #body="slotProps">
                  <div class="flex gap-2">
                    <Button icon="pi pi-eye" size="small" @click="viewTenant(slotProps.data)" />
                    <Button icon="pi pi-cog" size="small" severity="secondary" @click="manageTenant(slotProps.data)" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>
      
      <TabPanel header="System Configuration">
        <div class="grid">
          <div class="col-12 md:col-6">
            <Card>
              <template #title>Platform Settings</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>Platform Name</label>
                    <InputText v-model="config.platformName" class="w-full" />
                  </div>
                  <div>
                    <label>Maintenance Mode</label>
                    <InputSwitch v-model="config.maintenanceMode" />
                  </div>
                  <Button label="Save Configuration" @click="saveConfig" />
                </div>
              </template>
            </Card>
          </div>
          <div class="col-12 md:col-6">
            <Card>
              <template #title>Security Settings</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>Session Timeout (minutes)</label>
                    <InputNumber v-model="config.sessionTimeout" class="w-full" />
                  </div>
                  <div>
                    <label>Force 2FA</label>
                    <InputSwitch v-model="config.force2FA" />
                  </div>
                  <Button label="Update Security" @click="updateSecurity" />
                </div>
              </template>
            </Card>
          </div>
        </div>
      </TabPanel>
      
      <TabPanel header="System Monitoring">
        <div class="grid">
          <div class="col-12">
            <Card>
              <template #title>System Status</template>
              <template #content>
                <div class="grid">
                  <div class="col-12 md:col-4" v-for="service in services" :key="service.name">
                    <div class="service-status">
                      <div class="flex justify-content-between align-items-center">
                        <span>{{ service.name }}</span>
                        <Tag :value="service.status" :severity="service.status === 'Online' ? 'success' : 'danger'" />
                      </div>
                      <ProgressBar :value="service.uptime" class="mt-2" />
                      <small>{{ service.uptime }}% uptime</small>
                    </div>
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </TabPanel>
    </TabView>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref(0)

const stats = ref({
  totalTenants: 156,
  activeUsers: 2847,
  monthlyRevenue: 125000,
  systemHealth: 98
})

const tenants = ref([
  { id: 1, name: 'Acme Corp', plan: 'Enterprise', users: 150, status: 'Active' },
  { id: 2, name: 'Tech Solutions', plan: 'Professional', users: 75, status: 'Active' },
  { id: 3, name: 'StartUp Co', plan: 'Basic', users: 25, status: 'Suspended' }
])

const config = ref({
  platformName: 'Paksa Financial System',
  maintenanceMode: false,
  sessionTimeout: 30,
  force2FA: false
})

const services = ref([
  { name: 'API Server', status: 'Online', uptime: 99.9 },
  { name: 'Database', status: 'Online', uptime: 99.8 },
  { name: 'Cache Server', status: 'Online', uptime: 98.5 },
  { name: 'File Storage', status: 'Online', uptime: 99.2 }
])

const viewTenant = (tenant: any) => {
  console.log('View tenant:', tenant)
}

const manageTenant = (tenant: any) => {
  console.log('Manage tenant:', tenant)
}

const saveConfig = () => {
  console.log('Save config:', config.value)
}

const updateSecurity = () => {
  console.log('Update security:', config.value)
}
</script>

<style scoped>
.super-admin {
  padding: 1rem;
}

.page-header {
  margin-bottom: 2rem;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--primary-color);
}

.stat-label {
  color: var(--text-color-secondary);
  margin-top: 0.5rem;
}

.service-status {
  padding: 1rem;
  border: 1px solid var(--surface-border);
  border-radius: 6px;
}
</style>