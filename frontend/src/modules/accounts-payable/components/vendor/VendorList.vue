<template>
  <div class="vendor-list">
    <Card>
      <template #header>
        <div class="flex justify-content-between align-items-center">
          <h2>Vendors</h2>
          <Button 
            label="Add Vendor" 
            icon="pi pi-plus" 
            @click="openCreateDialog"
          />
        </div>
      </template>
      
      <template #content>
        <!-- Search and filters -->
        <div class="grid mb-4">
          <div class="col-12 md:col-4">
            <span class="p-input-icon-left w-full">
              <i class="pi pi-search" />
              <InputText 
                v-model="filters.name" 
                placeholder="Search by name" 
                class="w-full"
                @input="debouncedFetchVendors"
              />
            </span>
          </div>
          <div class="col-12 md:col-3">
            <Dropdown 
              v-model="filters.status" 
              :options="statusOptions" 
              optionLabel="title" 
              optionValue="value"
              placeholder="Status" 
              class="w-full"
              showClear
              @change="fetchVendors"
            />
          </div>
          <div class="col-12 md:col-3">
            <Dropdown 
              v-model="filters.is1099" 
              :options="is1099Options" 
              optionLabel="title" 
              optionValue="value"
              placeholder="1099 Status" 
              class="w-full"
              showClear
              @change="fetchVendors"
            />
          </div>
          <div class="col-12 md:col-2">
            <Button 
              label="Clear" 
              icon="pi pi-filter-slash" 
              class="p-button-outlined w-full"
              @click="clearFilters"
            />
          </div>
        </div>
        
        <!-- Data table -->
        <DataTable 
          :value="vendors" 
          :loading="loading"
          :paginator="true"
          :rows="pagination.itemsPerPage"
          :totalRecords="pagination.totalItems"
          :lazy="true"
          @page="handleTableUpdate"
          @sort="handleTableUpdate"
          class="p-datatable-sm"
          responsiveLayout="scroll"
        >
          <Column field="code" header="Code" :sortable="true" />
          <Column field="name" header="Name" :sortable="true" />
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag 
                :value="data.status" 
                :severity="getStatusSeverity(data.status)"
              />
            </template>
          </Column>
          <Column field="is_1099" header="1099" :sortable="true">
            <template #body="{ data }">
              <i v-if="data.is_1099" class="pi pi-check text-green-600"></i>
              <i v-else class="pi pi-times text-red-600"></i>
            </template>
          </Column>
          <Column field="phone" header="Phone" />
          <Column field="email" header="Email" />
          <Column header="Actions" style="width: 10rem">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-text p-button-sm" 
                  @click="viewVendor(data)"
                  v-tooltip.top="'View'"
                />
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-sm p-button-warning" 
                  @click="editVendor(data)"
                  v-tooltip.top="'Edit'"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-danger" 
                  @click="confirmDelete(data)"
                  v-tooltip.top="'Delete'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
    
    <!-- Create/Edit Dialog -->
    <Dialog 
      v-model:visible="dialog.show" 
      :header="dialog.isEdit ? 'Edit Vendor' : 'New Vendor'"
      :style="{width: '800px'}" 
      :modal="true"
      class="p-fluid"
    >
      <TabView>
        <TabPanel header="Basic Information">
          <div class="grid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="code">Vendor Code</label>
                <InputText id="code" v-model="vendorForm.code" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="name">Vendor Name</label>
                <InputText id="name" v-model="vendorForm.name" />
              </div>
            </div>
          </div>
        </TabPanel>
        <TabPanel header="Contact Information">
          <div class="grid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="phone">Phone</label>
                <InputText id="phone" v-model="vendorForm.phone" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="email">Email</label>
                <InputText id="email" v-model="vendorForm.email" />
              </div>
            </div>
          </div>
        </TabPanel>
        <TabPanel header="Address">
          <div class="grid">
            <div class="col-12">
              <div class="field">
                <label for="address">Address</label>
                <InputText id="address" v-model="vendorForm.address" />
              </div>
            </div>
          </div>
        </TabPanel>
        <TabPanel header="Payment Information">
          <div class="grid">
            <div class="col-12">
              <div class="field-checkbox">
                <Checkbox id="is1099" v-model="vendorForm.is_1099" :binary="true" />
                <label for="is1099">1099 Vendor</label>
              </div>
            </div>
          </div>
        </TabPanel>
        <TabPanel header="Additional Information">
          <div class="grid">
            <div class="col-12">
              <div class="field">
                <label for="notes">Notes</label>
                <Textarea id="notes" v-model="vendorForm.notes" rows="3" />
              </div>
            </div>
          </div>
        </TabPanel>
      </TabView>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="dialog.show = false"
        />
        <Button 
          :label="dialog.isEdit ? 'Update' : 'Create'" 
          icon="pi pi-check" 
          @click="saveVendor"
          :loading="saving"
        />
      </template>
    </Dialog>
    
    <!-- View Vendor Dialog -->
    <Dialog 
      v-model:visible="viewDialog" 
      :header="'Vendor Details - ' + (viewingVendor?.name || '')"
      :style="{width: '600px'}" 
      :modal="true"
    >
      <div v-if="viewingVendor" class="grid">
        <div class="col-6">
          <div class="field">
            <label class="font-semibold">Vendor Code</label>
            <div>{{ viewingVendor.code }}</div>
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label class="font-semibold">Vendor Name</label>
            <div>{{ viewingVendor.name }}</div>
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label class="font-semibold">Status</label>
            <div><Tag :value="viewingVendor.status" :severity="getStatusSeverity(viewingVendor.status)" /></div>
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label class="font-semibold">1099 Vendor</label>
            <div>
              <i v-if="viewingVendor.is_1099" class="pi pi-check text-green-600"></i>
              <i v-else class="pi pi-times text-red-600"></i>
              {{ viewingVendor.is_1099 ? 'Yes' : 'No' }}
            </div>
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label class="font-semibold">Phone</label>
            <div>{{ viewingVendor.phone || 'N/A' }}</div>
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label class="font-semibold">Email</label>
            <div>{{ viewingVendor.email || 'N/A' }}</div>
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label class="font-semibold">Address</label>
            <div>{{ viewingVendor.address || 'N/A' }}</div>
          </div>
        </div>
        <div class="col-12" v-if="viewingVendor.notes">
          <div class="field">
            <label class="font-semibold">Notes</label>
            <div>{{ viewingVendor.notes }}</div>
          </div>
        </div>
      </div>
      <template #footer>
        <Button 
          label="Close" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="viewDialog = false"
        />
        <Button 
          label="Edit" 
          icon="pi pi-pencil" 
          class="p-button-warning" 
          @click="editVendor(viewingVendor); viewDialog = false"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deleteDialog.show" 
      header="Delete Vendor" 
      :style="{width: '450px'}" 
      :modal="true"
    >
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to delete vendor "{{ deleteDialog.vendor?.name }}"? This action cannot be undone.</span>
      </div>
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="deleteDialog.show = false"
        />
        <Button 
          label="Delete" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="deleteVendor"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

