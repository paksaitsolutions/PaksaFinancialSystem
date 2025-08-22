<template>
  <v-container fluid class="reports-container">
    <v-card class="reports-card" elevation="2">
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-3" size="28" color="primary">mdi-chart-line</v-icon>
        <h1 class="text-h4 font-weight-bold">Reports</h1>
        <v-spacer />
        <v-btn color="primary" @click="showReportBuilder = true">
          <v-icon start>mdi-plus</v-icon>
          New Report
        </v-btn>
      </v-card-title>

      <v-card-text>
        <!-- Quick Actions -->
        <div class="mb-6">
          <h2 class="text-h6 mb-3">Quick Actions</h2>
          <v-row>
            <v-col v-for="action in quickActions" :key="action.id" cols="12" sm="6" md="3">
              <v-card class="action-card" elevation="1" @click="navigateToReport(action)">
                <v-card-text class="text-center pa-4">
                  <v-icon :color="action.color" size="32" class="mb-2">{{ action.icon }}</v-icon>
                  <div class="text-subtitle-2 font-weight-bold">{{ action.name }}</div>
                  <div class="text-caption text-medium-emphasis">{{ action.description }}</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>

        <!-- Report Categories -->
        <div v-for="category in reportCategories" :key="category.id" class="mb-6">
          <h2 class="text-h6 mb-3">{{ category.name }}</h2>
          <v-row>
            <v-col v-for="report in category.reports" :key="report.id" cols="12" sm="6" md="4">
              <v-card class="report-card" elevation="1" @click="navigateToReport(report)">
                <v-card-text class="pa-4">
                  <div class="d-flex align-center mb-2">
                    <v-icon :color="report.color || 'primary'" size="24" class="mr-2">{{ report.icon }}</v-icon>
                    <div class="text-subtitle-2 font-weight-bold">{{ report.name }}</div>
                  </div>
                  <div class="text-caption text-medium-emphasis">{{ report.description }}</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>
      </v-card-text>
    </v-card>

    <!-- Report Builder Dialog -->
    <v-dialog v-model="showReportBuilder" max-width="800px">
      <v-card>
        <v-card-title>
          <span class="text-h5">Report Builder</span>
        </v-card-title>
        <v-card-text>
          <p>Report builder functionality coming soon...</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="showReportBuilder = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showReportBuilder = ref(false)

const quickActions = ref([
  {
    id: 'trial-balance',
    name: 'Trial Balance',
    description: 'Account balances summary',
    icon: 'mdi-scale-balance',
    color: 'primary',
    route: '/gl/trial-balance'
  },
  {
    id: 'income-statement',
    name: 'Income Statement',
    description: 'Profit and loss report',
    icon: 'mdi-chart-line',
    color: 'success',
    route: '/reports/income-statement'
  },
  {
    id: 'balance-sheet',
    name: 'Balance Sheet',
    description: 'Financial position',
    icon: 'mdi-file-document',
    color: 'info',
    route: '/reports/balance-sheet'
  },
  {
    id: 'cash-flow',
    name: 'Cash Flow',
    description: 'Cash movement analysis',
    icon: 'mdi-cash-flow',
    color: 'warning',
    route: '/reports/cash-flow'
  }
])

const reportCategories = ref([
  {
    id: 'financial',
    name: 'Financial Statements',
    reports: [
      {
        id: 'balance-sheet',
        name: 'Balance Sheet',
        description: 'Assets, liabilities, and equity',
        icon: 'mdi-file-document',
        color: 'primary',
        route: '/reports/balance-sheet'
      },
      {
        id: 'income-statement',
        name: 'Income Statement',
        description: 'Revenue and expenses',
        icon: 'mdi-chart-line',
        color: 'success',
        route: '/reports/income-statement'
      }
    ]
  }
])

const navigateToReport = (report: any) => {
  console.log('Navigating to report:', report.route)
  router.push(report.route).catch(err => {
    console.error('Navigation error:', err)
    router.push('/dashboard')
  })
}
</script>

<style scoped>
.reports-container {
  background: #fafafa;
  min-height: 100vh;
  padding: 16px;
}

.reports-card {
  border-radius: 12px;
}

.action-card,
.report-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 8px;
  height: 100%;
}

.action-card:hover,
.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>