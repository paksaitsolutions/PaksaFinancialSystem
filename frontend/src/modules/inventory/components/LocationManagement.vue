<template>
  <div class="location-management">
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <div>
            <h2 class="m-0">Inventory Locations</h2>
            <p class="text-600 mt-1 mb-0">Manage warehouse and storage locations</p>
          </div>
          <Button icon="pi pi-plus" label="Add Location" @click="openCreateDialog" />
        </div>
      </template>
      
      <template #content>
        <!-- Search and filters -->
        <div class="grid mb-4">
          <div class="col-12 md:col-4">
            <span class="p-input-icon-left w-full">
              <i class="pi pi-search" />
              <InputText v-model="searchQuery" placeholder="Search locations" class="w-full" @input="debouncedFetchLocations" />
            </span>
          </div>
          <div class="col-12 md:col-4">
            <Dropdown
              v-model="statusFilter"
              :options="statusOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="Filter by status"
              class="w-full"
              showClear
              @change="fetchLocations"
            />
          </div>
          <div class="col-12 md:col-4">
            <Button
              icon="pi pi-filter-slash"
              label="Clear Filters"
              severity="secondary"
              outlined
              @click="clearFilters"
            />
          </div>
        </div>
        
        <!-- Data table -->
        <DataTable
          :value="locations"
          :loading="loading"
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <Column field="code" header="Code" sortable />
          <Column field="name" header="Name" sortable />
          
          <Column field="is_active" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.is_active ? 'Active' : 'Inactive'" :severity="data.is_active ? 'success' : 'danger'" />
            </template>
          </Column>
          
          <Column field="address" header="Address">
            <template #body="{ data }">
              <div v-if="data.address_line1">
                {{ formatAddress(data) }}
              </div>
              <span v-else class="text-500">No address</span>
            </template>
          </Column>
          
          <Column field="description" header="Description" />
          
          <Column header="Actions" :exportable="false">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button icon="pi pi-eye" size="small" text @click="viewLocation(data)" v-tooltip="'View Details'" />
                <Button icon="pi pi-pencil" size="small" text severity="warning" @click="editLocation(data)" v-tooltip="'Edit Location'" />
                <Button icon="pi pi-trash" size="small" text severity="danger" @click="confirmDelete(data)" v-tooltip="'Delete Location'" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
    
    <!-- Create/Edit Dialog -->
    <Dialog v-model:visible="dialog.show" modal :header="dialog.isEdit ? 'Edit Location' : 'Add Location'" :style="{ width: '800px' }">
      <form @submit.prevent="saveLocation">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="code" class="font-semibold">Code *</label>
              <InputText
                id="code"
                v-model="dialog.formData.code"
                :class="{ 'p-invalid': errors.code }"
                placeholder="Enter location code"
                class="w-full"
              />
              <small v-if="errors.code" class="p-error">{{ errors.code }}</small>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="name" class="font-semibold">Name *</label>
              <InputText
                id="name"
                v-model="dialog.formData.name"
                :class="{ 'p-invalid': errors.name }"
                placeholder="Enter location name"
                class="w-full"
              />
              <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
            </div>
          </div>
          
          <div class="col-12">
            <div class="field">
              <label for="description" class="font-semibold">Description</label>
              <Textarea
                id="description"
                v-model="dialog.formData.description"
                placeholder="Enter description"
                rows="2"
                class="w-full"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field-checkbox">
              <Checkbox id="is_active" v-model="dialog.formData.is_active" :binary="true" />
              <label for="is_active" class="ml-2">Active</label>
            </div>
          </div>
        </div>
        
        <Divider />
        <h4 class="mb-4">Address Information</h4>
        
        <div class="grid">
          <div class="col-12">
            <div class="field">
              <label for="address_line1" class="font-semibold">Address Line 1</label>
              <InputText
                id="address_line1"
                v-model="dialog.formData.address_line1"
                placeholder="Enter address line 1"
                class="w-full"
              />
            </div>
          </div>
          
          <div class="col-12">
            <div class="field">
              <label for="address_line2" class="font-semibold">Address Line 2</label>
              <InputText
                id="address_line2"
                v-model="dialog.formData.address_line2"
                placeholder="Enter address line 2"
                class="w-full"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-4">
            <div class="field">
              <label for="city" class="font-semibold">City</label>
              <InputText
                id="city"
                v-model="dialog.formData.city"
                placeholder="Enter city"
                class="w-full"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-4">
            <div class="field">
              <label for="state" class="font-semibold">State/Province</label>
              <InputText
                id="state"
                v-model="dialog.formData.state"
                placeholder="Enter state/province"
                class="w-full"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-4">
            <div class="field">
              <label for="postal_code" class="font-semibold">Postal Code</label>
              <InputText
                id="postal_code"
                v-model="dialog.formData.postal_code"
                placeholder="Enter postal code"
                class="w-full"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="country" class="font-semibold">Country</label>
              <InputText
                id="country"
                v-model="dialog.formData.country"
                placeholder="Enter country"
                class="w-full"
              />
            </div>
          </div>
        </div>
      </form>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="dialog.show = false" />
        <Button
          :label="dialog.isEdit ? 'Update' : 'Create'"
          :loading="dialog.saving"
          @click="saveLocation"
        />
      </template>
    </Dialog>
    
    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:visible="deleteDialog.show" modal header="Delete Location" :style="{ width: '450px' }">
      <div class="flex align-items-center gap-3 mb-3">
        <i class="pi pi-exclamation-triangle text-red-500" style="font-size: 2rem"></i>
        <span>Are you sure you want to delete location <strong>"{{ deleteDialog.location?.name }}"</strong>?</span>
      </div>
      <p class="text-600">This action cannot be undone.</p>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="deleteDialog.show = false" />
        <Button label="Delete" severity="danger" @click="deleteLocation" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { debounce } from '@/utils/debounce'