// Data
const vendors = ref([])
const loading = ref(false)
const saving = ref(false)
const selectedVendor = ref(null)

// Pagination
const pagination = reactive({
  page: 1,
  itemsPerPage: 10,
  totalItems: 0,
  sortBy: 'name',
  sortDesc: false,
})

// Filters
const filters = reactive({
  name: '',
  status: null,
  is1099: null,
})

// Dialogs
const dialog = reactive({
  show: false,
  isEdit: false,
})

const deleteDialog = reactive({
  show: false,
  vendor: null,
})

const viewDialog = ref(false)
const viewingVendor = ref(null)

// Form
const vendorForm = ref({
  code: '',
  name: '',
  phone: '',
  email: '',
  address: '',
  is_1099: false,
  notes: '',
  status: 'active'
})

// Options
const statusOptions = [
  { title: 'Active', value: 'active' },
  { title: 'Inactive', value: 'inactive' },
  { title: 'Hold', value: 'hold' },
  { title: 'Pending Approval', value: 'pending_approval' },
  { title: 'Blocked', value: 'blocked' },
]

const is1099Options = [
  { title: 'Yes', value: true },
  { title: 'No', value: false },
]

// Methods
const fetchVendors = async () => {
  loading.value = true
  try {
    // Mock data
    vendors.value = [
      {
        id: 1,
        code: 'V001',
        name: 'ABC Supplies',
        status: 'active',
        is_1099: true,
        phone: '555-0123',
        email: 'contact@abcsupplies.com'
      },
      {
        id: 2,
        code: 'V002',
        name: 'XYZ Services',
        status: 'active',
        is_1099: false,
        phone: '555-0456',
        email: 'info@xyzservices.com'
      }
    ]
    pagination.totalItems = vendors.value.length
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load vendors' })
  } finally {
    loading.value = false
  }
}

const debouncedFetchVendors = () => {
  setTimeout(fetchVendors, 300)
}

const handleTableUpdate = () => {
  fetchVendors()
}

const clearFilters = () => {
  filters.name = ''
  filters.status = null
  filters.is1099 = null
  fetchVendors()
}

const openCreateDialog = () => {
  vendorForm.value = {
    code: '',
    name: '',
    phone: '',
    email: '',
    address: '',
    is_1099: false,
    notes: '',
    status: 'active'
  }
  dialog.isEdit = false
  dialog.show = true
}

const viewVendor = (vendor) => {
  viewingVendor.value = vendor
  viewDialog.value = true
}

const editVendor = (vendor) => {
  vendorForm.value = { ...vendor }
  dialog.isEdit = true
  dialog.show = true
}

const confirmDelete = (vendor) => {
  deleteDialog.vendor = vendor
  deleteDialog.show = true
}

const saveVendor = async () => {
  saving.value = true
  try {
    if (dialog.isEdit) {
      toast.add({ severity: 'success', summary: 'Success', detail: 'Vendor updated' })
    } else {
      vendorForm.value.id = Date.now()
      vendors.value.push({ ...vendorForm.value })
      toast.add({ severity: 'success', summary: 'Success', detail: 'Vendor created' })
    }
    dialog.show = false
    fetchVendors()
  } finally {
    saving.value = false
  }
}

const deleteVendor = async () => {
  try {
    vendors.value = vendors.value.filter(v => v.id !== deleteDialog.vendor.id)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Vendor deleted' })
    deleteDialog.show = false
    deleteDialog.vendor = null
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete vendor' })
  }
}

const getStatusSeverity = (status) => {
  const severities = {
    active: 'success',
    inactive: 'secondary',
    hold: 'warning',
    pending_approval: 'info',
    blocked: 'danger',
  }
  return severities[status] || 'secondary'
}

// Lifecycle hooks
onMounted(() => {
  fetchVendors()
})
</script>

<style scoped>
.vendor-list {
  padding: 1rem;
}
</style>