<template>
  <div class="customer-management">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Customer Management</h1>
        <p class="text-color-secondary">Manage your customers and client relationships</p>
      </div>
      <Button label="Add Customer" icon="pi pi-plus" @click="openNew" />
    </div>
    
    <TabView v-model:activeIndex="activeTab">
      <TabPanel header="Customers">
        <Card>
          <template #content>
            <DataTable :value="customers" :loading="loading" paginator :rows="10">
              <Column field="customerId" header="Customer ID" sortable />
              <Column field="name" header="Name" sortable />
              <Column field="email" header="Email" sortable />
              <Column field="phone" header="Phone" sortable />
              <Column field="creditLimit" header="Credit Limit" sortable>
                <template #body="{ data }">
                  ${{ formatCurrency(data.creditLimit) }}
                </template>
              </Column>
              <Column field="status" header="Status" sortable>
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column header="Actions">
                <template #body="{ data }">
                  <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editCustomer(data)" />
                  <Button icon="pi pi-eye" class="p-button-text p-button-info" @click="viewCustomer(data)" />
                  <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="confirmDeleteCustomer(data)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>
      
      <TabPanel header="Credit Management">
        <Card>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-4" v-for="customer in customers" :key="customer.id">
                <Card>
                  <template #title>{{ customer.name }}</template>
                  <template #content>
                    <div class="flex justify-content-between mb-2">
                      <span>Credit Limit:</span>
                      <span class="font-bold">${{ formatCurrency(customer.creditLimit) }}</span>
                    </div>
                    <div class="flex justify-content-between mb-2">
                      <span>Used Credit:</span>
                      <span>${{ formatCurrency(customer.usedCredit || 0) }}</span>
                    </div>
                    <div class="flex justify-content-between mb-3">
                      <span>Available:</span>
                      <span class="text-green-600 font-bold">${{ formatCurrency((customer.creditLimit || 0) - (customer.usedCredit || 0)) }}</span>
                    </div>
                    <Button label="Update Credit" icon="pi pi-pencil" class="w-full" @click="updateCredit(customer)" />
                  </template>
                </Card>
              </div>
            </div>
          </template>
        </Card>
      </TabPanel>
      
      <TabPanel header="Aging Reports">
        <Card>
          <template #content>
            <div class="text-center p-4">
              <i class="pi pi-chart-line text-4xl text-primary mb-3"></i>
              <h3>Customer Aging Reports</h3>
              <p class="text-color-secondary">Aging analysis and reports will be displayed here</p>
              <Button label="Generate Report" icon="pi pi-file" @click="generateAgingReport" />
            </div>
          </template>
        </Card>
      </TabPanel>
    </TabView>
    
    <!-- Add/Edit Customer Dialog -->
    <Dialog v-model:visible="customerDialog" header="Customer Details" :modal="true" :style="{width: '600px'}">
      <div class="field">
        <label>Customer Name</label>
        <InputText v-model="customer.name" class="w-full" :class="{'p-invalid': submitted && !customer.name}" />
        <small class="p-error" v-if="submitted && !customer.name">Name is required.</small>
      </div>
      <div class="field">
        <label>Email</label>
        <InputText v-model="customer.email" class="w-full" :class="{'p-invalid': submitted && !customer.email}" />
        <small class="p-error" v-if="submitted && !customer.email">Email is required.</small>
      </div>
      <div class="field">
        <label>Phone</label>
        <InputText v-model="customer.phone" class="w-full" />
      </div>
      <div class="field">
        <label>Address</label>
        <Textarea v-model="customer.address" rows="3" class="w-full" />
      </div>
      <div class="field">
        <label>Credit Limit</label>
        <InputNumber v-model="customer.creditLimit" mode="currency" currency="USD" class="w-full" />
      </div>
      <div class="field">
        <label>Status</label>
        <Dropdown v-model="customer.status" :options="statuses" optionLabel="label" optionValue="value" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="hideDialog" />
        <Button label="Save" @click="saveCustomer" />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:visible="deleteCustomerDialog" header="Confirm" :modal="true" :style="{width: '450px'}">
      <div class="flex align-items-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="customer">Are you sure you want to delete <b>{{ customer.name }}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" class="p-button-text" @click="deleteCustomerDialog = false" />
        <Button label="Yes" class="p-button-danger" @click="deleteCustomer" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

