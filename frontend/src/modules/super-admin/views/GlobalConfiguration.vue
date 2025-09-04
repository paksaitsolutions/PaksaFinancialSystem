<template>
  <div class="global-config">
    <div class="dashboard-header">
      <h1>Global Configuration</h1>
      <p>System-wide configuration and platform settings</p>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>Platform Settings</template>
        <template #content>
          <div class="grid p-fluid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Platform Name</label>
                <InputText v-model="globalConfig.platformName" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Platform Version</label>
                <InputText v-model="globalConfig.platformVersion" readonly />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Default Language</label>
                <Dropdown v-model="globalConfig.defaultLanguage" :options="languages" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Default Currency</label>
                <Dropdown v-model="globalConfig.defaultCurrency" :options="currencies" />
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="globalConfig.maintenanceMode" binary />
                  <span class="ml-2">Enable maintenance mode</span>
                </label>
              </div>
            </div>
          </div>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>Security Settings</template>
        <template #content>
          <div class="grid p-fluid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Session Timeout (minutes)</label>
                <InputNumber v-model="globalConfig.sessionTimeout" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Max Login Attempts</label>
                <InputNumber v-model="globalConfig.maxLoginAttempts" />
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="globalConfig.enforceSSL" binary />
                  <span class="ml-2">Enforce SSL/HTTPS</span>
                </label>
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="globalConfig.enableTwoFactor" binary />
                  <span class="ml-2">Require two-factor authentication</span>
                </label>
              </div>
            </div>
          </div>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>Email Configuration</template>
        <template #content>
          <div class="grid p-fluid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>SMTP Server</label>
                <InputText v-model="globalConfig.smtpServer" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>SMTP Port</label>
                <InputNumber v-model="globalConfig.smtpPort" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>From Email</label>
                <InputText v-model="globalConfig.fromEmail" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>From Name</label>
                <InputText v-model="globalConfig.fromName" />
              </div>
            </div>
          </div>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Feature Flags</span>
            <Button label="Add Flag" icon="pi pi-plus" @click="showAddFlag = true" />
          </div>
        </template>
        <template #content>
          <DataTable :value="featureFlags" responsiveLayout="scroll">
            <Column field="name" header="Feature" />
            <Column field="description" header="Description" />
            <Column field="enabled" header="Status">
              <template #body="{ data }">
                <InputSwitch v-model="data.enabled" @change="updateFeatureFlag(data)" />
              </template>
            </Column>
            <Column header="Actions">
              <template #body="{ data }">
                <Button icon="pi pi-trash" class="p-button-rounded p-button-text p-button-danger" @click="deleteFlag(data)" />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>

    <div class="actions-footer">
      <Button label="Reset to Defaults" severity="secondary" @click="resetDefaults" />
      <Button label="Save Configuration" icon="pi pi-check" @click="saveConfiguration" />
    </div>

    <Dialog v-model:visible="showAddFlag" modal header="Add Feature Flag" :style="{ width: '500px' }">
      <div class="grid p-fluid">
        <div class="col-12">
          <div class="field">
            <label>Feature Name</label>
            <InputText v-model="newFlag.name" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Description</label>
            <Textarea v-model="newFlag.description" rows="3" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label class="flex align-items-center">
              <Checkbox v-model="newFlag.enabled" binary />
              <span class="ml-2">Enable by default</span>
            </label>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showAddFlag = false" />
        <Button label="Add" @click="addFlag" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showAddFlag = ref(false)

const globalConfig = ref({
  platformName: 'Paksa Financial System',
  platformVersion: '1.0.0',
  defaultLanguage: 'English',
  defaultCurrency: 'USD',
  maintenanceMode: false,
  sessionTimeout: 30,
  maxLoginAttempts: 5,
  enforceSSL: true,
  enableTwoFactor: false,
  smtpServer: 'smtp.gmail.com',
  smtpPort: 587,
  fromEmail: 'noreply@paksa.com',
  fromName: 'Paksa Financial System'
})

const featureFlags = ref([
  { id: 1, name: 'Advanced Analytics', description: 'Enable advanced analytics dashboard', enabled: true },
  { id: 2, name: 'Multi-Currency', description: 'Support for multiple currencies', enabled: true },
  { id: 3, name: 'API Access', description: 'Enable REST API access', enabled: false },
  { id: 4, name: 'Mobile App', description: 'Mobile application support', enabled: false }
])

const newFlag = ref({
  name: '',
  description: '',
  enabled: false
})

const languages = ref(['English', 'Spanish', 'French', 'German', 'Chinese'])
const currencies = ref(['USD', 'EUR', 'GBP', 'CAD', 'AUD'])

const addFlag = () => {
  featureFlags.value.push({
    id: Date.now(),
    ...newFlag.value
  })
  newFlag.value = { name: '', description: '', enabled: false }
  showAddFlag.value = false
}

const updateFeatureFlag = (flag: any) => {
  console.log('Updating feature flag:', flag.name, flag.enabled)
}

const deleteFlag = (flag: any) => {
  const index = featureFlags.value.findIndex(f => f.id === flag.id)
  if (index > -1) {
    featureFlags.value.splice(index, 1)
  }
}

const saveConfiguration = () => {
  console.log('Saving global configuration:', globalConfig.value)
}

const resetDefaults = () => {
  globalConfig.value = {
    platformName: 'Paksa Financial System',
    platformVersion: '1.0.0',
    defaultLanguage: 'English',
    defaultCurrency: 'USD',
    maintenanceMode: false,
    sessionTimeout: 30,
    maxLoginAttempts: 5,
    enforceSSL: true,
    enableTwoFactor: false,
    smtpServer: 'smtp.gmail.com',
    smtpPort: 587,
    fromEmail: 'noreply@paksa.com',
    fromName: 'Paksa Financial System'
  }
}
</script>

<style scoped>
.global-config {
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
  margin-bottom: 2rem;
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

.actions-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

@media (max-width: 768px) {
  .global-config {
    padding: 1rem;
  }
  
  .actions-footer {
    flex-direction: column;
  }
}
</style>