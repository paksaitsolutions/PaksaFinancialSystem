<template>
  <div class="integration-settings">
    <div class="dashboard-header">
      <h1>Integration Settings</h1>
      <p>Configure third-party integrations and API connections</p>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Active Integrations</span>
            <Button label="Add Integration" icon="pi pi-plus" @click="showAddIntegration = true" />
          </div>
        </template>
        <template #content>
          <DataTable :value="integrations" responsiveLayout="scroll">
            <Column field="name" header="Integration" />
            <Column field="type" header="Type" />
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column field="lastSync" header="Last Sync">
              <template #body="{ data }">
                {{ formatDateTime(data.lastSync) }}
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button icon="pi pi-cog" class="p-button-rounded p-button-text" @click="configureIntegration(data)" />
                  <Button icon="pi pi-refresh" class="p-button-rounded p-button-text" @click="syncIntegration(data)" />
                  <Button icon="pi pi-times" class="p-button-rounded p-button-text p-button-danger" @click="disconnectIntegration(data)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>API Settings</template>
        <template #content>
          <div class="grid p-fluid">
            <div class="col-12">
              <div class="field">
                <label>API Base URL</label>
                <InputText v-model="apiSettings.baseUrl" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Rate Limit (requests/minute)</label>
                <InputNumber v-model="apiSettings.rateLimit" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Timeout (seconds)</label>
                <InputNumber v-model="apiSettings.timeout" />
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="apiSettings.enableLogging" binary />
                  <span class="ml-2">Enable API request logging</span>
                </label>
              </div>
            </div>
          </div>
        </template>
        <template #footer>
          <Button label="Save API Settings" icon="pi pi-check" @click="saveApiSettings" />
        </template>
      </Card>
    </div>

    <Dialog v-model:visible="showAddIntegration" modal header="Add Integration" :style="{ width: '500px' }">
      <div class="grid p-fluid">
        <div class="col-12">
          <div class="field">
            <label>Integration Type</label>
            <Dropdown v-model="newIntegration.type" :options="integrationTypes" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Name</label>
            <InputText v-model="newIntegration.name" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>API Key</label>
            <Password v-model="newIntegration.apiKey" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Endpoint URL</label>
            <InputText v-model="newIntegration.endpoint" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showAddIntegration = false" />
        <Button label="Add" @click="addIntegration" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showAddIntegration = ref(false)

const integrations = ref([
  { id: 1, name: 'QuickBooks Online', type: 'Accounting', status: 'Connected', lastSync: '2023-11-15T14:30:00' },
  { id: 2, name: 'Stripe', type: 'Payment', status: 'Connected', lastSync: '2023-11-15T14:25:00' },
  { id: 3, name: 'Salesforce', type: 'CRM', status: 'Disconnected', lastSync: '2023-11-10T09:15:00' }
])

const apiSettings = ref({
  baseUrl: 'https://api.paksa.com/v1',
  rateLimit: 1000,
  timeout: 30,
  enableLogging: true
})

const newIntegration = ref({
  name: '',
  type: '',
  apiKey: '',
  endpoint: ''
})

const integrationTypes = ref(['Accounting', 'Payment', 'CRM', 'Banking', 'E-commerce', 'Payroll'])

const formatDateTime = (dateString: string) => new Date(dateString).toLocaleString()

const getStatusSeverity = (status: string) => {
  return status === 'Connected' ? 'success' : 'danger'
}

const addIntegration = () => {
  integrations.value.push({
    id: Date.now(),
    ...newIntegration.value,
    status: 'Connected',
    lastSync: new Date().toISOString()
  })
  newIntegration.value = { name: '', type: '', apiKey: '', endpoint: '' }
  showAddIntegration.value = false
}

const configureIntegration = (integration: any) => {
  console.log('Configuring integration:', integration)
}

const syncIntegration = (integration: any) => {
  console.log('Syncing integration:', integration)
}

const disconnectIntegration = (integration: any) => {
  console.log('Disconnecting integration:', integration)
}

const saveApiSettings = () => {
  console.log('Saving API settings:', apiSettings.value)
}
</script>

<style scoped>
.integration-settings {
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

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}

@media (max-width: 768px) {
  .integration-settings {
    padding: 1rem;
  }
}
</style>