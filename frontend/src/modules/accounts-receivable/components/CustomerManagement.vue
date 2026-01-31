<template>
  <ResponsiveContainer>
    <Card>
      <template #header>
        <div class="flex justify-content-between align-items-center p-4">
          <h2 class="m-0">Customer Management</h2>
          <Button label="New Customer" icon="pi pi-plus" @click="openCustomerDialog" data-shortcut="create" />
        </div>
      </template>
      
      <template #content>
        <DataTable
          :value="customers"
          :loading="loading"
          :paginator="true"
          :rows="10"
          responsiveLayout="scroll"
        >
          <Column field="customer_code" header="Code" />
          <Column field="name" header="Name" />
          <Column field="email" header="Email" />
          <Column field="balance" header="Balance">
            <template #body="{ data }">
              {{ formatCurrency(data.balance) }}
            </template>
          </Column>
          <Column field="is_active" header="Status">
            <template #body="{ data }">
              <Tag :severity="data.is_active ? 'success' : 'danger'" :value="data.is_active ? 'Active' : 'Inactive'" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" class="p-button-text p-button-sm mr-2" @click="editCustomer(data)" />
              <Button icon="pi pi-file" class="p-button-text p-button-sm" @click="viewInvoices(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Customer Dialog -->
    <Dialog v-model:visible="customerDialog" :header="editMode ? 'Edit Customer' : 'New Customer'" :modal="true" :style="{ width: '600px' }">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="name">Customer Name *</label>
            <InputText id="name" v-model="editedCustomer.name" class="w-full" :class="{ 'p-invalid': !editedCustomer.name }" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="email">Email</label>
            <InputText id="email" v-model="editedCustomer.email" type="email" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="phone">Phone</label>
            <InputText id="phone" v-model="editedCustomer.phone" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="credit_limit">Credit Limit</label>
            <InputNumber id="credit_limit" v-model="editedCustomer.credit_limit" mode="currency" currency="USD" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="address">Address</label>
            <Textarea id="address" v-model="editedCustomer.address" rows="2" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="payment_terms">Payment Terms (Days)</label>
            <InputNumber id="payment_terms" v-model="editedCustomer.payment_terms" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field-checkbox">
            <Checkbox id="is_active" v-model="editedCustomer.is_active" :binary="true" />
            <label for="is_active">Active</label>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="customerDialog = false" data-shortcut="close" />
        <Button label="Save" icon="pi pi-check" @click="saveCustomer" :disabled="!editedCustomer.name" data-shortcut="save" />
      </template>
    </Dialog>
  </ResponsiveContainer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const loading = ref(false)
const customerDialog = ref(false)
const editMode = ref(false)

const customers = ref([
  {
    id: '1',
    customer_code: 'CUST-1001',
    name: 'ABC Corporation',
    email: 'billing@abc.com',
    phone: '555-0123',
    address: '123 Business St, City, ST 12345',
    credit_limit: 50000,
    payment_terms: 30,
    balance: 15000,
    is_active: true
  }
])

const editedCustomer = ref({
  name: '',
  email: '',
  phone: '',
  address: '',
  credit_limit: null,
  payment_terms: 30,
  is_active: true
})

const openCustomerDialog = () => {
  editMode.value = false
  editedCustomer.value = {
    name: '',
    email: '',
    phone: '',
    address: '',
    credit_limit: null,
    payment_terms: 30,
    is_active: true
  }
  customerDialog.value = true
}

const editCustomer = (customer: any) => {
  editMode.value = true
  editedCustomer.value = { ...customer }
  customerDialog.value = true
}

const saveCustomer = () => {
  if (editMode.value) {
    const index = customers.value.findIndex(c => c.id === editedCustomer.value.id)
    customers.value[index] = { ...editedCustomer.value }
  } else {
    customers.value.push({
      ...editedCustomer.value,
      id: Date.now().toString(),
      customer_code: `CUST-${1000 + customers.value.length + 1}`,
      balance: 0
    })
  }
  customerDialog.value = false
}

const viewInvoices = (customer: any) => {
  router.push(`/accounts-receivable/invoices?customer=${customer.id}`)
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}
</script>