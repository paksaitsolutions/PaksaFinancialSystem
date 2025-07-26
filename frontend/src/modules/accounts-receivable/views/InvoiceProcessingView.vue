<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <h1 class="text-h4">Invoice Processing</h1>
          <v-btn color="primary" @click="showCreateInvoice = true">
            <v-icon left>mdi-plus</v-icon>
            Create Invoice
          </v-btn>
        </div>
        
        <v-tabs v-model="activeTab">
          <v-tab value="invoices">Invoices</v-tab>
          <v-tab value="recurring">Recurring</v-tab>
          <v-tab value="payments">Payment Tracking</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="invoices">
            <invoice-list @edit="editInvoice" @approve="approveInvoice" />
          </v-window-item>
          
          <v-window-item value="recurring">
            <recurring-invoice-management @create="createRecurring" />
          </v-window-item>
          
          <v-window-item value="payments">
            <payment-tracking-dashboard @record="recordPayment" />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
    
    <invoice-form-dialog 
      v-model="showCreateInvoice" 
      :invoice="selectedInvoice"
      @save="saveInvoice"
    />
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import InvoiceList from '../components/invoice/InvoiceList.vue'
import RecurringInvoiceManagement from '../components/invoice/RecurringInvoiceManagement.vue'
import PaymentTrackingDashboard from '../components/invoice/PaymentTrackingDashboard.vue'
import InvoiceFormDialog from '../components/invoice/InvoiceFormDialog.vue'
import { useInvoiceStore } from '../store/invoices'

const invoiceStore = useInvoiceStore()
const activeTab = ref('invoices')
const showCreateInvoice = ref(false)
const selectedInvoice = ref(null)

const editInvoice = (invoice) => {
  selectedInvoice.value = invoice
  showCreateInvoice.value = true
}

const saveInvoice = async (invoiceData) => {
  if (selectedInvoice.value) {
    await invoiceStore.updateInvoice(selectedInvoice.value.id, invoiceData)
  } else {
    await invoiceStore.createInvoice(invoiceData)
  }
  showCreateInvoice.value = false
  selectedInvoice.value = null
}

const approveInvoice = async (invoiceId, approvalData) => {
  await invoiceStore.approveInvoice(invoiceId, approvalData)
}

const createRecurring = async (recurringData) => {
  await invoiceStore.createRecurringInvoice(recurringData)
}

const recordPayment = async (invoiceId, paymentData) => {
  await invoiceStore.recordPayment(invoiceId, paymentData)
}
</script>