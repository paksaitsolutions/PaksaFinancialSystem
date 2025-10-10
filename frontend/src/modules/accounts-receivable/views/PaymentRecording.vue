<template>
  <div class="payment-recording">
    <h2>Record Customer Payment</h2>
    <Card>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label>Customer</label>
              <Dropdown v-model="payment.customer_id" :options="customers" optionLabel="name" optionValue="id" placeholder="Select Customer" class="w-full" />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label>Invoice</label>
              <Dropdown v-model="payment.invoice_id" :options="invoices" optionLabel="invoice_number" optionValue="id" placeholder="Select Invoice" class="w-full" />
            </div>
          </div>
          <div class="col-12 md:col-4">
            <div class="field">
              <label>Payment Amount</label>
              <InputNumber v-model="payment.amount" mode="currency" currency="USD" class="w-full" />
            </div>
          </div>
          <div class="col-12 md:col-4">
            <div class="field">
              <label>Payment Method</label>
              <Dropdown v-model="payment.payment_method" :options="paymentMethods" placeholder="Select Method" class="w-full" />
            </div>
          </div>
          <div class="col-12 md:col-4">
            <div class="field">
              <label>Reference</label>
              <InputText v-model="payment.reference" placeholder="Check #, Transaction ID" class="w-full" />
            </div>
          </div>
        </div>
        <Button label="Record Payment" icon="pi pi-check" @click="recordPayment" :loading="processing" />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { invoiceService, customerService } from '@/api/arService'

const toast = useToast()
const processing = ref(false)
const customers = ref([])
const invoices = ref([])

const payment = ref({
  customer_id: '',
  invoice_id: '',
  amount: 0,
  payment_method: '',
  reference: ''
})

const paymentMethods = ref([
  'Cash', 'Check', 'Credit Card', 'Bank Transfer', 'ACH', 'Wire Transfer'
])

const recordPayment = async () => {
  processing.value = true
  try {
    await invoiceService.recordPayment(payment.value)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Payment recorded successfully' })
    resetForm()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to record payment' })
  } finally {
    processing.value = false
  }
}

const resetForm = () => {
  payment.value = {
    customer_id: '',
    invoice_id: '',
    amount: 0,
    payment_method: '',
    reference: ''
  }
}

onMounted(async () => {
  try {
    const [customersData, invoicesData] = await Promise.all([
      customerService.getCustomers(),
      invoiceService.getInvoices()
    ])
    customers.value = customersData.customers
    invoices.value = invoicesData.invoices
  } catch (error) {
    console.error('Error loading data:', error)
  }
})
</script>