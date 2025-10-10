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
        <DataTable :value="tenants" :loading="loading" paginator :rows="10" dataKey="id" 
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
                <Button icon="pi pi-eye" size="small" @click="viewTenant(slotProps.data)" v-tooltip.top="'View Details'" />
                <Button icon="pi pi-pencil" size="small" severity="secondary" @click="editTenant(slotProps.data)" v-tooltip.top="'Edit Company'" />
                <Button :icon="slotProps.data.status === 'Active' ? 'pi pi-ban' : 'pi pi-check'" size="small" :severity="slotProps.data.status === 'Active' ? 'warning' : 'success'" @click="suspendTenant(slotProps.data)" :v-tooltip.top="slotProps.data.status === 'Active' ? 'Suspend' : 'Activate'" />
                <Button icon="pi pi-trash" size="small" severity="danger" @click="deleteTenant(slotProps.data)" v-tooltip.top="'Delete Company'" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="showAddDialog" modal header="Add New Company" :style="{ width: '50rem' }">
      <div class="grid">
        <div class="col-12 md:col-6">
          <label>Company Name</label>
          <InputText v-model="newTenant.name" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Company Code</label>
          <InputText v-model="newTenant.code" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Subdomain</label>
          <InputText v-model="newTenant.subdomain" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Plan</label>
          <Dropdown v-model="newTenant.plan" :options="plans" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Admin Name</label>
          <InputText v-model="newTenant.admin_name" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Admin Email</label>
          <InputText v-model="newTenant.admin_email" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Admin Password</label>
          <Password v-model="newTenant.admin_password" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Currency</label>
          <Dropdown v-model="newTenant.currency" :options="['USD', 'EUR', 'GBP', 'PKR']" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showAddDialog = false" />
        <Button label="Create Company" @click="createTenant" :loading="saving" />
      </template>
    </Dialog>

    <Dialog v-model:visible="showEditDialog" modal header="Edit Company" :style="{ width: '50rem' }">
      <div class="grid" v-if="editedTenant">
        <div class="col-12 md:col-6">
          <label>Company Name</label>
          <InputText v-model="editedTenant.name" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Plan</label>
          <Dropdown v-model="editedTenant.plan" :options="plans" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Max Users</label>
          <InputNumber v-model="editedTenant.max_users" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Storage Limit (GB)</label>
          <InputNumber v-model="editedTenant.storage_limit_gb" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Currency</label>
          <Dropdown v-model="editedTenant.currency" :options="['USD', 'EUR', 'GBP', 'PKR']" class="w-full" />
        </div>
        <div class="col-12 md:col-6">
          <label>Timezone</label>
          <InputText v-model="editedTenant.timezone" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showEditDialog = false" />
        <Button label="Update Company" @click="updateTenant" :loading="saving" />
      </template>
    </Dialog>

    <Dialog v-model:visible="showViewDialog" modal header="Company Details" :style="{ width: '50rem' }">
      <div class="grid" v-if="selectedTenant">
        <div class="col-12 md:col-6">
          <strong>Company Name:</strong>
          <p>{{ selectedTenant.name }}</p>
        </div>
        <div class="col-12 md:col-6">
          <strong>Code:</strong>
          <p>{{ selectedTenant.code }}</p>
        </div>
        <div class="col-12 md:col-6">
          <strong>Domain:</strong>
          <p>{{ selectedTenant.domain || selectedTenant.subdomain + '.paksa.com' }}</p>
        </div>
        <div class="col-12 md:col-6">
          <strong>Plan:</strong>
          <Tag :value="selectedTenant.plan" :severity="getPlanSeverity(selectedTenant.plan)" />
        </div>
        <div class="col-12 md:col-6">
          <strong>Status:</strong>
          <Tag :value="selectedTenant.status" :severity="getStatusSeverity(selectedTenant.status)" />
        </div>
        <div class="col-12 md:col-6">
          <strong>Users:</strong>
          <p>{{ selectedTenant.current_users || 0 }} / {{ selectedTenant.max_users }}</p>
        </div>
        <div class="col-12 md:col-6">
          <strong>Storage Limit:</strong>
          <p>{{ selectedTenant.storage_limit_gb }}GB</p>
        </div>
        <div class="col-12 md:col-6">
          <strong>Currency:</strong>
          <p>{{ selectedTenant.currency }}</p>
        </div>
        <div class="col-12 md:col-6">
          <strong>Created:</strong>
          <p>{{ new Date(selectedTenant.created_at || '').toLocaleDateString() }}</p>
        </div>
        <div class="col-12 md:col-6">
          <strong>Timezone:</strong>
          <p>{{ selectedTenant.timezone }}</p>
        </div>
      </div>
      <template #footer>
        <Button label="Close" @click="showViewDialog = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { FilterMatchMode } from 'primevue/api'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import tenantService, { type TenantCompany } from '@/services/tenantService'

