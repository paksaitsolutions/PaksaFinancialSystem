<template>
  <div class="license-management">
    <div class="dashboard-header">
      <h1>License Management</h1>
      <p>Manage software licenses and subscription plans</p>
    </div>

    <div class="summary-cards">
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-key text-blue"></i>
            <span>Active Licenses</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-blue">{{ activeLicenses }}</div>
          <div class="summary-date">Currently in use</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-calendar text-orange"></i>
            <span>Expiring Soon</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-orange">{{ expiringSoon }}</div>
          <div class="summary-date">Within 30 days</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-dollar text-green"></i>
            <span>Monthly Revenue</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-green">${{ monthlyRevenue.toLocaleString() }}</div>
          <div class="summary-date">Subscription income</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-users text-purple"></i>
            <span>Total Users</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-purple">{{ totalUsers }}</div>
          <div class="summary-date">Across all licenses</div>
        </template>
      </Card>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>License Overview</span>
            <Button label="Generate License" icon="pi pi-plus" @click="showGenerateDialog = true" />
          </div>
        </template>
        <template #content>
          <DataTable :value="licenses" responsiveLayout="scroll">
            <Column field="licenseKey" header="License Key">
              <template #body="{ data }">
                <code class="license-key">{{ data.licenseKey }}</code>
              </template>
            </Column>
            <Column field="tenant" header="Tenant" />
            <Column field="plan" header="Plan">
              <template #body="{ data }">
                <Tag :value="data.plan" :severity="getPlanSeverity(data.plan)" />
              </template>
            </Column>
            <Column field="users" header="Users">
              <template #body="{ data }">
                {{ data.currentUsers }} / {{ data.maxUsers }}
              </template>
            </Column>
            <Column field="expiryDate" header="Expires">
              <template #body="{ data }">
                {{ formatDate(data.expiryDate) }}
              </template>
            </Column>
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button icon="pi pi-refresh" class="p-button-rounded p-button-text" @click="renewLicense(data)" />
                  <Button icon="pi pi-pencil" class="p-button-rounded p-button-text" @click="editLicense(data)" />
                  <Button icon="pi pi-ban" class="p-button-rounded p-button-text p-button-danger" @click="revokeLicense(data)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>Subscription Plans</template>
        <template #content>
          <DataTable :value="subscriptionPlans" responsiveLayout="scroll">
            <Column field="name" header="Plan Name" />
            <Column field="price" header="Price">
              <template #body="{ data }">
                ${{ data.price }}/month
              </template>
            </Column>
            <Column field="maxUsers" header="Max Users" />
            <Column field="features" header="Features">
              <template #body="{ data }">
                {{ data.features.join(', ') }}
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <Button icon="pi pi-pencil" class="p-button-rounded p-button-text" @click="editPlan(data)" />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>

    <Dialog v-model:visible="showGenerateDialog" modal header="Generate License" :style="{ width: '500px' }">
      <div class="grid p-fluid">
        <div class="col-12">
          <div class="field">
            <label>Tenant Name</label>
            <InputText v-model="newLicense.tenant" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Subscription Plan</label>
            <Dropdown v-model="newLicense.plan" :options="planOptions" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Max Users</label>
            <InputNumber v-model="newLicense.maxUsers" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Duration (months)</label>
            <InputNumber v-model="newLicense.duration" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showGenerateDialog = false" />
        <Button label="Generate" @click="generateLicense" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showGenerateDialog = ref(false)
const activeLicenses = ref(45)
const expiringSoon = ref(3)
const monthlyRevenue = ref(89500)
const totalUsers = ref(1247)

const licenses = ref([
  { 
    licenseKey: 'PFS-ENT-2023-ABC123', 
    tenant: 'Acme Corp', 
    plan: 'Enterprise', 
    currentUsers: 45, 
    maxUsers: 100, 
    expiryDate: '2024-12-31', 
    status: 'Active' 
  },
  { 
    licenseKey: 'PFS-PRO-2023-DEF456', 
    tenant: 'Tech Solutions', 
    plan: 'Professional', 
    currentUsers: 25, 
    maxUsers: 50, 
    expiryDate: '2024-06-30', 
    status: 'Active' 
  },
  { 
    licenseKey: 'PFS-BAS-2023-GHI789', 
    tenant: 'Small Business', 
    plan: 'Basic', 
    currentUsers: 8, 
    maxUsers: 10, 
    expiryDate: '2023-12-15', 
    status: 'Expiring' 
  }
])

const subscriptionPlans = ref([
  { name: 'Basic', price: 29, maxUsers: 10, features: ['Core Accounting', 'Basic Reports'] },
  { name: 'Professional', price: 79, maxUsers: 50, features: ['Advanced Analytics', 'Multi-Currency', 'API Access'] },
  { name: 'Enterprise', price: 199, maxUsers: 200, features: ['All Features', 'Priority Support', 'Custom Integrations'] }
])

const newLicense = ref({
  tenant: '',
  plan: '',
  maxUsers: 10,
  duration: 12
})

const planOptions = ref(['Basic', 'Professional', 'Enterprise'])

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
    Expiring: 'warning',
    Expired: 'danger',
    Revoked: 'secondary'
  }
  return severities[status] || 'secondary'
}

const generateLicense = () => {
  const licenseKey = `PFS-${newLicense.value.plan.substring(0, 3).toUpperCase()}-${new Date().getFullYear()}-${Math.random().toString(36).substring(2, 8).toUpperCase()}`
  
  licenses.value.push({
    licenseKey,
    tenant: newLicense.value.tenant,
    plan: newLicense.value.plan,
    currentUsers: 0,
    maxUsers: newLicense.value.maxUsers,
    expiryDate: new Date(Date.now() + newLicense.value.duration * 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    status: 'Active'
  })
  
  newLicense.value = { tenant: '', plan: '', maxUsers: 10, duration: 12 }
  showGenerateDialog.value = false
}

const renewLicense = (license: any) => {
  console.log('Renewing license:', license.licenseKey)
}

const editLicense = (license: any) => {
  console.log('Editing license:', license.licenseKey)
}

const revokeLicense = (license: any) => {
  console.log('Revoking license:', license.licenseKey)
}

const editPlan = (plan: any) => {
  console.log('Editing plan:', plan.name)
}
</script>

<style scoped>
.license-management {
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

.license-key {
  font-family: 'Courier New', monospace;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}

.text-blue { color: #3b82f6; }
.text-orange { color: #f59e0b; }
.text-green { color: #10b981; }
.text-purple { color: #8b5cf6; }

@media (max-width: 768px) {
  .license-management {
    padding: 1rem;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>