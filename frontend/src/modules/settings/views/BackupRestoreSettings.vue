<template>
  <div class="backup-restore">
    <div class="dashboard-header">
      <h1>Backup & Restore</h1>
      <p>Manage system backups and data restoration</p>
    </div>

    <div class="summary-cards">
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-cloud-upload text-blue"></i>
            <span>Last Backup</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-blue">{{ formatDateTime(lastBackup) }}</div>
          <div class="summary-date">Automatic backup</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-database text-green"></i>
            <span>Backup Size</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-green">{{ backupSize }}</div>
          <div class="summary-date">Total storage used</div>
        </template>
      </Card>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Backup History</span>
            <Button label="Create Backup" icon="pi pi-plus" @click="createBackup" />
          </div>
        </template>
        <template #content>
          <DataTable :value="backupHistory" responsiveLayout="scroll">
            <Column field="name" header="Backup Name" />
            <Column field="type" header="Type" />
            <Column field="size" header="Size" />
            <Column field="createdAt" header="Created">
              <template #body="{ data }">
                {{ formatDateTime(data.createdAt) }}
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
                  <Button icon="pi pi-download" class="p-button-rounded p-button-text" @click="downloadBackup(data)" />
                  <Button icon="pi pi-refresh" class="p-button-rounded p-button-text" @click="restoreBackup(data)" />
                  <Button icon="pi pi-trash" class="p-button-rounded p-button-text p-button-danger" @click="deleteBackup(data)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>Backup Settings</template>
        <template #content>
          <div class="grid p-fluid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Backup Frequency</label>
                <Dropdown v-model="backupSettings.frequency" :options="frequencies" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Retention Period (days)</label>
                <InputNumber v-model="backupSettings.retentionDays" />
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label>Backup Location</label>
                <Dropdown v-model="backupSettings.location" :options="locations" />
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="backupSettings.autoBackup" binary />
                  <span class="ml-2">Enable automatic backups</span>
                </label>
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="backupSettings.compression" binary />
                  <span class="ml-2">Enable backup compression</span>
                </label>
              </div>
            </div>
          </div>
        </template>
        <template #footer>
          <Button label="Save Settings" icon="pi pi-check" @click="saveSettings" />
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const lastBackup = ref('2023-11-15T02:00:00')
const backupSize = ref('2.4 GB')

const backupHistory = ref([
  { id: 1, name: 'Daily_Backup_2023-11-15', type: 'Automatic', size: '2.4 GB', createdAt: '2023-11-15T02:00:00', status: 'Completed' },
  { id: 2, name: 'Manual_Backup_2023-11-14', type: 'Manual', size: '2.3 GB', createdAt: '2023-11-14T15:30:00', status: 'Completed' },
  { id: 3, name: 'Daily_Backup_2023-11-14', type: 'Automatic', size: '2.3 GB', createdAt: '2023-11-14T02:00:00', status: 'Completed' }
])

const backupSettings = ref({
  frequency: 'Daily',
  retentionDays: 30,
  location: 'Cloud Storage',
  autoBackup: true,
  compression: true
})

const frequencies = ref(['Hourly', 'Daily', 'Weekly', 'Monthly'])
const locations = ref(['Local Storage', 'Cloud Storage', 'Network Drive'])

const formatDateTime = (dateString: string) => new Date(dateString).toLocaleString()

const getStatusSeverity = (status: string) => {
  const severities = {
    Completed: 'success',
    'In Progress': 'warning',
    Failed: 'danger'
  }
  return severities[status] || 'info'
}

const createBackup = () => {
  console.log('Creating manual backup')
}

const downloadBackup = (backup: any) => {
  console.log('Downloading backup:', backup.name)
}

const restoreBackup = (backup: any) => {
  console.log('Restoring backup:', backup.name)
}

const deleteBackup = (backup: any) => {
  console.log('Deleting backup:', backup.name)
}

const saveSettings = () => {
  console.log('Saving backup settings:', backupSettings.value)
}
</script>

<style scoped>
.backup-restore {
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
.text-green { color: #10b981; }

@media (max-width: 768px) {
  .backup-restore {
    padding: 1rem;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>