import { apiClient } from '@/utils/apiClient'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import Checkbox from 'primevue/checkbox'
import Dialog from 'primevue/dialog'
import Tag from 'primevue/tag'
import Divider from 'primevue/divider'

// Composables
const toast = useToast()

// Data
const locations = ref([
  {
    id: 1,
    code: 'WH001',
    name: 'Main Warehouse',
    description: 'Primary storage facility',
    is_active: true,
    address_line1: '123 Industrial Blvd',
    city: 'Manufacturing City',
    state: 'CA',
    postal_code: '90210',
    country: 'USA'
  },
  {
    id: 2,
    code: 'STORE01',
    name: 'Retail Store',
    description: 'Customer-facing retail location',
    is_active: true,
    address_line1: '456 Main Street',
    city: 'Downtown',
    state: 'CA',
    postal_code: '90211'
  }
])

const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref(null)

// Dialog state
const dialog = reactive({
  show: false,
  isEdit: false,
  saving: false,
  formData: {
    code: '',
    name: '',
    description: '',
    is_active: true,
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: ''
  },
  editId: null
})

const deleteDialog = reactive({
  show: false,
  location: null
})

// Validation errors
const errors = reactive({})

// Options
const statusOptions = [
  { label: 'Active', value: true },
  { label: 'Inactive', value: false }
]

// Methods
const fetchLocations = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) {
      params.name = searchQuery.value
    }
    if (statusFilter.value !== null) {
      params.is_active = statusFilter.value
    }
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500))
    // const response = await apiClient.get('/api/v1/inventory/locations', { params })
    // locations.value = response.data
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load locations' })
    console.error('Error fetching locations:', error)
  } finally {
    loading.value = false
  }
}

const debouncedFetchLocations = debounce(fetchLocations, 300)

const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = null
  fetchLocations()
}

const validateForm = () => {
  const newErrors = {}
  
  if (!dialog.formData.code.trim()) {
    newErrors.code = 'Code is required'
  }
  
  if (!dialog.formData.name.trim()) {
    newErrors.name = 'Name is required'
  }
  
  Object.assign(errors, newErrors)
  return Object.keys(newErrors).length === 0
}

const openCreateDialog = () => {
  dialog.isEdit = false
  dialog.editId = null
  dialog.formData = {
    code: '',
    name: '',
    description: '',
    is_active: true,
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: ''
  }
  Object.keys(errors).forEach(key => delete errors[key])
  dialog.show = true
}

const viewLocation = (location) => {
  console.log('View location:', location)
}

const editLocation = (location) => {
  dialog.isEdit = true
  dialog.editId = location.id
  dialog.formData = {
    code: location.code,
    name: location.name,
    description: location.description || '',
    is_active: location.is_active,
    address_line1: location.address_line1 || '',
    address_line2: location.address_line2 || '',
    city: location.city || '',
    state: location.state || '',
    postal_code: location.postal_code || '',
    country: location.country || ''
  }
  Object.keys(errors).forEach(key => delete errors[key])
  dialog.show = true
}

const saveLocation = async () => {
  if (!validateForm()) {
    toast.add({ severity: 'error', summary: 'Validation Error', detail: 'Please fix the errors and try again' })
    return
  }
  
  dialog.saving = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (dialog.isEdit) {
      // await apiClient.put(`/api/v1/inventory/locations/${dialog.editId}`, dialog.formData)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Location updated successfully' })
    } else {
      // await apiClient.post('/api/v1/inventory/locations', dialog.formData)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Location created successfully' })
    }
    
    dialog.show = false
    fetchLocations()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save location' })
    console.error('Error saving location:', error)
  } finally {
    dialog.saving = false
  }
}

const confirmDelete = (location) => {
  deleteDialog.location = location
  deleteDialog.show = true
}

const deleteLocation = async () => {
  if (!deleteDialog.location) return
  
  try {
    // await apiClient.delete(`/api/v1/inventory/locations/${deleteDialog.location.id}`)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Location deleted successfully' })
    fetchLocations()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete location' })
    console.error('Error deleting location:', error)
  } finally {
    deleteDialog.show = false
    deleteDialog.location = null
  }
}

const formatAddress = (location) => {
  const parts = [
    location.address_line1,
    location.city,
    location.state,
    location.postal_code
  ].filter(Boolean)
  return parts.join(', ')
}

// Lifecycle hooks
onMounted(() => {
  fetchLocations()
})
</script>

<style scoped>
.location-management {
  padding: 1.5rem;
}

.field {
  margin-bottom: 1.5rem;
}

.field-checkbox {
  margin-bottom: 1.5rem;
}
</style>