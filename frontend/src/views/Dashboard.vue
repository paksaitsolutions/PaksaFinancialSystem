<template>
  <div class="dashboard">
    <ResponsiveContainer>
      <v-row>
        <v-col cols="12">
          <h1 :class="titleClass">Financial Dashboard</h1>
        </v-col>
      </v-row>

      <!-- Key Metrics Cards -->
      <ResponsiveGrid
        :items="metricsCards"
        :columns="{ mobile: 1, tablet: 2, desktop: 4 }"
        class="mb-6"
      >
        <template #default="{ item }">
          <v-card :color="item.color" dark class="metric-card">
            <v-card-text>
              <div :class="metricContentClass">
                <v-icon :size="iconSize" class="mr-3">{{ item.icon }}</v-icon>
                <div>
                  <div :class="metricValueClass">{{ formatCurrency(item.value) }}</div>
                  <div :class="metricLabelClass">{{ item.label }}</div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </template>
      </ResponsiveGrid>

      <!-- Charts Row -->
      <v-row class="mt-4">
        <v-col cols="12" :md="isMobile ? 12 : 8">
          <v-card class="chart-card">
            <v-card-title>Revenue Trend</v-card-title>
            <v-card-text>
              <div :class="chartPlaceholderClass">
                <v-icon :size="chartIconSize" color="grey lighten-2">mdi-chart-line</v-icon>
                <p class="text-center mt-4">Revenue trend chart will be displayed here</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" :md="isMobile ? 12 : 4">
          <v-card class="chart-card">
            <v-card-title>Expense Breakdown</v-card-title>
            <v-card-text>
              <div :class="chartPlaceholderClass">
                <v-icon :size="chartIconSize" color="grey lighten-2">mdi-chart-pie</v-icon>
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
              <ResponsiveGrid
                :items="quickActions"
                :columns="{ mobile: 1, tablet: 2, desktop: 4 }"
              >
                <template #default="{ item }">
                  <v-btn 
                    :color="item.color" 
                    block 
                    :size="buttonSize"
                    @click="$router.push(item.route)"
                    class="quick-action-btn"
                  >
                    <v-icon :left="!isMobile">{{ item.icon }}</v-icon>
                    <span v-if="!isMobile || true">{{ item.label }}</span>
                  </v-btn>
                </template>
              </ResponsiveGrid>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </ResponsiveContainer>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useResponsive } from '@/composables/useResponsive'
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import ResponsiveGrid from '@/components/layout/ResponsiveGrid.vue'

export default {
  name: 'Dashboard',
  components: {
    ResponsiveContainer,
    ResponsiveGrid
  },
  setup() {
    const { isMobile, isTablet } = useResponsive()

    const titleClass = computed(() => ({
      'text-h4': !isMobile.value,
      'text-h5': isMobile.value,
      'mb-6': !isMobile.value,
      'mb-4': isMobile.value
    }))

    const metricContentClass = computed(() => ({
      'd-flex': true,
      'align-center': !isMobile.value,
      'flex-column': isMobile.value,
      'text-center': isMobile.value
    }))

    const metricValueClass = computed(() => ({
      'text-h6': !isMobile.value,
      'text-h5': isMobile.value
    }))

    const metricLabelClass = computed(() => ({
      'text-caption': !isMobile.value,
      'text-body-2': isMobile.value
    }))

    const iconSize = computed(() => isMobile.value ? 32 : 40)
    const chartIconSize = computed(() => isMobile.value ? 60 : 100)
    const buttonSize = computed(() => isMobile.value ? 'large' : 'default')

    const chartPlaceholderClass = computed(() => ({
      'chart-placeholder': true,
      'chart-placeholder--mobile': isMobile.value
    }))

    return {
      isMobile,
      isTablet,
      titleClass,
      metricContentClass,
      metricValueClass,
      metricLabelClass,
      iconSize,
      chartIconSize,
      buttonSize,
      chartPlaceholderClass
    }
  },
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

  computed: {
    metricsCards() {
      return [
        { icon: 'mdi-cash', value: this.metrics.totalRevenue, label: 'Total Revenue', color: 'primary' },
        { icon: 'mdi-trending-up', value: this.metrics.netIncome, label: 'Net Income', color: 'success' },
        { icon: 'mdi-account-cash', value: this.metrics.accountsReceivable, label: 'Accounts Receivable', color: 'warning' },
        { icon: 'mdi-credit-card', value: this.metrics.accountsPayable, label: 'Accounts Payable', color: 'error' }
      ]
    },
    quickActions() {
      return [
        { icon: 'mdi-book-open', label: 'New Journal Entry', color: 'primary', route: '/general-ledger/journal-entries' },
        { icon: 'mdi-receipt', label: 'Create Invoice', color: 'success', route: '/accounts-receivable' },
        { icon: 'mdi-credit-card-outline', label: 'Record Payment', color: 'warning', route: '/accounts-payable' },
        { icon: 'mdi-chart-box', label: 'View Reports', color: 'info', route: '/reports' }
      ]
    }
  },

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

.metric-card {
  height: 100%;
  min-height: 120px;
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

.chart-placeholder--mobile {
  height: 150px;
}

.chart-card {
  height: 100%;
}

.quick-action-btn {
  height: 56px;
  text-transform: none;
}

@media (max-width: 600px) {
  .dashboard {
    padding: 16px;
  }
  
  .metric-card {
    min-height: 100px;
  }
  
  .quick-action-btn {
    height: 48px;
    font-size: 14px;
  }
}

@media (max-width: 960px) {
  .chart-placeholder {
    height: 180px;
  }
}
</style>