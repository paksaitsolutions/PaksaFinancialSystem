<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Payment Processing</h2>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="openPaymentDialog" data-shortcut="create">
          <v-icon left>mdi-plus</v-icon>
          Record Payment
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="payments"
          :loading="loading"
          :items-per-page="10"
        >
          <template v-slot:item.amount="{ item }">
            {{ formatCurrency(item.amount) }}
          </template>
          
          <template v-slot:item.payment_method="{ item }">
            <v-chip small>{{ formatPaymentMethod(item.payment_method) }}</v-chip>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn icon small @click="viewPayment(item)">
              <v-icon small>mdi-eye</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Payment Dialog -->
    <v-dialog v-model="paymentDialog" max-width="600px">
      <v-card>
        <v-card-title>Record Payment</v-card-title>
        <v-card-text>
          <v-form ref="paymentForm" v-model="formValid">
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedPayment.customer_id"
                  :items="customers"
                  item-title="name"
                  item-value="id"
                  label="Customer"
                  :rules="[v => !!v || 'Customer is required']"
                  @update:modelValue="loadCustomerInvoices"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedPayment.invoice_id"
                  :items="customerInvoices"
                  item-title="invoice_number"
                  item-value="id"
                  label="Invoice"
                  :rules="[v => !!v || 'Invoice is required']"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedPayment.amount"
                  label="Payment Amount"
                  type="number"
                  prefix="$"
                  :rules="[v => !!v || 'Amount is required', v => v > 0 || 'Amount must be positive']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedPayment.payment_date"
                  label="Payment Date"
                  type="date"
                  :rules="[v => !!v || 'Date is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedPayment.payment_method"
                  :items="paymentMethods"
                  item-title="text"
                  item-value="value"
                  label="Payment Method"
                  :rules="[v => !!v || 'Payment method is required']"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedPayment.reference"
                  label="Reference/Check Number"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="editedPayment.notes"
                  label="Notes"
                  rows="2"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="paymentDialog = false" data-shortcut="close">Cancel</v-btn>
          <v-btn color="primary" @click="savePayment" :disabled="!formValid" data-shortcut="save">Record Payment</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'

export default {
  name: 'PaymentProcessing',
  components: { ResponsiveContainer },
  
  data: () => ({
    loading: false,
    paymentDialog: false,
    formValid: false,
    payments: [
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
    ],
    customers: [
      { id: '1', name: 'ABC Corporation' },
      { id: '2', name: 'XYZ Company' }
    ],
    customerInvoices: [],
    paymentMethods: [
      { text: 'Cash', value: 'cash' },
      { text: 'Check', value: 'check' },
      { text: 'Credit Card', value: 'credit_card' },
      { text: 'Bank Transfer', value: 'bank_transfer' },
      { text: 'ACH', value: 'ach' }
    ],
    editedPayment: {
      customer_id: '',
      invoice_id: '',
      amount: 0,
      payment_date: new Date().toISOString().substr(0, 10),
      payment_method: '',
      reference: '',
      notes: ''
    },
    headers: [
      { title: 'Payment #', key: 'payment_number' },
      { title: 'Customer', key: 'customer_name' },
      { title: 'Invoice', key: 'invoice_number' },
      { title: 'Amount', key: 'amount' },
      { title: 'Date', key: 'payment_date' },
      { title: 'Method', key: 'payment_method' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
  }),

  methods: {
    openPaymentDialog() {
      this.editedPayment = {
        customer_id: '',
        invoice_id: '',
        amount: 0,
        payment_date: new Date().toISOString().substr(0, 10),
        payment_method: '',
        reference: '',
        notes: ''
      }
      this.paymentDialog = true
    },

    loadCustomerInvoices() {
      // Mock data - in real app, fetch from API
      this.customerInvoices = [
        { id: '1', invoice_number: 'INV-1001', balance: 5000 },
        { id: '2', invoice_number: 'INV-1002', balance: 3000 }
      ]
    },

    savePayment() {
      const customer = this.customers.find(c => c.id === this.editedPayment.customer_id)
      const invoice = this.customerInvoices.find(i => i.id === this.editedPayment.invoice_id)

      this.payments.push({
        ...this.editedPayment,
        id: Date.now().toString(),
        payment_number: `PAY-${1000 + this.payments.length + 1}`,
        customer_name: customer?.name,
        invoice_number: invoice?.invoice_number
      })
      this.paymentDialog = false
    },

    viewPayment(payment) {
      console.log('View payment:', payment)
    },

    formatPaymentMethod(method) {
      return method.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }
  }
}
</script>