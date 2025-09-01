<template>
  <ResponsiveContainer>
    <Card>
      <template #header>
        <div class="flex justify-content-between align-items-center p-4">
          <h2 class="m-0">Payment Processing</h2>
          <Button label="Record Payment" icon="pi pi-plus" @click="openPaymentDialog" data-shortcut="create" />
        </div>
      </template>
      
      <template #content>
        <DataTable
          :value="payments"
          :loading="loading"
          :paginator="true"
          :rows="10"
          responsiveLayout="scroll"
        >
          <Column field="payment_number" header="Payment #" />
          <Column field="customer_name" header="Customer" />
          <Column field="invoice_number" header="Invoice" />
          <Column field="amount" header="Amount">
            <template #body="{ data }">
              {{ formatCurrency(data.amount) }}
            </template>
          </Column>
          <Column field="payment_date" header="Date" />
          <Column field="payment_method" header="Method">
            <template #body="{ data }">
              <Tag :value="formatPaymentMethod(data.payment_method)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text p-button-sm" @click="viewPayment(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Payment Dialog -->
    <Dialog v-model:visible="paymentDialog" header="Record Payment" :modal="true" :style="{ width: '600px' }">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="customer">Customer *</label>
            <Dropdown id="customer" v-model="editedPayment.customer_id" :options="customers" optionLabel="name" optionValue="id" placeholder="Select Customer" class="w-full" @change="loadCustomerInvoices" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="invoice">Invoice *</label>
            <Dropdown id="invoice" v-model="editedPayment.invoice_id" :options="customerInvoices" optionLabel="invoice_number" optionValue="id" placeholder="Select Invoice" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="amount">Payment Amount *</label>
            <InputNumber id="amount" v-model="editedPayment.amount" mode="currency" currency="USD" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="payment_date">Payment Date *</label>
            <Calendar id="payment_date" v-model="editedPayment.payment_date" dateFormat="yy-mm-dd" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="payment_method">Payment Method *</label>
            <Dropdown id="payment_method" v-model="editedPayment.payment_method" :options="paymentMethods" optionLabel="text" optionValue="value" placeholder="Select Method" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="reference">Reference/Check Number</label>
            <InputText id="reference" v-model="editedPayment.reference" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="notes">Notes</label>
            <Textarea id="notes" v-model="editedPayment.notes" rows="2" class="w-full" />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="paymentDialog = false" data-shortcut="close" />
        <Button label="Record Payment" icon="pi pi-check" @click="savePayment" :disabled="!editedPayment.customer_id || !editedPayment.amount" data-shortcut="save" />
      </template>
    </Dialog>
  </ResponsiveContainer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import Tag from 'primevue/tag'

const loading = ref(false)
const paymentDialog = ref(false)

const payments = ref([
  {
    id: '1',
    payment_number: 'PAY-1001',
    customer_name: 'ABC Corporation',
    invoice_number: 'INV-1001',
    amount: 2500,
    payment_date: '2024-01-20',
    payment_method: 'check',
    reference: 'CHK-12345'
  }
])

const customers = ref([
  { id: '1', name: 'ABC Corporation' },
  { id: '2', name: 'XYZ Company' }
])

const customerInvoices = ref([])

const paymentMethods = ref([
  { text: 'Cash', value: 'cash' },
  { text: 'Check', value: 'check' },
  { text: 'Credit Card', value: 'credit_card' },
  { text: 'Bank Transfer', value: 'bank_transfer' },
  { text: 'ACH', value: 'ach' }
])

const editedPayment = ref({
  customer_id: '',
  invoice_id: '',
  amount: 0,
  payment_date: new Date(),
  payment_method: '',
  reference: '',
  notes: ''
})

const openPaymentDialog = () => {
  editedPayment.value = {
    customer_id: '',
    invoice_id: '',
    amount: 0,
    payment_date: new Date(),
    payment_method: '',
    reference: '',
    notes: ''
  }
  paymentDialog.value = true
}

const loadCustomerInvoices = () => {
  // Mock data - in real app, fetch from API
  customerInvoices.value = [
    { id: '1', invoice_number: 'INV-1001', balance: 5000 },
    { id: '2', invoice_number: 'INV-1002', balance: 3000 }
  ]
}

const savePayment = () => {
  const customer = customers.value.find(c => c.id === editedPayment.value.customer_id)
  const invoice = customerInvoices.value.find(i => i.id === editedPayment.value.invoice_id)

  payments.value.push({
    ...editedPayment.value,
    id: Date.now().toString(),
    payment_number: `PAY-${1000 + payments.value.length + 1}`,
    customer_name: customer?.name,
    invoice_number: invoice?.invoice_number
  })
  paymentDialog.value = false
}

const viewPayment = (payment: any) => {
  console.log('View payment:', payment)
}

const formatPaymentMethod = (method: string) => {
  return method.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}
</script>