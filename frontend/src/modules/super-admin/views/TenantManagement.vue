<template>
  <div class="tenant-management">
    <div class="page-header">
      <h1>Tenant Management</h1>
      <Button label="Add New Tenant" icon="pi pi-plus" @click="showAddDialog = true" />
    </div>

    <div class="grid">
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="stat-card">
              <div class="stat-value">{{ tenants.length }}</div>
              <div class="stat-label">Total Tenants</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="stat-card">
              <div class="stat-value">{{ activeTenants }}</div>
              <div class="stat-label">Active Tenants</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="stat-card">
              <div class="stat-value">{{ suspendedTenants }}</div>
              <div class="stat-label">Suspended</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="stat-card">
              <div class="stat-value">${{ totalRevenue.toLocaleString() }}</div>
              <div class="stat-label">Monthly Revenue</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Card class="mt-4">
      <template #title>Tenant Directory</template>
      <template #content>
        <DataTable :value="tenants" paginator :rows="10" dataKey="id" 
                   filterDisplay="menu" :globalFilterFields="['name', 'domain', 'status']" :filters="filters">
          <template #header>
            <div class="flex justify-content-between">
              <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText v-model="filters['global'].value" placeholder="Search tenants..." />
              </span>
            </div>
          </template>
          
          <Column field="name" header="Tenant Name" sortable>
            <template #body="slotProps">
              <div class="flex align-items-center gap-2">
                <Avatar :label="slotProps.data.name.charAt(0)" shape="circle" />
                <span>{{ slotProps.data.name }}</span>
              </div>
            </template>
          </Column>
          <Column field="domain" header="Domain" sortable />
          <Column field="plan" header="Plan" sortable>
            <template #body="slotProps">
              <Tag :value="slotProps.data.plan" :severity="getPlanSeverity(slotProps.data.plan)" />
            </template>
          </Column>
          <Column field="users" header="Users" sortable />
          <Column field="storage" header="Storage Used" sortable>
            <template #body="slotProps">
              {{ slotProps.data.storage }}GB
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="slotProps">
              <Tag :value="slotProps.data.status" :severity="getStatusSeverity(slotProps.data.status)" />
            </template>
          </Column>
          <Column field="created" header="Created" sortable />
          <Column header="Actions">
            <template #body="slotProps">
              <div class="flex gap-2">
                <Button icon="pi pi-eye" size="small" @click="viewTenant(slotProps.data)" />
                <Button icon="pi pi-pencil" size="small" severity="secondary" @click="editTenant(slotProps.data)" />
                <Button icon="pi pi-ban" size="small" severity="warning" @click="suspendTenant(slotProps.data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="showAddDialog" modal header="Add New Tenant" :style="{ width: '50rem' }">
      <div class="grid">
        <div class="col-12">
          <label>Tenant Name</label>
          <InputText v-model="newTenant.name" class="w-full" />
        </div>
        <div class="col-12">
          <label>Domain</label>
          <InputText v-model="newTenant.domain" class="w-full" />
        </div>
        <div class="col-6">
          <label>Plan</label>
          <Dropdown v-model="newTenant.plan" :options="plans" class="w-full" />
        </div>
        <div class="col-6">
          <label>Admin Email</label>
          <InputText v-model="newTenant.adminEmail" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showAddDialog = false" />
        <Button label="Create Tenant" @click="createTenant" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { FilterMatchMode } from 'primevue/api'

const showAddDialog = ref(false)

const tenants = ref([
  {
    id: 1,
    name: 'Acme Corporation',
    domain: 'acme.paksa.com',
    plan: 'Enterprise',
    users: 150,
    storage: 45.2,
    status: 'Active',
    created: '2024-01-15',
    revenue: 2500
  },
  {
    id: 2,
    name: 'Tech Solutions Inc',
    domain: 'techsol.paksa.com',
    plan: 'Professional',
    users: 75,
    storage: 22.8,
    status: 'Active',
    created: '2024-02-01',
    revenue: 1200
  },
  {
    id: 3,
    name: 'StartUp Co',
    domain: 'startup.paksa.com',
    plan: 'Basic',
    users: 25,
    storage: 8.5,
    status: 'Suspended',
    created: '2024-03-10',
    revenue: 0
  }
])

const newTenant = ref({
  name: '',
  domain: '',
  plan: 'Basic',
  adminEmail: ''
})

const plans = ['Basic', 'Professional', 'Enterprise']

const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS }
})

const activeTenants = computed(() => 
  tenants.value.filter(t => t.status === 'Active').length
)

const suspendedTenants = computed(() => 
  tenants.value.filter(t => t.status === 'Suspended').length
)

const totalRevenue = computed(() => 
  tenants.value.reduce((sum, t) => sum + t.revenue, 0)
)

const getPlanSeverity = (plan: string) => {
  switch (plan) {
    case 'Enterprise': return 'success'
    case 'Professional': return 'info'
    case 'Basic': return 'warning'
    default: return 'secondary'
  }
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'Active': return 'success'
    case 'Suspended': return 'danger'
    case 'Pending': return 'warning'
    default: return 'secondary'
  }
}

const viewTenant = (tenant: any) => {
  console.log('View tenant:', tenant)
}

const editTenant = (tenant: any) => {
  console.log('Edit tenant:', tenant)
}

const suspendTenant = (tenant: any) => {
  console.log('Suspend tenant:', tenant)
}

const createTenant = () => {
  console.log('Create tenant:', newTenant.value)
  showAddDialog.value = false
  newTenant.value = { name: '', domain: '', plan: 'Basic', adminEmail: '' }
}
</script>

<style scoped>
.tenant-management {
  padding: 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
</style>