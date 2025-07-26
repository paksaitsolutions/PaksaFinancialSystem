<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1>General Ledger Reporting Dashboard</h1>
      </v-col>
    </v-row>
    
    <!-- Quick Stats -->
    <v-row>
      <v-col cols="12" md="3" v-for="stat in quickStats" :key="stat.title">
        <v-card>
          <v-card-text>
            <div class="d-flex align-center">
              <v-icon :color="stat.color" size="40" class="mr-3">
                {{ stat.icon }}
              </v-icon>
              <div>
                <div class="text-h6">${{ formatCurrency(stat.value) }}</div>
                <div class="text-caption">{{ stat.title }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Reports Grid -->
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-file-document</v-icon>
            Financial Statements
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item 
                v-for="statement in financialStatements" 
                :key="statement.name"
                @click="generateReport(statement.type)"
              >
                <template v-slot:prepend>
                  <v-icon>{{ statement.icon }}</v-icon>
                </template>
                <v-list-item-title>{{ statement.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ statement.description }}</v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn icon small>
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-chart-line</v-icon>
            Account Analysis
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item 
                v-for="analysis in accountAnalysis" 
                :key="analysis.name"
                @click="generateReport(analysis.type)"
              >
                <template v-slot:prepend>
                  <v-icon>{{ analysis.icon }}</v-icon>
                </template>
                <v-list-item-title>{{ analysis.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ analysis.description }}</v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn icon small>
                    <v-icon>mdi-download</v-icon>
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Trial Balance Preview -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-scale-balance</v-icon>
            Trial Balance Summary
            <v-spacer />
            <v-btn color="primary" @click="viewFullTrialBalance">
              View Full Report
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="trialBalanceHeaders"
              :items="trialBalancePreview"
              :items-per-page="5"
              class="elevation-1"
            >
              <template v-slot:item.debit="{ item }">
                <span v-if="item.debit > 0">${{ formatCurrency(item.debit) }}</span>
              </template>
              <template v-slot:item.credit="{ item }">
                <span v-if="item.credit > 0">${{ formatCurrency(item.credit) }}</span>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Account Activity Chart -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon left>mdi-chart-bar</v-icon>
            Account Activity Trends
          </v-card-title>
          <v-card-text>
            <div class="chart-container" style="height: 300px;">
              <!-- Chart would go here -->
              <div class="d-flex align-center justify-center" style="height: 100%;">
                <v-icon size="100" color="grey lighten-2">mdi-chart-line</v-icon>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'GLReportingDashboard',
  
  data: () => ({
    quickStats: [
      {
        title: 'Total Assets',
        value: 2500000,
        icon: 'mdi-bank',
        color: 'success'
      },
      {
        title: 'Total Liabilities',
        value: 1200000,
        icon: 'mdi-credit-card',
        color: 'warning'
      },
      {
        title: 'Total Equity',
        value: 1300000,
        icon: 'mdi-trending-up',
        color: 'info'
      },
      {
        title: 'Net Income',
        value: 150000,
        icon: 'mdi-cash',
        color: 'success'
      }
    ],
    
    financialStatements: [
      {
        name: 'Balance Sheet',
        description: 'Assets, liabilities, and equity',
        icon: 'mdi-scale-balance',
        type: 'balance_sheet'
      },
      {
        name: 'Income Statement',
        description: 'Revenue and expenses',
        icon: 'mdi-chart-line',
        type: 'income_statement'
      },
      {
        name: 'Cash Flow Statement',
        description: 'Cash inflows and outflows',
        icon: 'mdi-cash-flow',
        type: 'cash_flow'
      },
      {
        name: 'Statement of Equity',
        description: 'Changes in equity',
        icon: 'mdi-trending-up',
        type: 'equity_statement'
      }
    ],
    
    accountAnalysis: [
      {
        name: 'Trial Balance',
        description: 'All account balances',
        icon: 'mdi-scale-balance',
        type: 'trial_balance'
      },
      {
        name: 'General Ledger',
        description: 'Detailed account transactions',
        icon: 'mdi-book-open',
        type: 'general_ledger'
      },
      {
        name: 'Account Activity',
        description: 'Transaction history by account',
        icon: 'mdi-history',
        type: 'account_activity'
      },
      {
        name: 'Journal Entries',
        description: 'All journal entry details',
        icon: 'mdi-notebook',
        type: 'journal_entries'
      }
    ],
    
    trialBalanceHeaders: [
      { text: 'Account Code', value: 'code' },
      { text: 'Account Name', value: 'name' },
      { text: 'Debit', value: 'debit', align: 'end' },
      { text: 'Credit', value: 'credit', align: 'end' }
    ],
    
    trialBalancePreview: [
      { code: '1000', name: 'Cash', debit: 50000, credit: 0 },
      { code: '1200', name: 'Accounts Receivable', debit: 75000, credit: 0 },
      { code: '2000', name: 'Accounts Payable', debit: 0, credit: 25000 },
      { code: '3000', name: 'Common Stock', debit: 0, credit: 100000 },
      { code: '4000', name: 'Sales Revenue', debit: 0, credit: 150000 }
    ]
  }),
  
  methods: {
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US').format(amount)
    },
    
    generateReport(reportType) {
      console.log('Generating report:', reportType)
    },
    
    viewFullTrialBalance() {
      this.$router.push('/general-ledger/trial-balance')
    }
  }
}
</script>

<style scoped>
.chart-container {
  background-color: #f5f5f5;
  border-radius: 4px;
}
</style>