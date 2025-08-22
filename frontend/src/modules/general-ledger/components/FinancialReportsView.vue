<template>
  <v-container fluid>
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-chart-line</v-icon>
        Financial Reports
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12" md="4" v-for="report in reports" :key="report.id">
            <v-card class="report-card" @click="generateReport(report)" :loading="report.loading">
              <v-card-title class="d-flex align-center">
                <v-icon :color="report.color" class="mr-2">{{ report.icon }}</v-icon>
                {{ report.name }}
              </v-card-title>
              <v-card-text>
                <p class="text-body-2">{{ report.description }}</p>
                <v-btn color="primary" size="small" :loading="report.loading">
                  Generate Report
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <!-- Report Results Dialog -->
        <v-dialog v-model="showReport" max-width="1200px">
          <v-card>
            <v-card-title class="d-flex align-center justify-space-between">
              {{ selectedReport?.name }}
              <v-btn icon @click="showReport = false">
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </v-card-title>
            <v-card-text>
              <div v-if="reportData" class="report-content">
                <v-data-table
                  :items="reportData"
                  :headers="reportHeaders"
                  class="elevation-1"
                  density="compact"
                >
                  <template #item.amount="{ item }">
                    {{ formatCurrency(item.amount) }}
                  </template>
                </v-data-table>
              </div>
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn color="primary" @click="exportReport">
                <v-icon start>mdi-download</v-icon>
                Export
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'

const showReport = ref(false)
const selectedReport = ref(null)
const reportData = ref(null)

const reports = ref([
  {
    id: 'balance-sheet',
    name: 'Balance Sheet',
    description: 'Assets, Liabilities, and Equity',
    icon: 'mdi-scale-balance',
    color: 'primary',
    loading: false
  },
  {
    id: 'income-statement',
    name: 'Income Statement',
    description: 'Revenue and Expenses',
    icon: 'mdi-trending-up',
    color: 'success',
    loading: false
  },
  {
    id: 'cash-flow',
    name: 'Cash Flow Statement',
    description: 'Cash Inflows and Outflows',
    icon: 'mdi-cash-flow',
    color: 'info',
    loading: false
  }
])

const reportHeaders = [
  { title: 'Account', key: 'account' },
  { title: 'Amount', key: 'amount', align: 'end' }
]

const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

const generateReport = async (report) => {
  report.loading = true
  selectedReport.value = report
  
  // Mock data - replace with API call
  setTimeout(() => {
    reportData.value = [
      { account: 'Cash and Cash Equivalents', amount: 50000 },
      { account: 'Accounts Receivable', amount: 25000 },
      { account: 'Total Assets', amount: 75000 }
    ]
    report.loading = false
    showReport.value = true
  }, 1000)
}

const exportReport = () => {
  // Export functionality
  console.log('Exporting report:', selectedReport.value?.name)
}
</script>

<style scoped>
.report-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.report-card:hover {
  transform: translateY(-2px);
}
</style>