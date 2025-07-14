<template>
  <div class="dashboard">
    <v-container fluid>
      <!-- Header -->
      <v-row class="mb-4">
        <v-col cols="12">
          <h1 class="text-h4 font-weight-bold">Financial Dashboard</h1>
          <p class="text-subtitle-1 text-grey-600">
            Welcome to Paksa Financial System
          </p>
        </v-col>
      </v-row>

      <!-- Key Metrics Cards -->
      <v-row class="mb-6">
        <v-col cols="12" sm="6" md="3">
          <MetricCard
            title="Total Assets"
            :value="formatCurrency(metrics.totalAssets)"
            icon="mdi-bank"
            color="blue"
            :trend="metrics.assetsTrend"
          />
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <MetricCard
            title="Total Liabilities"
            :value="formatCurrency(metrics.totalLiabilities)"
            icon="mdi-credit-card"
            color="red"
            :trend="metrics.liabilitiesTrend"
          />
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <MetricCard
            title="Monthly Revenue"
            :value="formatCurrency(metrics.monthlyRevenue)"
            icon="mdi-trending-up"
            color="green"
            :trend="metrics.revenueTrend"
          />
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <MetricCard
            title="Monthly Expenses"
            :value="formatCurrency(metrics.monthlyExpenses)"
            icon="mdi-trending-down"
            color="orange"
            :trend="metrics.expensesTrend"
          />
        </v-col>
      </v-row>

      <!-- Charts Row -->
      <v-row class="mb-6">
        <v-col cols="12" md="8">
          <v-card>
            <v-card-title>Cash Flow Trend</v-card-title>
            <v-card-text>
              <CashFlowChart :data="cashFlowData" />
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Account Balance Distribution</v-card-title>
            <v-card-text>
              <AccountBalanceChart :data="balanceData" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Recent Transactions and Quick Actions -->
      <v-row>
        <v-col cols="12" md="8">
          <v-card>
            <v-card-title class="d-flex justify-space-between">
              <span>Recent Transactions</span>
              <v-btn variant="text" size="small" to="/gl/journal-entries">View All</v-btn>
            </v-card-title>
            <v-card-text>
              <RecentTransactions :transactions="recentTransactions" />
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Quick Actions</v-card-title>
            <v-card-text>
              <QuickActions />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import MetricCard from '@/components/common/MetricCard.vue'
import CashFlowChart from '@/components/charts/CashFlowChart.vue'
import AccountBalanceChart from '@/components/charts/AccountBalanceChart.vue'
import RecentTransactions from '@/components/common/RecentTransactions.vue'
import QuickActions from '@/components/common/QuickActions.vue'

const metrics = ref({
  totalAssets: 1250000,
  totalLiabilities: 450000,
  monthlyRevenue: 125000,
  monthlyExpenses: 85000,
  assetsTrend: 5.2,
  liabilitiesTrend: -2.1,
  revenueTrend: 8.5,
  expensesTrend: 3.2
})

const cashFlowData = ref([
  { month: 'Jan', inflow: 120000, outflow: 80000 },
  { month: 'Feb', inflow: 135000, outflow: 85000 },
  { month: 'Mar', inflow: 125000, outflow: 90000 },
  { month: 'Apr', inflow: 140000, outflow: 95000 },
  { month: 'May', inflow: 155000, outflow: 100000 },
  { month: 'Jun', inflow: 145000, outflow: 85000 }
])

const balanceData = ref([
  { label: 'Cash', value: 250000, color: '#2196F3' },
  { label: 'Accounts Receivable', value: 180000, color: '#4CAF50' },
  { label: 'Inventory', value: 320000, color: '#FF9800' },
  { label: 'Fixed Assets', value: 500000, color: '#9C27B0' }
])

const recentTransactions = ref([
  {
    id: 1,
    date: '2024-01-15',
    description: 'Office Supplies Purchase',
    amount: -1250.00,
    account: 'Office Expenses'
  },
  {
    id: 2,
    date: '2024-01-14',
    description: 'Client Payment Received',
    amount: 5000.00,
    account: 'Accounts Receivable'
  },
  {
    id: 3,
    date: '2024-01-13',
    description: 'Rent Payment',
    amount: -2500.00,
    account: 'Rent Expense'
  }
])

onMounted(async () => {
  // Load dashboard data
  await loadDashboardData()
})

const loadDashboardData = async () => {
  // In a real app, this would fetch data from the API
  console.log('Loading dashboard data...')
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f5f5f5;
}
</style>