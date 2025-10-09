<template>
  <div class="locations-view">
    <Card>
      <template #title>
        <div class="header-content">
          <div class="header-text">
            <h2 class="m-0">Inventory Locations</h2>
            <p class="text-600 mt-1 mb-0">Manage warehouse and storage locations</p>
          </div>
          <div class="header-actions">
            <Button icon="pi pi-plus" label="Add Location" @click="showCreateDialog = true" />
          </div>
        </div>
      </template>
      
      <template #content>
        <DataTable :value="locations" :loading="loading" paginator :rows="10">
          <Column field="location_code" header="Code" sortable />
          <Column field="location_name" header="Name" sortable />
          <Column field="location_type" header="Type" sortable />
          <Column field="address" header="Address" />
          <Column header="Status">
            <template #body="{ data }">
              <Tag :value="data.is_active ? 'Active' : 'Inactive'" :severity="data.is_active ? 'success' : 'danger'" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" size="small" text @click="editLocation(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="showCreateDialog" modal header="Add Location" :style="{ width: '500px' }">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label>Location Code *</label>
            <InputText v-model="newLocation.location_code" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Location Name *</label>
            <InputText v-model="newLocation.location_name" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Type</label>
            <Dropdown v-model="newLocation.location_type" :options="locationTypes" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Address</label>
            <Textarea v-model="newLocation.address" rows="3" class="w-full" />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showCreateDialog = false" />
        <Button label="Save" @click="saveLocation" :loading="saving" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { inventoryService, type InventoryLocation } from '@/services/inventoryService'

const toast = useToast()
const loading = ref(false)
const saving = ref(false)
const showCreateDialog = ref(false)
const locations = ref<InventoryLocation[]>([])

const newLocation = reactive({
  location_code: '',
  location_name: '',
  location_type: '',
  address: ''
})

const locationTypes = [
  { label: 'Warehouse', value: 'warehouse' },
  { label: 'Store', value: 'store' },
  { label: 'Depot', value: 'depot' }
]

const loadLocations = async () => {
  loading.value = true
  try {
    locations.value = await inventoryService.getLocations()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load locations' })
  } finally {
    loading.value = false
  }
}

const saveLocation = async () => {
  saving.value = true
  try {
    await inventoryService.createLocation(newLocation)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Location created successfully' })
    showCreateDialog.value = false
    Object.assign(newLocation, { location_code: '', location_name: '', location_type: '', address: '' })
    loadLocations()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create location' })
  } finally {
    saving.value = false
  }
}

const editLocation = (location: InventoryLocation) => {
  // Implementation for editing
  console.log('Edit location:', location)
}

onMounted(() => {
  loadLocations()
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
}

@media screen and (max-width: 960px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>