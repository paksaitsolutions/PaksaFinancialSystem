<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Invoice Generation</h2>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="openInvoiceDialog" data-shortcut="create">
          <v-icon left>mdi-plus</v-icon>
          New Invoice
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="invoices"
          :loading="loading"
          :items-per-page="10"
        >
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" small>
              {{ item.status.toUpperCase() }}
            </v-chip>
          </template>
          
          <template v-slot:item.total_amount="{ item }">
            {{ formatCurrency(item.total_amount) }}
          </template>
          
          <template v-slot:item.balance="{ item }">
            {{ formatCurrency(item.balance) }}
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn icon small @click="viewInvoice(item)">
              <v-icon small>mdi-eye</v-icon>
            </v-btn>
            <v-btn icon small @click="sendInvoice(item)" :disabled="item.status === 'sent'">
              <v-icon small>mdi-send</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Invoice Dialog -->
    <v-dialog v-model="invoiceDialog" max-width="800px">
      <v-card>
        <v-card-title>{{ editMode ? 'View Invoice' : 'New Invoice' }}</v-card-title>
        <v-card-text>
          <v-form ref="invoiceForm" v-model="formValid">
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedInvoice.customer_id"
                  :items="customers"
                  item-title="name"
                  item-value="id"
                  label="Customer"
                  :rules="[v => !!v || 'Customer is required']"
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedInvoice.invoice_date"
                  label="Invoice Date"
                  type="date"
                  :rules="[v => !!v || 'Date is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedInvoice.due_date"
                  label="Due Date"
                  type="date"
                  :rules="[v => !!v || 'Due date is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedInvoice.reference"
                  label="Reference"
                ></v-text-field>
              </v-col>
            </v-row>

            <!-- Line Items -->
            <h3 class="mb-4">Line Items</h3>
            <v-row v-for="(item, index) in editedInvoice.line_items" :key="index" class="mb-2">
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="item.description"
                  label="Description"
                  :rules="[v => !!v || 'Description is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field
                  v-model="item.quantity"
                  label="Quantity"
                  type="number"
                  @input="calculateLineAmount(index)"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field
                  v-model="item.unit_price"
                  label="Unit Price"
                  type="number"
                  prefix="$"
                  @input="calculateLineAmount(index)"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="2">
                <v-text-field
                  v-model="item.amount"
                  label="Amount"
                  prefix="$"
                  readonly
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="2">
                <v-btn icon color="error" @click="removeLineItem(index)">
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </v-col>
            </v-row>
            
            <v-btn color="primary" variant="outlined" @click="addLineItem" class="mb-4">
              <v-icon left>mdi-plus</v-icon>
              Add Line Item
            </v-btn>

            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="editedInvoice.notes"
                  label="Notes"
                  rows="2"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="invoiceDialog = false" data-shortcut="close">Cancel</v-btn>
          <v-btn color="primary" @click="saveInvoice" :disabled="!formValid" data-shortcut="save">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'

export default {
  name: 'InvoiceGeneration',
  components: { ResponsiveContainer },
  
  data: () => ({
    loading: false,
    invoiceDialog: false,
    editMode: false,
    formValid: false,
    invoices: [
      {
        id: '1',
        invoice_number: 'INV-1001',
        customer_name: 'ABC Corporation',
        invoice_date: '2024-01-15',
        due_date: '2024-02-14',
        status: 'sent',
        total_amount: 5000,
        balance: 5000
      }
    ],
    customers: [
      { id: '1', name: 'ABC Corporation' },
      { id: '2', name: 'XYZ Company' }
    ],
    editedInvoice: {
      customer_id: '',
      invoice_date: new Date().toISOString().substr(0, 10),
      due_date: '',
      reference: '',
      notes: '',
      line_items: []
    },
    headers: [
      { title: 'Invoice #', key: 'invoice_number' },
      { title: 'Customer', key: 'customer_name' },
      { title: 'Date', key: 'invoice_date' },
      { title: 'Due Date', key: 'due_date' },
      { title: 'Status', key: 'status' },
      { title: 'Total', key: 'total_amount' },
      { title: 'Balance', key: 'balance' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
  }),

  methods: {
    openInvoiceDialog() {
      this.editMode = false
      this.editedInvoice = {
        customer_id: '',
        invoice_date: new Date().toISOString().substr(0, 10),
        due_date: '',
        reference: '',
        notes: '',
        line_items: [{ description: '', quantity: 1, unit_price: 0, amount: 0 }]
      }
      this.invoiceDialog = true
    },

    addLineItem() {
      this.editedInvoice.line_items.push({
        description: '',
        quantity: 1,
        unit_price: 0,
        amount: 0
      })
    },

    removeLineItem(index) {
      this.editedInvoice.line_items.splice(index, 1)
    },

    calculateLineAmount(index) {
      const item = this.editedInvoice.line_items[index]
      item.amount = (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0)
    },

    saveInvoice() {
      const subtotal = this.editedInvoice.line_items.reduce((sum, item) => sum + item.amount, 0)
      const tax = subtotal * 0.08
      const total = subtotal + tax

      this.invoices.push({
        ...this.editedInvoice,
        id: Date.now().toString(),
        invoice_number: `INV-${1000 + this.invoices.length + 1}`,
        customer_name: this.customers.find(c => c.id === this.editedInvoice.customer_id)?.name,
        status: 'draft',
        total_amount: total,
        balance: total
      })
      this.invoiceDialog = false
    },

    viewInvoice(invoice) {
      console.log('View invoice:', invoice)
    },

    sendInvoice(invoice) {
      invoice.status = 'sent'
    },

    getStatusColor(status) {
      const colors = {
        draft: 'grey',
        sent: 'blue',
        paid: 'success',
        overdue: 'error'
      }
      return colors[status] || 'grey'
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