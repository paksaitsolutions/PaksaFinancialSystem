<template>
  <div class="vendor-management">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Vendor Management</h1>
        <p class="text-color-secondary">Manage your vendors and supplier relationships</p>
      </div>
      <Button label="Add Vendor" icon="pi pi-plus" @click="openNew" />
    </div>
    
    <TabView v-model:activeIndex="activeTab">
      <TabPanel header="Vendor List">
        <Card>
          <template #content>
            <DataTable :value="vendors" :loading="loading" paginator :rows="10">
              <Column field="vendorId" header="Vendor ID" sortable />
              <Column field="name" header="Name" sortable />
              <Column field="email" header="Email" sortable />
              <Column field="phone" header="Phone" sortable />
              <Column field="status" header="Status" sortable>
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column header="Actions">
                <template #body="{ data }">
                  <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editVendor(data)" />
                  <Button icon="pi pi-eye" class="p-button-text p-button-info" @click="viewVendor(data)" />
                  <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="confirmDeleteVendor(data)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>
      
      <TabPanel header="Approvals">
        <Card>
          <template #content>
            <DataTable :value="pendingApprovals" :loading="loading">
              <Column field="vendorName" header="Vendor" sortable />
              <Column field="requestType" header="Request Type" sortable />
              <Column field="requestDate" header="Request Date" sortable />
              <Column header="Actions">
                <template #body="{ data }">
                  <Button label="Approve" icon="pi pi-check" class="p-button-success mr-2" @click="approveVendor(data)" />
                  <Button label="Reject" icon="pi pi-times" class="p-button-danger" @click="rejectVendor(data)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>
      
      <TabPanel header="Performance">
        <Card>
          <template #content>
            <div class="text-center p-4">
              <i class="pi pi-chart-bar text-4xl text-primary mb-3"></i>
              <h3>Vendor Performance Dashboard</h3>
              <p class="text-color-secondary">Performance metrics and analytics will be displayed here</p>
            </div>
          </template>
        </Card>
      </TabPanel>
    </TabView>
    
    <!-- Add/Edit Vendor Dialog -->
    <Dialog v-model:visible="vendorDialog" header="Vendor Details" :modal="true" :style="{width: '600px'}">
      <div class="field">
        <label>Vendor Name</label>
        <InputText v-model="vendor.name" class="w-full" :class="{'p-invalid': submitted && !vendor.name}" />
        <small class="p-error" v-if="submitted && !vendor.name">Name is required.</small>
      </div>
      <div class="field">
        <label>Email</label>
        <InputText v-model="vendor.email" class="w-full" :class="{'p-invalid': submitted && !vendor.email}" />
        <small class="p-error" v-if="submitted && !vendor.email">Email is required.</small>
      </div>
      <div class="field">
        <label>Phone</label>
        <InputText v-model="vendor.phone" class="w-full" />
      </div>
      <div class="field">
        <label>Address</label>
        <Textarea v-model="vendor.address" rows="3" class="w-full" />
      </div>
      <div class="field">
        <label>Status</label>
        <Dropdown v-model="vendor.status" :options="statuses" optionLabel="label" optionValue="value" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="hideDialog" />
        <Button label="Save" @click="saveVendor" />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:visible="deleteVendorDialog" header="Confirm" :modal="true" :style="{width: '450px'}">
      <div class="flex align-items-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="vendor">Are you sure you want to delete <b>{{ vendor.name }}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" class="p-button-text" @click="deleteVendorDialog = false" />
        <Button label="Yes" class="p-button-danger" @click="deleteVendor" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

interface Vendor {
  id?: string
  vendorId: string
  name: string
  email: string
  phone: string
  address: string
  status: string
}

const toast = useToast()
const loading = ref(false)
const vendorDialog = ref(false)
const deleteVendorDialog = ref(false)
const submitted = ref(false)
const activeTab = ref(0)

const vendors = ref<Vendor[]>([])
const pendingApprovals = ref([])
const vendor = ref<Vendor>({
  vendorId: '',
  name: '',
  email: '',
  phone: '',
  address: '',
  status: 'active'
})

const statuses = ref([
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'Pending', value: 'pending' }
])

const openNew = () => {
  vendor.value = {
    vendorId: `VEN${Date.now()}`,
    name: '',
    email: '',
    phone: '',
    address: '',
    status: 'active'
  }
  submitted.value = false
  vendorDialog.value = true
}

const editVendor = (vendorData: Vendor) => {
  vendor.value = { ...vendorData }
  vendorDialog.value = true
}

const viewVendor = (vendorData: Vendor) => {
  vendor.value = { ...vendorData }
  vendorDialog.value = true
}

const hideDialog = () => {
  vendorDialog.value = false
  submitted.value = false
}

const saveVendor = async () => {
  submitted.value = true
  if (vendor.value.name && vendor.value.email) {
    try {
      if (vendor.value.id) {
        const index = vendors.value.findIndex(v => v.id === vendor.value.id)
        if (index !== -1) vendors.value[index] = { ...vendor.value }
        toast.add({ severity: 'success', summary: 'Success', detail: 'Vendor updated', life: 3000 })
      } else {
        vendor.value.id = Date.now().toString()
        vendors.value.push({ ...vendor.value })
        toast.add({ severity: 'success', summary: 'Success', detail: 'Vendor created', life: 3000 })
      }
      vendorDialog.value = false
    } catch (error: any) {
      toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'Operation failed', life: 3000 })
    }
  }
}

const confirmDeleteVendor = (vendorData: Vendor) => {
  vendor.value = { ...vendorData }
  deleteVendorDialog.value = true
}

const deleteVendor = async () => {
  try {
    vendors.value = vendors.value.filter(v => v.id !== vendor.value.id)
    deleteVendorDialog.value = false
    toast.add({ severity: 'success', summary: 'Success', detail: 'Vendor deleted', life: 3000 })
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Delete failed', life: 3000 })
  }
}

const approveVendor = async (approvalData: any) => {
  toast.add({ severity: 'success', summary: 'Success', detail: 'Vendor approved', life: 3000 })
}

const rejectVendor = async (approvalData: any) => {
  toast.add({ severity: 'info', summary: 'Info', detail: 'Vendor rejected', life: 3000 })
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'danger'
    case 'pending': return 'warning'
    default: return 'info'
  }
}

const loadVendors = async () => {
  loading.value = true
  try {
    // Mock data
    vendors.value = [
      { id: '1', vendorId: 'VEN001', name: 'ABC Supplies', email: 'contact@abcsupplies.com', phone: '123-456-7890', address: '123 Main St', status: 'active' },
      { id: '2', vendorId: 'VEN002', name: 'XYZ Services', email: 'info@xyzservices.com', phone: '123-456-7891', address: '456 Oak Ave', status: 'active' },
      { id: '3', vendorId: 'VEN003', name: 'Tech Solutions', email: 'sales@techsolutions.com', phone: '123-456-7892', address: '789 Pine St', status: 'pending' }
    ]
    
    pendingApprovals.value = [
      { id: '1', vendorName: 'New Vendor Co', requestType: 'New Registration', requestDate: '2024-01-15' },
      { id: '2', vendorName: 'Updated Services', requestType: 'Information Update', requestDate: '2024-01-14' }
    ]
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadVendors()
})
</script>

<style scoped>
.vendor-management {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>