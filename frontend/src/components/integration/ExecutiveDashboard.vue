<template>
  <div class="executive-dashboard">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-4">Executive Dashboard</h1>
        </v-col>
      </v-row>
      
      <!-- KPI Cards -->
      <v-row>
        <v-col cols="12" md="3" v-for="kpi in kpiCards" :key="kpi.title">
          <v-card>
            <v-card-text>
              <div class="text-overline mb-1">{{ kpi.title }}</div>
              <div class="text-h5 font-weight-bold" :class="kpi.color">
                {{ formatCurrency(kpi.value) }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <!-- Module Status -->
      <v-row class="mt-4">
        <v-col cols="12">
          <v-card>
            <v-card-title>Module Integration Status</v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="3" v-for="module in moduleStatus" :key="module.name">
                  <v-card outlined>
                    <v-card-text class="text-center">
                      <v-icon :color="module.color" size="48">{{ module.icon }}</v-icon>
                      <div class="text-h6 mt-2">{{ module.name }}</div>
                      <v-chip :color="module.color" small>{{ module.status }}</v-chip>
                    </v-card-text>
                  </v-card>
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
import { ref, onMounted } from 'vue'
import { useIntegrationStore } from '@/stores/integration'

export default {
  name: 'ExecutiveDashboard',
  setup() {
    const integrationStore = useIntegrationStore()
    const kpiCards = ref([])
    const moduleStatus = ref([])
    
    const formatCurrency = (value) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value || 0)
    }
    
    const loadDashboardData = async () => {
      try {
        const today = new Date()
        const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
        
        const data = await integrationStore.getExecutiveDashboard(
          1, 
          startOfMonth.toISOString().split('T')[0],
          today.toISOString().split('T')[0]
        )
        
        kpiCards.value = [
          {
            title: 'Net Cash Flow',
            value: data.executive_summary?.net_cash_flow || 0,
            color: (data.executive_summary?.net_cash_flow || 0) > 0 ? 'text-success' : 'text-error'
          },
          {
            title: 'Cash Position',
            value: data.executive_summary?.total_cash_position || 0,
            color: 'text-primary'
          },
          {
            title: 'AR Balance',
            value: data.executive_summary?.accounts_receivable_balance || 0,
            color: 'text-warning'
          },
          {
            title: 'AP Balance',
            value: data.executive_summary?.accounts_payable_balance || 0,
            color: 'text-info'
          }
        ]
        
        moduleStatus.value = [
          { name: 'Accounts Payable', status: 'Integrated', color: 'success', icon: 'mdi-credit-card-outline' },
          { name: 'Accounts Receivable', status: 'Integrated', color: 'success', icon: 'mdi-receipt' },
          { name: 'Cash Management', status: 'Integrated', color: 'success', icon: 'mdi-bank' },
          { name: 'Budget Management', status: 'Integrated', color: 'success', icon: 'mdi-chart-line' }
        ]
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        // Set default values on error
        kpiCards.value = [
          { title: 'Net Cash Flow', value: 0, color: 'text-primary' },
          { title: 'Cash Position', value: 0, color: 'text-primary' },
          { title: 'AR Balance', value: 0, color: 'text-primary' },
          { title: 'AP Balance', value: 0, color: 'text-primary' }
        ]
      }
    }
    
    onMounted(() => {
      loadDashboardData()
    })
    
    return {
      kpiCards,
      moduleStatus,
      formatCurrency
    }
  }
}
</script>