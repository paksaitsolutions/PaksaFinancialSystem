<template>
  <div class="dashboard">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-6">Financial Dashboard</h1>
        </v-col>
      </v-row>

      <!-- Key Metrics Cards -->
      <v-row>
        <v-col cols="12" md="3">
          <v-card color="primary" dark>
            <v-card-text>
              <div class="d-flex align-center">
                <v-icon size="40" class="mr-3">mdi-cash</v-icon>
                <div>
                  <div class="text-h6">{{ formatCurrency(metrics.totalRevenue) }}</div>
                  <div class="text-caption">Total Revenue</div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="3">
          <v-card color="success" dark>
            <v-card-text>
              <div class="d-flex align-center">
                <v-icon size="40" class="mr-3">mdi-trending-up</v-icon>
                <div>
                  <div class="text-h6">{{ formatCurrency(metrics.netIncome) }}</div>
                  <div class="text-caption">Net Income</div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="3">
          <v-card color="warning" dark>
            <v-card-text>
              <div class="d-flex align-center">
                <v-icon size="40" class="mr-3">mdi-account-cash</v-icon>
                <div>
                  <div class="text-h6">{{ formatCurrency(metrics.accountsReceivable) }}</div>
                  <div class="text-caption">Accounts Receivable</div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="3">
          <v-card color="error" dark>
            <v-card-text>
              <div class="d-flex align-center">
                <v-icon size="40" class="mr-3">mdi-credit-card</v-icon>
                <div>
                  <div class="text-h6">{{ formatCurrency(metrics.accountsPayable) }}</div>
                  <div class="text-caption">Accounts Payable</div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Charts Row -->
      <v-row class="mt-4">
        <v-col cols="12" md="8">
          <v-card>
            <v-card-title>Revenue Trend</v-card-title>
            <v-card-text>
              <div class="chart-placeholder">
                <v-icon size="100" color="grey lighten-2">mdi-chart-line</v-icon>
                <p class="text-center mt-4">Revenue trend chart will be displayed here</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Expense Breakdown</v-card-title>
            <v-card-text>
              <div class="chart-placeholder">
                <v-icon size="80" color="grey lighten-2">mdi-chart-pie</v-icon>
                <p class="text-center mt-4">Expense breakdown chart</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Recent Transactions -->
      <v-row class="mt-4">
        <v-col cols="12">
          <v-card>
            <v-card-title>Recent Transactions</v-card-title>
            <v-card-text>
              <v-data-table
                :headers="transactionHeaders"
                :items="recentTransactions"
                :items-per-page="5"
                hide-default-footer
              >
                <template v-slot:item.amount="{ item }">
                  <span :class="item.type === 'credit' ? 'text-success' : 'text-error'">
                    {{ formatCurrency(item.amount) }}
                  </span>
                </template>
                <template v-slot:item.date="{ item }">
                  {{ formatDate(item.date) }}
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Quick Actions -->
      <v-row class="mt-4">
        <v-col cols="12">
          <v-card>
            <v-card-title>Quick Actions</v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="3">
                  <v-btn color="primary" block @click="$router.push('/general-ledger/journal-entries')">
                    <v-icon left>mdi-book-open</v-icon>
                    New Journal Entry
                  </v-btn>
                </v-col>
                <v-col cols="12" md="3">
                  <v-btn color="success" block @click="$router.push('/accounts-receivable')">
                    <v-icon left>mdi-receipt</v-icon>
                    Create Invoice
                  </v-btn>
                </v-col>
                <v-col cols="12" md="3">
                  <v-btn color="warning" block @click="$router.push('/accounts-payable')">
                    <v-icon left>mdi-credit-card-outline</v-icon>
                    Record Payment
                  </v-btn>
                </v-col>
                <v-col cols="12" md="3">
                  <v-btn color="info" block @click="$router.push('/reports')">
                    <v-icon left>mdi-chart-box</v-icon>
                    View Reports
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
export default {
  name: 'Dashboard',
  data: () => ({
    metrics: {
      totalRevenue: 1250000,
      netIncome: 185000,
      accountsReceivable: 325000,
      accountsPayable: 145000
    },
    transactionHeaders: [
      { title: 'Date', key: 'date' },
      { title: 'Description', key: 'description' },
      { title: 'Account', key: 'account' },
      { title: 'Amount', key: 'amount' }
    ],
    recentTransactions: [
      { date: '2024-01-15', description: 'Office Supplies', account: 'Office Expenses', amount: 250, type: 'debit' },
      { date: '2024-01-14', description: 'Client Payment', account: 'Accounts Receivable', amount: 5000, type: 'credit' },
      { date: '2024-01-13', description: 'Rent Payment', account: 'Rent Expense', amount: 2500, type: 'debit' },
      { date: '2024-01-12', description: 'Service Revenue', account: 'Revenue', amount: 7500, type: 'credit' },
      { date: '2024-01-11', description: 'Utility Bill', account: 'Utilities', amount: 450, type: 'debit' }
    ]
  }),

  methods: {
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    },

    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  background-color: #f5f5f5;
  border-radius: 8px;
}
</style>