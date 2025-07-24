<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Customer Management</h2>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="openCustomerDialog" data-shortcut="create">
          <v-icon left>mdi-plus</v-icon>
          New Customer
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="customers"
          :loading="loading"
          :items-per-page="10"
        >
          <template v-slot:item.balance="{ item }">
            {{ formatCurrency(item.balance) }}
          </template>
          
          <template v-slot:item.is_active="{ item }">
            <v-chip :color="item.is_active ? 'success' : 'error'" small>
              {{ item.is_active ? 'Active' : 'Inactive' }}
            </v-chip>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn icon small @click="editCustomer(item)">
              <v-icon small>mdi-pencil</v-icon>
            </v-btn>
            <v-btn icon small @click="viewInvoices(item)">
              <v-icon small>mdi-file-document</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Customer Dialog -->
    <v-dialog v-model="customerDialog" max-width="600px">
      <v-card>
        <v-card-title>{{ editMode ? 'Edit Customer' : 'New Customer' }}</v-card-title>
        <v-card-text>
          <v-form ref="customerForm" v-model="formValid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedCustomer.name"
                  label="Customer Name"
                  :rules="[v => !!v || 'Name is required']"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedCustomer.email"
                  label="Email"
                  type="email"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedCustomer.phone"
                  label="Phone"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedCustomer.credit_limit"
                  label="Credit Limit"
                  type="number"
                  prefix="$"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="editedCustomer.address"
                  label="Address"
                  rows="2"
                ></v-textarea>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedCustomer.payment_terms"
                  label="Payment Terms (Days)"
                  type="number"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-checkbox
                  v-model="editedCustomer.is_active"
                  label="Active"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="customerDialog = false" data-shortcut="close">Cancel</v-btn>
          <v-btn color="primary" @click="saveCustomer" :disabled="!formValid" data-shortcut="save">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'

export default {
  name: 'CustomerManagement',
  components: { ResponsiveContainer },
  
  data: () => ({
    loading: false,
    customerDialog: false,
    editMode: false,
    formValid: false,
    customers: [
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
    ],
    editedCustomer: {
      name: '',
      email: '',
      phone: '',
      address: '',
      credit_limit: null,
      payment_terms: 30,
      is_active: true
    },
    headers: [
      { title: 'Code', key: 'customer_code' },
      { title: 'Name', key: 'name' },
      { title: 'Email', key: 'email' },
      { title: 'Balance', key: 'balance' },
      { title: 'Status', key: 'is_active' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
  }),

  methods: {
    openCustomerDialog() {
      this.editMode = false
      this.editedCustomer = {
        name: '',
        email: '',
        phone: '',
        address: '',
        credit_limit: null,
        payment_terms: 30,
        is_active: true
      }
      this.customerDialog = true
    },

    editCustomer(customer) {
      this.editMode = true
      this.editedCustomer = { ...customer }
      this.customerDialog = true
    },

    saveCustomer() {
      if (this.editMode) {
        const index = this.customers.findIndex(c => c.id === this.editedCustomer.id)
        this.customers[index] = { ...this.editedCustomer }
      } else {
        this.customers.push({
          ...this.editedCustomer,
          id: Date.now().toString(),
          customer_code: `CUST-${1000 + this.customers.length + 1}`,
          balance: 0
        })
      }
      this.customerDialog = false
    },

    viewInvoices(customer) {
      this.$router.push(`/accounts-receivable/invoices?customer=${customer.id}`)
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