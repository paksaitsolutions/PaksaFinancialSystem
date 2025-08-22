<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Accounts Receivable Aging Report</h2>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="refreshReport">
          <v-icon left>mdi-refresh</v-icon>
          Refresh
        </v-btn>
      </v-card-title>

      <v-card-text>
        <!-- Summary Cards -->
        <v-row class="mb-6">
          <v-col cols="12" md="3">
            <v-card color="success" dark>
              <v-card-text class="text-center">
                <div class="text-h6">{{ formatCurrency(summary.current) }}</div>
                <div class="text-caption">Current (0-30 days)</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card color="warning" dark>
              <v-card-text class="text-center">
                <div class="text-h6">{{ formatCurrency(summary.days31to60) }}</div>
                <div class="text-caption">31-60 days</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card color="orange" dark>
              <v-card-text class="text-center">
                <div class="text-h6">{{ formatCurrency(summary.days61to90) }}</div>
                <div class="text-caption">61-90 days</div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12" md="3">
            <v-card color="error" dark>
              <v-card-text class="text-center">
                <div class="text-h6">{{ formatCurrency(summary.over90) }}</div>
                <div class="text-caption">Over 90 days</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Aging Table -->
        <v-data-table
          :headers="headers"
          :items="agingData"
          :loading="loading"
          :items-per-page="10"
        >
          <template v-slot:item.customer_name="{ item }">
            <strong>{{ item.customer_name }}</strong>
          </template>
          
          <template v-slot:item.current="{ item }">
            <span :class="item.current > 0 ? 'text-success' : ''">
              {{ formatCurrency(item.current) }}
            </span>
          </template>
          
          <template v-slot:item.days31to60="{ item }">
            <span :class="item.days31to60 > 0 ? 'text-warning' : ''">
              {{ formatCurrency(item.days31to60) }}
            </span>
          </template>
          
          <template v-slot:item.days61to90="{ item }">
            <span :class="item.days61to90 > 0 ? 'text-orange' : ''">
              {{ formatCurrency(item.days61to90) }}
            </span>
          </template>
          
          <template v-slot:item.over90="{ item }">
            <span :class="item.over90 > 0 ? 'text-error' : ''">
              {{ formatCurrency(item.over90) }}
            </span>
          </template>
          
          <template v-slot:item.total="{ item }">
            <strong>{{ formatCurrency(item.total) }}</strong>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn icon small @click="viewCustomerDetail(item)">
              <v-icon small>mdi-eye</v-icon>
            </v-btn>
            <v-btn icon small @click="contactCustomer(item)" :disabled="item.total <= 0">
              <v-icon small>mdi-email</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Customer Detail Dialog -->
    <v-dialog v-model="detailDialog" max-width="800px">
      <v-card>
        <v-card-title>{{ selectedCustomer?.customer_name }} - Invoice Details</v-card-title>
        <v-card-text>
          <v-data-table
            :headers="invoiceHeaders"
            :items="customerInvoices"
            :items-per-page="5"
          >
            <template v-slot:item.days_overdue="{ item }">
              <v-chip :color="getOverdueColor(item.days_overdue)" small>
                {{ item.days_overdue > 0 ? `${item.days_overdue} days` : 'Current' }}
              </v-chip>
            </template>
            
            <template v-slot:item.balance="{ item }">
              {{ formatCurrency(item.balance) }}
            </template>
          </v-data-table>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="detailDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'

export default {
  name: 'AgingReport',
  components: { ResponsiveContainer },
  
  data: () => ({
    loading: false,
    detailDialog: false,
    selectedCustomer: null,
    agingData: [
      {
        customer_id: '1',
        customer_name: 'ABC Corporation',
        current: 5000,
        days31to60: 2000,
        days61to90: 0,
        over90: 1000,
        total: 8000
      },
      {
        customer_id: '2',
        customer_name: 'XYZ Company',
        current: 3000,
        days31to60: 0,
        days61to90: 1500,
        over90: 0,
        total: 4500
      }
    ],
    customerInvoices: [
      {
        invoice_number: 'INV-1001',
        invoice_date: '2024-01-15',
        due_date: '2024-02-14',
        balance: 5000,
        days_overdue: 0
      },
      {
        invoice_number: 'INV-1002',
        invoice_date: '2023-12-15',
        due_date: '2024-01-14',
        balance: 2000,
        days_overdue: 45
      }
    ],
    headers: [
      { title: 'Customer', key: 'customer_name' },
      { title: 'Current', key: 'current' },
      { title: '31-60 Days', key: 'days31to60' },
      { title: '61-90 Days', key: 'days61to90' },
      { title: 'Over 90 Days', key: 'over90' },
      { title: 'Total', key: 'total' },
      { title: 'Actions', key: 'actions', sortable: false }
    ],
    invoiceHeaders: [
      { title: 'Invoice #', key: 'invoice_number' },
      { title: 'Invoice Date', key: 'invoice_date' },
      { title: 'Due Date', key: 'due_date' },
      { title: 'Balance', key: 'balance' },
      { title: 'Days Overdue', key: 'days_overdue' }
    ]
  }),

  computed: {
    summary() {
      return this.agingData.reduce((sum, item) => ({
        current: sum.current + item.current,
        days31to60: sum.days31to60 + item.days31to60,
        days61to90: sum.days61to90 + item.days61to90,
        over90: sum.over90 + item.over90
      }), { current: 0, days31to60: 0, days61to90: 0, over90: 0 })
    }
  },

  methods: {
    refreshReport() {
      this.loading = true
      setTimeout(() => {
        this.loading = false
      }, 1000)
    },

    viewCustomerDetail(customer) {
      this.selectedCustomer = customer
      this.detailDialog = true
    },

    contactCustomer(customer) {
      console.log('Contact customer:', customer.customer_name)
    },

    getOverdueColor(days) {
      if (days <= 0) return 'success'
      if (days <= 30) return 'warning'
      if (days <= 60) return 'orange'
      return 'error'
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