const toast = useToast()
const confirm = useConfirm()

const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const showViewDialog = ref(false)

const tenants = ref<TenantCompany[]>([])
const selectedTenant = ref<TenantCompany | null>(null)

const newTenant = ref({
  name: '',
  code: '',
  subdomain: '',
  plan: 'Basic',
  admin_name: '',
  admin_email: '',
  admin_password: '',
  max_users: 10,
  storage_limit_gb: 5,
  api_rate_limit: 1000,
  timezone: 'UTC',
  language: 'en',
  currency: 'USD',
  date_format: 'MM/DD/YYYY'
})

const editedTenant = ref<Partial<TenantCompany>>({})

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

const totalRevenue = computed(() => {
  // Calculate based on plan pricing
  return tenants.value.reduce((sum, t) => {
    const pricing = tenantService.getPlanPrice(t.plan)
    return sum + (t.status === 'Active' ? pricing.monthly : 0)
  }, 0)
})

const loadTenants = async () => {
  loading.value = true
  try {
    tenants.value = await tenantService.getCompanies()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load companies' })
  } finally {
    loading.value = false
  }
}

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

const viewTenant = (tenant: TenantCompany) => {
  selectedTenant.value = tenant
  showViewDialog.value = true
}

const editTenant = (tenant: TenantCompany) => {
  editedTenant.value = { ...tenant }
  showEditDialog.value = true
}

const suspendTenant = (tenant: TenantCompany) => {
  confirm.require({
    message: `Are you sure you want to ${tenant.status === 'Active' ? 'suspend' : 'activate'} "${tenant.name}"?`,
    header: 'Confirm Action',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try {
        const newStatus = tenant.status === 'Active' ? 'Suspended' : 'Active'
        await tenantService.updateCompany(tenant.id!, { status: newStatus })
        toast.add({ severity: 'success', summary: 'Success', detail: `Company ${newStatus.toLowerCase()} successfully` })
        await loadTenants()
      } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to update company status' })
      }
    }
  })
}

const deleteTenant = (tenant: TenantCompany) => {
  confirm.require({
    message: `Are you sure you want to delete "${tenant.name}"? This action cannot be undone.`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try {
        await tenantService.deleteCompany(tenant.id!)
        toast.add({ severity: 'success', summary: 'Success', detail: 'Company deleted successfully' })
        await loadTenants()
      } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete company' })
      }
    }
  })
}

const createTenant = async () => {
  saving.value = true
  try {
    // Generate code and subdomain if not provided
    if (!newTenant.value.code) {
      newTenant.value.code = tenantService.generateCompanyCode(newTenant.value.name)
    }
    if (!newTenant.value.subdomain) {
      newTenant.value.subdomain = tenantService.generateSubdomain(newTenant.value.name)
    }

    await tenantService.registerCompany(newTenant.value)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Company created successfully' })
    showAddDialog.value = false
    resetNewTenant()
    await loadTenants()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create company' })
  } finally {
    saving.value = false
  }
}

const updateTenant = async () => {
  saving.value = true
  try {
    await tenantService.updateCompany(editedTenant.value.id!, editedTenant.value)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Company updated successfully' })
    showEditDialog.value = false
    await loadTenants()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to update company' })
  } finally {
    saving.value = false
  }
}

const resetNewTenant = () => {
  newTenant.value = {
    name: '',
    code: '',
    subdomain: '',
    plan: 'Basic',
    admin_name: '',
    admin_email: '',
    admin_password: '',
    max_users: 10,
    storage_limit_gb: 5,
    api_rate_limit: 1000,
    timezone: 'UTC',
    language: 'en',
    currency: 'USD',
    date_format: 'MM/DD/YYYY'
  }
}

onMounted(() => {
  loadTenants()
})
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