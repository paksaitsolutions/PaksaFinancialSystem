<template>
  <Card>
    <template #header>
      <div class="flex justify-content-between align-items-center p-4">
        <h3 class="m-0">Tenant Management</h3>
        <Button label="Add Tenant" icon="pi pi-plus" @click="showAddTenant = true" />
      </div>
    </template>
    <template #content>
      <DataTable :value="tenants" responsiveLayout="scroll">
        <Column field="name" header="Tenant Name"></Column>
        <Column field="domain" header="Domain"></Column>
        <Column field="plan" header="Plan">
          <template #body="{ data }">
            <Tag :value="data.plan" :severity="getPlanSeverity(data.plan)" />
          </template>
        </Column>
        <Column field="users" header="Users"></Column>
        <Column field="status" header="Status">
          <template #body="{ data }">
            <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
          </template>
        </Column>
        <Column field="createdAt" header="Created">
          <template #body="{ data }">
            {{ formatDate(data.createdAt) }}
          </template>
        </Column>
        <Column header="Actions">
          <template #body="{ data }">
            <Button icon="pi pi-eye" class="p-button-text p-button-sm mr-2" />
            <Button icon="pi pi-pencil" class="p-button-text p-button-sm mr-2" />
            <Button icon="pi pi-trash" class="p-button-text p-button-sm p-button-danger" />
          </template>
        </Column>
      </DataTable>
    </template>
  </Card>

  <Dialog v-model:visible="showAddTenant" header="Add Tenant" :style="{ width: '600px' }" :modal="true">
    <div class="grid">
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="tenantName">Tenant Name</label>
          <InputText id="tenantName" v-model="newTenant.name" class="w-full" />
        </div>
      </div>
      
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="tenantDomain">Domain</label>
          <InputText id="tenantDomain" v-model="newTenant.domain" class="w-full" />
        </div>
      </div>
      
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="tenantPlan">Plan</label>
          <Dropdown 
            id="tenantPlan" 
            v-model="newTenant.plan" 
            :options="plans" 
            optionLabel="label" 
            optionValue="value"
            class="w-full" 
          />
        </div>
      </div>
      
      <div class="col-12 md:col-6">
        <div class="field">
          <label for="maxUsers">Max Users</label>
          <InputNumber id="maxUsers" v-model="newTenant.maxUsers" class="w-full" />
        </div>
      </div>
      
      <div class="col-12">
        <div class="field">
          <label for="tenantDescription">Description</label>
          <Textarea id="tenantDescription" v-model="newTenant.description" rows="3" class="w-full" />
        </div>
      </div>
    </div>
    
    <template #footer>
      <Button label="Cancel" @click="showAddTenant = false" class="p-button-text" />
      <Button label="Create Tenant" @click="addTenant" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showAddTenant = ref(false)

const tenants = ref([
  { 
    id: 1, 
    name: 'Acme Corp', 
    domain: 'acme.paksa.com', 
    plan: 'Enterprise', 
    users: 25, 
    status: 'Active',
    createdAt: '2024-01-15'
  },
  { 
    id: 2, 
    name: 'Tech Solutions', 
    domain: 'techsol.paksa.com', 
    plan: 'Professional', 
    users: 10, 
    status: 'Active',
    createdAt: '2024-01-20'
  },
  { 
    id: 3, 
    name: 'StartupXYZ', 
    domain: 'startup.paksa.com', 
    plan: 'Basic', 
    users: 5, 
    status: 'Trial',
    createdAt: '2024-02-01'
  }
])

const newTenant = ref({
  name: '',
  domain: '',
  plan: '',
  maxUsers: 10,
  description: ''
})

const plans = [
  { label: 'Basic', value: 'Basic' },
  { label: 'Professional', value: 'Professional' },
  { label: 'Enterprise', value: 'Enterprise' }
]

const getPlanSeverity = (plan: string) => {
  switch (plan) {
    case 'Enterprise': return 'success'
    case 'Professional': return 'warning'
    case 'Basic': return 'info'
    default: return 'secondary'
  }
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'Active': return 'success'
    case 'Trial': return 'warning'
    case 'Suspended': return 'danger'
    default: return 'secondary'
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const addTenant = () => {
  tenants.value.push({
    id: tenants.value.length + 1,
    ...newTenant.value,
    users: 0,
    status: 'Active',
    createdAt: new Date().toISOString().split('T')[0]
  })
  newTenant.value = { name: '', domain: '', plan: '', maxUsers: 10, description: '' }
  showAddTenant.value = false
}
</script>