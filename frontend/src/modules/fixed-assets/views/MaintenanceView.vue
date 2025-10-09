<template>
  <div class="maintenance-view">
    <Card>
      <template #title>
        <div class="header-content">
          <div class="header-text">
            <h2 class="m-0">Asset Maintenance</h2>
            <p class="text-600 mt-1 mb-0">Schedule and track asset maintenance activities</p>
          </div>
          <div class="header-actions">
            <Button icon="pi pi-calendar" label="Upcoming" severity="info" @click="showUpcoming" />
            <Button icon="pi pi-plus" label="Schedule Maintenance" @click="showCreateDialog = true" />
          </div>
        </div>
      </template>
      
      <template #content>
        <!-- Filters -->
        <div class="grid mb-4">
          <div class="col-12 md:col-4">
            <div class="field">
              <label>Filter by Asset</label>
              <Dropdown 
                v-model="selectedAssetId" 
                :options="assets" 
                optionLabel="asset_name" 
                optionValue="id" 
                placeholder="All assets" 
                class="w-full"
                showClear
                @change="loadMaintenanceRecords"
              />
            </div>
          </div>
          <div class="col-12 md:col-4">
            <div class="field">
              <label>Status Filter</label>
              <Dropdown 
                v-model="statusFilter" 
                :options="statusOptions" 
                optionLabel="label" 
                optionValue="value" 
                placeholder="All statuses" 
                class="w-full"
                showClear
                @change="loadMaintenanceRecords"
              />
            </div>
          </div>
          <div class="col-12 md:col-4">
            <div class="field">
              <label>&nbsp;</label>
              <div class="flex gap-2">
                <Button icon="pi pi-refresh" @click="loadMaintenanceRecords" />
                <Button icon="pi pi-filter-slash" severity="secondary" outlined @click="clearFilters" />
              </div>
            </div>
          </div>
        </div>

        <!-- Maintenance Records -->
        <DataTable :value="maintenanceRecords" :loading="loading" paginator :rows="10">
          <template #empty>
            <div class="text-center p-4">
              <i class="pi pi-wrench text-4xl text-400 mb-3"></i>
              <p class="text-600">No maintenance records found</p>
            </div>
          </template>
          
          <Column field="asset_name" header="Asset" sortable />
          <Column field="maintenance_type" header="Type" sortable />
          <Column field="maintenance_date" header="Scheduled Date" sortable>
            <template #body="{ data }">
              {{ formatDate(data.maintenance_date) }}
            </template>
          </Column>
          <Column field="description" header="Description" />
          <Column field="cost" header="Cost">
            <template #body="{ data }">
              {{ data.cost ? formatCurrency(data.cost) : '-' }}
            </template>
          </Column>
          <Column field="vendor" header="Vendor" />
          <Column field="next_maintenance_date" header="Next Due">
            <template #body="{ data }">
              {{ data.next_maintenance_date ? formatDate(data.next_maintenance_date) : '-' }}
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" size="small" text @click="editMaintenance(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Create/Edit Maintenance Dialog -->
    <Dialog v-model:visible="showCreateDialog" modal :header="isEditing ? 'Edit Maintenance' : 'Schedule Maintenance'" :style="{ width: '600px' }">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Asset *</label>
            <Dropdown 
              v-model="maintenanceForm.asset_id" 
              :options="assets" 
              optionLabel="asset_name" 
              optionValue="id" 
              placeholder="Select asset" 
              class="w-full"
              :class="{ 'p-invalid': submitted && !maintenanceForm.asset_id }"
            />
            <small class="p-error" v-if="submitted && !maintenanceForm.asset_id">Asset is required</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Maintenance Type</label>
            <Dropdown 
              v-model="maintenanceForm.maintenance_type" 
              :options="maintenanceTypes" 
              optionLabel="label" 
              optionValue="value" 
              placeholder="Select type" 
              class="w-full"
              editable
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Scheduled Date *</label>
            <InputText v-model="maintenanceForm.maintenance_date" type="date" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Next Maintenance Date</label>
            <InputText v-model="maintenanceForm.next_maintenance_date" type="date" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Description</label>
            <Textarea v-model="maintenanceForm.description" rows="3" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Estimated Cost</label>
            <InputNumber 
              v-model="maintenanceForm.cost" 
              mode="currency" 
              currency="USD" 
              class="w-full" 
              :min="0"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Vendor</label>
            <InputText v-model="maintenanceForm.vendor" class="w-full" />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="hideDialog" />
        <Button :label="isEditing ? 'Update' : 'Schedule'" @click="saveMaintenance" :loading="saving" />
      </template>
    </Dialog>

    <!-- Upcoming Maintenance Dialog -->
    <Dialog v-model:visible="showUpcomingDialog" modal header="Upcoming Maintenance" :style="{ width: '800px' }">
      <DataTable :value="upcomingMaintenance" :loading="loadingUpcoming">
        <template #empty>
          <div class="text-center p-4">
            <i class="pi pi-check-circle text-4xl text-green-500 mb-3"></i>
            <p class="text-600">No upcoming maintenance in the next 30 days</p>
          </div>
        </template>
        
        <Column field="asset_name" header="Asset" />
        <Column field="maintenance_type" header="Type" />
        <Column field="maintenance_date" header="Due Date">
          <template #body="{ data }">
            <span :class="{ 'text-red-500 font-semibold': isOverdue(data.maintenance_date) }">
              {{ formatDate(data.maintenance_date) }}
            </span>
          </template>
        </Column>
        <Column field="description" header="Description" />
        <Column field="cost" header="Est. Cost">
          <template #body="{ data }">
            {{ data.cost ? formatCurrency(data.cost) : '-' }}
          </template>
        </Column>
      </DataTable>
      
      <template #footer>
        <Button label="Close" @click="showUpcomingDialog = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { fixedAssetsService, type FixedAsset, type AssetMaintenance } from '@/services/fixedAssetsService'
import { formatCurrency } from '@/utils/formatters'

const toast = useToast()
const loading = ref(false)
const loadingUpcoming = ref(false)
const saving = ref(false)
const submitted = ref(false)
const showCreateDialog = ref(false)
const showUpcomingDialog = ref(false)
const isEditing = ref(false)
const selectedAssetId = ref<string>('')
const statusFilter = ref<string>('')

const assets = ref<FixedAsset[]>([])
const maintenanceRecords = ref<AssetMaintenance[]>([])
const upcomingMaintenance = ref<AssetMaintenance[]>([])

const maintenanceForm = reactive({
  id: '',
  asset_id: '',
  maintenance_date: new Date().toISOString().split('T')[0],
  maintenance_type: '',
  description: '',
  cost: 0,
  vendor: '',
  next_maintenance_date: ''
})

const statusOptions = [
  { label: 'Scheduled', value: 'scheduled' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' }
]

const maintenanceTypes = [
  { label: 'Preventive', value: 'preventive' },
  { label: 'Corrective', value: 'corrective' },
  { label: 'Emergency', value: 'emergency' },
  { label: 'Inspection', value: 'inspection' },
  { label: 'Calibration', value: 'calibration' }
]

const loadAssets = async () => {
  try {
    assets.value = await fixedAssetsService.getAssets()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load assets' })
  }
}

const loadMaintenanceRecords = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (selectedAssetId.value) params.asset_id = selectedAssetId.value
    
    maintenanceRecords.value = await fixedAssetsService.getMaintenanceRecords(params)
    
    // Add asset names to records
    maintenanceRecords.value = maintenanceRecords.value.map(record => ({
      ...record,
      asset_name: assets.value.find(asset => asset.id === record.asset_id)?.asset_name || 'Unknown Asset'
    }))
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load maintenance records' })
  } finally {
    loading.value = false
  }
}

