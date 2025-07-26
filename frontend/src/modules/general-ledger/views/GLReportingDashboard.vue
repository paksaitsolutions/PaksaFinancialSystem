<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">GL Reporting Dashboard</h1>
        
        <v-row class="mb-4">
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedPeriod"
              :items="periods"
              label="Reporting Period"
              @update:model-value="loadReports"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedCurrency"
              :items="currencies"
              label="Currency"
              @update:model-value="loadReports"
            />
          </v-col>
          <v-col cols="12" md="6">
            <v-btn @click="exportReports" color="primary" class="mr-2">
              <v-icon left>mdi-download</v-icon>
              Export Reports
            </v-btn>
            <v-btn @click="scheduleReport" color="secondary">
              <v-icon left>mdi-calendar</v-icon>
              Schedule Report
            </v-btn>
          </v-col>
        </v-row>
        
        <v-tabs v-model="activeTab">
          <v-tab value="overview">Overview</v-tab>
          <v-tab value="balance-sheet">Balance Sheet</v-tab>
          <v-tab value="income-statement">Income Statement</v-tab>
          <v-tab value="cash-flow">Cash Flow</v-tab>
          <v-tab value="trial-balance">Trial Balance</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="overview">
            <v-row>
              <v-col cols="12" md="3" v-for="metric in keyMetrics" :key="metric.title">
                <v-card>
                  <v-card-text class="text-center">
                    <div class="text-h6">{{ metric.title }}</div>
                    <div class="text-h4" :class="metric.color">
                      {{ formatCurrency(metric.value) }}
                    </div>
                    <div class="text-caption">
                      <v-icon :color="metric.trend === 'up' ? 'success' : 'error'" small>
                        {{ metric.trend === 'up' ? 'mdi-trending-up' : 'mdi-trending-down' }}
                      </v-icon>
                      {{ metric.change }}% vs last period
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            
            <v-row class="mt-4">
              <v-col cols="12" md="6">
                <v-card>
                  <v-card-title>Account Balance Trends</v-card-title>
                  <v-card-text>
                    <account-balance-chart :data="balanceTrendData" />
                  </v-card-text>
                </v-card>
              </v-col>
              <v-col cols="12" md="6">
                <v-card>
                  <v-card-title>Account Type Distribution</v-card-title>
                  <v-card-text>
                    <account-distribution-chart :data="distributionData" />
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-window-item>
          
          <v-window-item value="balance-sheet">
            <v-card>
              <v-card-title>Balance Sheet</v-card-title>
              <v-card-text>
                <balance-sheet-report
                  :data="balanceSheetData"
                  :period="selectedPeriod"
                  :loading="loadingReports"
                />
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <v-window-item value="income-statement">
            <v-card>
              <v-card-title>Income Statement</v-card-title>
              <v-card-text>
                <income-statement-report
                  :data="incomeStatementData"
                  :period="selectedPeriod"
                  :loading="loadingReports"
                />
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <v-window-item value="cash-flow">
            <v-card>
              <v-card-title>Cash Flow Statement</v-card-title>
              <v-card-text>
                <cash-flow-report
                  :data="cashFlowData"
                  :period="selectedPeriod"
                  :loading="loadingReports"
                />
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <v-window-item value="trial-balance">
            <v-card>
              <v-card-title>Trial Balance</v-card-title>
              <v-card-text>
                <trial-balance-report
                  :data="trialBalanceData"
                  :period="selectedPeriod"
                  :loading="loadingReports"
                />
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
    
    <!-- Export Dialog -->
    <export-dialog
      v-model="showExportDialog"
      :reports="availableReports"
      @export="handleExport"
    />
    
    <!-- Schedule Dialog -->
    <schedule-report-dialog
      v-model="showScheduleDialog"
      @schedule="handleSchedule"
    />
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AccountBalanceChart from '../components/AccountBalanceChart.vue'
import AccountDistributionChart from '../components/AccountDistributionChart.vue'
import BalanceSheetReport from '../components/reports/BalanceSheetReport.vue'
import IncomeStatementReport from '../components/reports/IncomeStatementReport.vue'
import CashFlowReport from '../components/reports/CashFlowReport.vue'
import TrialBalanceReport from '../components/reports/TrialBalanceReport.vue'
import ExportDialog from '../components/ExportDialog.vue'
import ScheduleReportDialog from '../components/ScheduleReportDialog.vue'
import { useGLReportingStore } from '../store/gl-reporting'

const glReportingStore = useGLReportingStore()
const activeTab = ref('overview')
const selectedPeriod = ref('2023-12')
const selectedCurrency = ref('USD')
const loadingReports = ref(false)
const showExportDialog = ref(false)
const showScheduleDialog = ref(false)

const periods = [
  { title: 'December 2023', value: '2023-12' },
  { title: 'November 2023', value: '2023-11' },
  { title: 'October 2023', value: '2023-10' },
  { title: 'Q4 2023', value: '2023-Q4' },
  { title: 'YTD 2023', value: '2023-YTD' }
]

const currencies = ['USD', 'EUR', 'GBP', 'CAD']

const availableReports = [
  'Balance Sheet',
  'Income Statement',
  'Cash Flow Statement',
  'Trial Balance',
  'General Ledger Detail'
]

const keyMetrics = ref([
  {
    title: 'Total Assets',
    value: 2450000,
    change: 5.2,
    trend: 'up',
    color: 'text-success'
  },
  {
    title: 'Total Liabilities',
    value: 980000,
    change: -2.1,
    trend: 'down',
    color: 'text-info'
  },
  {
    title: 'Net Income',
    value: 185000,
    change: 12.5,
    trend: 'up',
    color: 'text-success'
  },
  {
    title: 'Cash Position',
    value: 425000,
    change: 8.3,
    trend: 'up',
    color: 'text-primary'
  }
])

const balanceTrendData = ref([])
const distributionData = ref([])
const balanceSheetData = ref({})
const incomeStatementData = ref({})
const cashFlowData = ref({})
const trialBalanceData = ref([])

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: selectedCurrency.value
  }).format(amount || 0)
}

const loadReports = async () => {
  loadingReports.value = true
  try {
    const [
      balanceSheet,
      incomeStatement,
      cashFlow,
      trialBalance,
      trends,
      distribution
    ] = await Promise.all([
      glReportingStore.getBalanceSheet(selectedPeriod.value),
      glReportingStore.getIncomeStatement(selectedPeriod.value),
      glReportingStore.getCashFlowStatement(selectedPeriod.value),
      glReportingStore.getTrialBalance(selectedPeriod.value),
      glReportingStore.getBalanceTrends(selectedPeriod.value),
      glReportingStore.getAccountDistribution(selectedPeriod.value)
    ])
    
    balanceSheetData.value = balanceSheet
    incomeStatementData.value = incomeStatement
    cashFlowData.value = cashFlow
    trialBalanceData.value = trialBalance
    balanceTrendData.value = trends
    distributionData.value = distribution
  } finally {
    loadingReports.value = false
  }
}

const exportReports = () => {
  showExportDialog.value = true
}

const scheduleReport = () => {
  showScheduleDialog.value = true
}

const handleExport = async (exportOptions) => {
  await glReportingStore.exportReports(exportOptions)
  showExportDialog.value = false
}

const handleSchedule = async (scheduleOptions) => {
  await glReportingStore.scheduleReport(scheduleOptions)
  showScheduleDialog.value = false
}

onMounted(() => {
  loadReports()
})
</script>