interface Customer {
  id?: string
  customerId: string
  name: string
  email: string
  phone: string
  address: string
  creditLimit: number
  usedCredit?: number
  status: string
}

const toast = useToast()
const loading = ref(false)
const customerDialog = ref(false)
const deleteCustomerDialog = ref(false)
const submitted = ref(false)
const activeTab = ref(0)

const customers = ref<Customer[]>([])
const customer = ref<Customer>({
  customerId: '',
  name: '',
  email: '',
  phone: '',
  address: '',
  creditLimit: 0,
  status: 'active'
})

const statuses = ref([
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'Suspended', value: 'suspended' }
])

const openNew = () => {
  customer.value = {
    customerId: `CUS${Date.now()}`,
    name: '',
    email: '',
    phone: '',
    address: '',
    creditLimit: 0,
    status: 'active'
  }
  submitted.value = false
  customerDialog.value = true
}

const editCustomer = (customerData: Customer) => {
  customer.value = { ...customerData }
  customerDialog.value = true
}

const viewCustomer = (customerData: Customer) => {
  customer.value = { ...customerData }
  customerDialog.value = true
}

const hideDialog = () => {
  customerDialog.value = false
  submitted.value = false
}

const saveCustomer = async () => {
  submitted.value = true
  if (customer.value.name && customer.value.email) {
    try {
      if (customer.value.id) {
        const index = customers.value.findIndex(c => c.id === customer.value.id)
        if (index !== -1) customers.value[index] = { ...customer.value }
        toast.add({ severity: 'success', summary: 'Success', detail: 'Customer updated', life: 3000 })
      } else {
        customer.value.id = Date.now().toString()
        customers.value.push({ ...customer.value })
        toast.add({ severity: 'success', summary: 'Success', detail: 'Customer created', life: 3000 })
      }
      customerDialog.value = false
    } catch (error: any) {
      toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'Operation failed', life: 3000 })
    }
  }
}

const confirmDeleteCustomer = (customerData: Customer) => {
  customer.value = { ...customerData }
  deleteCustomerDialog.value = true
}

const deleteCustomer = async () => {
  try {
    customers.value = customers.value.filter(c => c.id !== customer.value.id)
    deleteCustomerDialog.value = false
    toast.add({ severity: 'success', summary: 'Success', detail: 'Customer deleted', life: 3000 })
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Delete failed', life: 3000 })
  }
}

const updateCredit = (customerData: Customer) => {
  toast.add({ severity: 'info', summary: 'Credit Update', detail: `Updating credit for ${customerData.name}`, life: 3000 })
}

const generateAgingReport = () => {
  toast.add({ severity: 'info', summary: 'Report Generation', detail: 'Generating aging report...', life: 3000 })
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'danger'
    case 'suspended': return 'warning'
    default: return 'info'
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US').format(amount || 0)
}

const loadCustomers = async () => {
  loading.value = true
  try {
    // Mock data
    customers.value = [
      { id: '1', customerId: 'CUS001', name: 'Acme Corp', email: 'contact@acmecorp.com', phone: '123-456-7890', address: '123 Business St', creditLimit: 50000, usedCredit: 15000, status: 'active' },
      { id: '2', customerId: 'CUS002', name: 'Tech Solutions Inc', email: 'info@techsolutions.com', phone: '123-456-7891', address: '456 Tech Ave', creditLimit: 75000, usedCredit: 25000, status: 'active' },
      { id: '3', customerId: 'CUS003', name: 'Global Services', email: 'sales@globalservices.com', phone: '123-456-7892', address: '789 Global Blvd', creditLimit: 100000, usedCredit: 80000, status: 'suspended' }
    ]
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCustomers()
})
</script>

<style scoped>
.customer-management {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>