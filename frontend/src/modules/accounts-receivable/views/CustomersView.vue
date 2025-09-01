<template>
  <div class="customers-view">
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1>Customers</h1>
          <p>Manage customer information and accounts</p>
        </div>
        <Button label="Add Customer" icon="pi pi-plus" @click="showAddDialog = true" class="p-button-primary" />
      </div>
    </div>

    <Card>
      <template #content>
        <DataTable :value="customers" responsiveLayout="scroll" :paginator="true" :rows="10">
          <Column field="name" header="Customer Name" sortable></Column>
          <Column field="email" header="Email" sortable></Column>
          <Column field="phone" header="Phone"></Column>
          <Column field="balance" header="Balance" sortable>
            <template #body="{ data }">
              <span :class="data.balance >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ formatCurrency(data.balance) }}
              </span>
            </template>
          </Column>
          <Column field="status" header="Status">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text" @click="viewCustomer(data)" />
              <Button icon="pi pi-pencil" class="p-button-text" @click="editCustomer(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="showAddDialog" header="Add New Customer" :modal="true" class="p-fluid customer-dialog">
      <form @submit.prevent="saveCustomer">
        <TabView>
          <TabPanel header="Basic Information">
            <div class="form-grid">
              <div class="field">
                <label for="customerType">Customer Type *</label>
                <Dropdown id="customerType" v-model="customerForm.type" :options="customerTypes" optionLabel="label" optionValue="value" placeholder="Select customer type" />
              </div>
              <div class="field">
                <label for="status">Status</label>
                <Dropdown id="status" v-model="customerForm.status" :options="statusOptions" optionLabel="label" optionValue="value" />
              </div>
            </div>
            
            <div class="field">
              <label for="companyName">Company/Customer Name *</label>
              <InputText id="companyName" v-model="customerForm.companyName" required placeholder="Enter company or customer name" />
            </div>
            
            <div class="form-grid">
              <div class="field">
                <label for="firstName">First Name</label>
                <InputText id="firstName" v-model="customerForm.firstName" placeholder="First name" />
              </div>
              <div class="field">
                <label for="lastName">Last Name</label>
                <InputText id="lastName" v-model="customerForm.lastName" placeholder="Last name" />
              </div>
            </div>
            
            <div class="field">
              <label for="taxId">Tax ID / VAT Number</label>
              <InputText id="taxId" v-model="customerForm.taxId" placeholder="Tax identification number" />
            </div>
          </TabPanel>
          
          <TabPanel header="Contact Information">
            <div class="form-grid">
              <div class="field">
                <label for="email">Email Address *</label>
                <InputText id="email" v-model="customerForm.email" type="email" required placeholder="customer@example.com" />
              </div>
              <div class="field">
                <label for="phone">Phone Number</label>
                <InputText id="phone" v-model="customerForm.phone" placeholder="(555) 123-4567" />
              </div>
            </div>
            
            <div class="form-grid">
              <div class="field">
                <label for="mobile">Mobile Number</label>
                <InputText id="mobile" v-model="customerForm.mobile" placeholder="(555) 987-6543" />
              </div>
              <div class="field">
                <label for="website">Website</label>
                <InputText id="website" v-model="customerForm.website" placeholder="https://www.example.com" />
              </div>
            </div>
            
            <div class="field">
              <label for="contactPerson">Primary Contact Person</label>
              <InputText id="contactPerson" v-model="customerForm.contactPerson" placeholder="Contact person name" />
            </div>
          </TabPanel>
          
          <TabPanel header="Address">
            <div class="field">
              <label for="address1">Address Line 1 *</label>
              <InputText id="address1" v-model="customerForm.address1" required placeholder="Street address" />
            </div>
            
            <div class="field">
              <label for="address2">Address Line 2</label>
              <InputText id="address2" v-model="customerForm.address2" placeholder="Apartment, suite, etc." />
            </div>
            
            <div class="form-grid">
              <div class="field">
                <label for="city">City *</label>
                <InputText id="city" v-model="customerForm.city" required placeholder="City" />
              </div>
              <div class="field">
                <label for="state">State/Province</label>
                <InputText id="state" v-model="customerForm.state" placeholder="State or Province" />
              </div>
            </div>
            
            <div class="form-grid">
              <div class="field">
                <label for="zipCode">ZIP/Postal Code</label>
                <InputText id="zipCode" v-model="customerForm.zipCode" placeholder="ZIP or Postal Code" />
              </div>
              <div class="field">
                <label for="country">Country *</label>
                <Dropdown id="country" v-model="customerForm.country" :options="countries" optionLabel="name" optionValue="code" placeholder="Select country" filter />
              </div>
            </div>
          </TabPanel>
          
          <TabPanel header="Financial Settings">
            <div class="form-grid">
              <div class="field">
                <label for="creditLimit">Credit Limit</label>
                <InputNumber id="creditLimit" v-model="customerForm.creditLimit" mode="currency" currency="USD" placeholder="0.00" />
              </div>
              <div class="field">
                <label for="paymentTerms">Payment Terms</label>
                <Dropdown id="paymentTerms" v-model="customerForm.paymentTerms" :options="paymentTermsOptions" optionLabel="label" optionValue="value" placeholder="Select payment terms" />
              </div>
            </div>
            
            <div class="form-grid">
              <div class="field">
                <label for="currency">Preferred Currency</label>
                <Dropdown id="currency" v-model="customerForm.currency" :options="currencies" optionLabel="label" optionValue="value" placeholder="Select currency" />
              </div>
              <div class="field">
                <label for="taxRate">Tax Rate (%)</label>
                <InputNumber id="taxRate" v-model="customerForm.taxRate" suffix="%" :min="0" :max="100" placeholder="0.00" />
              </div>
            </div>
            
            <div class="field">
              <label for="notes">Notes</label>
              <Textarea id="notes" v-model="customerForm.notes" rows="3" placeholder="Additional notes about the customer..." />
            </div>
          </TabPanel>
        </TabView>
      </form>
      
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" @click="cancelForm" class="p-button-text" />
        <Button label="Save Customer" icon="pi pi-check" @click="saveCustomer" class="p-button-primary" :loading="saving" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const showAddDialog = ref(false)