const showUpcoming = async () => {
  loadingUpcoming.value = true
  showUpcomingDialog.value = true
  
  try {
    upcomingMaintenance.value = await fixedAssetsService.getMaintenanceRecords({ upcoming_days: 30 })
    
    // Add asset names to records
    upcomingMaintenance.value = upcomingMaintenance.value.map(record => ({
      ...record,
      asset_name: assets.value.find(asset => asset.id === record.asset_id)?.asset_name || 'Unknown Asset'
    }))
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load upcoming maintenance' })
  } finally {
    loadingUpcoming.value = false
  }
}

const editMaintenance = (maintenance: AssetMaintenance) => {
  isEditing.value = true
  Object.assign(maintenanceForm, maintenance)
  showCreateDialog.value = true
}

const hideDialog = () => {
  showCreateDialog.value = false
  isEditing.value = false
  submitted.value = false
  
  // Reset form
  Object.assign(maintenanceForm, {
    id: '',
    asset_id: '',
    maintenance_date: new Date().toISOString().split('T')[0],
    maintenance_type: '',
    description: '',
    cost: 0,
    vendor: '',
    next_maintenance_date: ''
  })
}

const saveMaintenance = async () => {
  submitted.value = true
  
  if (!maintenanceForm.asset_id) {
    return
  }

  saving.value = true
  try {
    if (isEditing.value && maintenanceForm.id) {
      await fixedAssetsService.updateMaintenanceRecord(maintenanceForm.id, maintenanceForm)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Maintenance record updated successfully' })
    } else {
      await fixedAssetsService.createMaintenanceRecord(maintenanceForm)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Maintenance scheduled successfully' })
    }
    
    hideDialog()
    await loadMaintenanceRecords()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save maintenance record' })
  } finally {
    saving.value = false
  }
}

const clearFilters = () => {
  selectedAssetId.value = ''
  statusFilter.value = ''
  loadMaintenanceRecords()
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const isOverdue = (dateString: string) => {
  return new Date(dateString) < new Date()
}

onMounted(async () => {
  await loadAssets()
  await loadMaintenanceRecords()
})
</script>

<style scoped>
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

@media screen and (max-width: 960px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>