const saving = ref(false)

const customerForm = ref({
  type: 'business',
  status: 'active',
  companyName: '',
  firstName: '',
  lastName: '',
  taxId: '',
  email: '',
  phone: '',
  mobile: '',
  website: '',
  contactPerson: '',
  address1: '',
  address2: '',
  city: '',
  state: '',
  zipCode: '',
  country: 'US',
  creditLimit: 0,
  paymentTerms: 'net30',
  currency: 'USD',
  taxRate: 0,
  notes: ''
})

const customerTypes = [
  { label: 'Business', value: 'business' },
  { label: 'Individual', value: 'individual' }
]

const statusOptions = [
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'Suspended', value: 'suspended' }
]

const countries = [
  { name: 'United States', code: 'US' },
  { name: 'Canada', code: 'CA' },
  { name: 'United Kingdom', code: 'GB' },
  { name: 'Germany', code: 'DE' },
  { name: 'France', code: 'FR' }
]

const paymentTermsOptions = [
  { label: 'Net 15', value: 'net15' },
  { label: 'Net 30', value: 'net30' },
  { label: 'Net 45', value: 'net45' },
  { label: 'Net 60', value: 'net60' },
  { label: 'Due on Receipt', value: 'due_on_receipt' },
  { label: '2/10 Net 30', value: '2_10_net30' }
]

const currencies = [
  { label: 'USD - US Dollar', value: 'USD' },
  { label: 'EUR - Euro', value: 'EUR' },
  { label: 'GBP - British Pound', value: 'GBP' },
  { label: 'CAD - Canadian Dollar', value: 'CAD' }
]

const customers = ref([
  { id: 1, name: 'ABC Corporation', email: 'contact@abc.com', phone: '555-0123', balance: 15000, status: 'Active' },
  { id: 2, name: 'XYZ Industries', email: 'info@xyz.com', phone: '555-0456', balance: -2500, status: 'Active' },
  { id: 3, name: 'Tech Solutions Ltd', email: 'hello@tech.com', phone: '555-0789', balance: 8750, status: 'Active' }
])

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const getStatusSeverity = (status) => {
  return status === 'Active' ? 'success' : 'danger'
}

const viewCustomer = (customer) => {
  console.log('View customer:', customer)
}

const editCustomer = (customer) => {
  console.log('Edit customer:', customer)
}

const saveCustomer = async () => {
  saving.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    customers.value.push({
      id: customers.value.length + 1,
      name: customerForm.value.companyName || `${customerForm.value.firstName} ${customerForm.value.lastName}`.trim(),
      email: customerForm.value.email,
      phone: customerForm.value.phone,
      balance: 0,
      status: customerForm.value.status === 'active' ? 'Active' : 'Inactive',
      ...customerForm.value
    })
    
    showAddDialog.value = false
    resetForm()
  } catch (error) {
    console.error('Error saving customer:', error)
  } finally {
    saving.value = false
  }
}

const cancelForm = () => {
  showAddDialog.value = false
  resetForm()
}

const resetForm = () => {
  customerForm.value = {
    type: 'business',
    status: 'active',
    companyName: '',
    firstName: '',
    lastName: '',
    taxId: '',
    email: '',
    phone: '',
    mobile: '',
    website: '',
    contactPerson: '',
    address1: '',
    address2: '',
    city: '',
    state: '',
    zipCode: '',
    country: 'US',
    creditLimit: 0,
    paymentTerms: 'net30',
    currency: 'USD',
    taxRate: 0,
    notes: ''
  }
}
</script>

<style scoped>
.customers-view {
  padding: 1rem;
}

.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.page-header h1 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.page-header p {
  margin: 0;
  color: var(--text-color-secondary);
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
}

.customer-dialog {
  width: 90vw;
  max-width: 800px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .customer-dialog {
    width: 95vw;
  }
}
</style>