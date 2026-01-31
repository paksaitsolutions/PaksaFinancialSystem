<template>
  <div class="integrated-reports">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-4">Integrated Reports</h1>
        </v-col>
      </v-row>
      
      <!-- Report Selection -->
      <v-row>
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Available Reports</v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item 
                  v-for="report in availableReports" 
                  :key="report.id"
                  @click="selectReport(report)"
                  :class="{ 'v-list-item--active': selectedReport?.id === report.id }"
                >
                  <v-list-item-content>
                    <v-list-item-title>{{ report.title }}</v-list-item-title>
                    <v-list-item-subtitle>{{ report.description }}</v-list-item-subtitle>
                  </v-list-item-content>
                  <v-list-item-action>
                    <v-icon>{{ report.icon }}</v-icon>
                  </v-list-item-action>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
        
        <!-- Report Content -->
        <v-col cols="12" md="8">
          <v-card v-if="selectedReport">
            <v-card-title>
              {{ selectedReport.title }}
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="generateReport" :loading="loading">
                Generate Report
              </v-btn>
            </v-card-title>
            
            <!-- Date Range Selector -->
            <v-card-text>
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model="dateRange.start"
                    label="Start Date"
                    type="date"
                    outlined
                  ></v-text-field>
                </v-col>
                <v-col cols="6">
                  <v-text-field
                    v-model="dateRange.end"
                    label="End Date"
                    type="date"
                    outlined
                  ></v-text-field>
                </v-col>
              </v-row>
              
              <!-- Report Content -->
              <div v-if="reportData">
                <!-- Executive Dashboard Report -->
                <div v-if="selectedReport.id === 'executive-dashboard'">
                  <v-row>
                    <v-col cols="12" md="6">
                      <v-card outlined>
                        <v-card-title class="text-h6">Financial Summary</v-card-title>
                        <v-card-text>
                          <v-simple-table>
                            <tbody>
                              <tr>
                                <td>Net Cash Flow</td>
                                <td class="text-right">{{ formatCurrency(reportData.executive_summary?.net_cash_flow) }}</td>
                              </tr>
                              <tr>
                                <td>Cash Position</td>
                                <td class="text-right">{{ formatCurrency(reportData.executive_summary?.total_cash_position) }}</td>
                              </tr>
                              <tr>
                                <td>AR Balance</td>
                                <td class="text-right">{{ formatCurrency(reportData.executive_summary?.accounts_receivable_balance) }}</td>
                              </tr>
                              <tr>
                                <td>AP Balance</td>
                                <td class="text-right">{{ formatCurrency(reportData.executive_summary?.accounts_payable_balance) }}</td>
                              </tr>
                            </tbody>
                          </v-simple-table>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-card outlined>
                        <v-card-title class="text-h6">Key Metrics</v-card-title>
                        <v-card-text>
                          <v-simple-table>
                            <tbody>
                              <tr>
                                <td>Liquidity Ratio</td>
                                <td class="text-right">{{ (reportData.key_metrics?.liquidity_ratio || 0).toFixed(2) }}</td>
                              </tr>
                              <tr>
                                <td>Collection Efficiency</td>
                                <td class="text-right">{{ (reportData.key_metrics?.collection_efficiency || 0).toFixed(1) }}%</td>
                              </tr>
                              <tr>
                                <td>Payment Efficiency</td>
                                <td class="text-right">{{ (reportData.key_metrics?.payment_efficiency || 0).toFixed(1) }}%</td>
                              </tr>
                              <tr>
                                <td>Budget Variance</td>
                                <td class="text-right">{{ (reportData.key_metrics?.budget_variance || 0).toFixed(1) }}%</td>
                              </tr>
                            </tbody>
                          </v-simple-table>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                </div>
                
                <!-- Cash Flow Statement Report -->
                <div v-if="selectedReport.id === 'cash-flow-statement'">
                  <v-card outlined>
                    <v-card-title class="text-h6">Cash Flow Statement</v-card-title>
                    <v-card-text>
                      <v-simple-table>
                        <tbody>
                          <tr class="font-weight-bold">
                            <td colspan="2">Operating Activities</td>
                          </tr>
                          <tr>
                            <td class="pl-4">Cash Receipts from Customers</td>
                            <td class="text-right">{{ formatCurrency(reportData.cash_flow_statement?.operating_activities?.cash_receipts_from_customers) }}</td>
                          </tr>
                          <tr>
                            <td class="pl-4">Cash Payments to Suppliers</td>
                            <td class="text-right">{{ formatCurrency(reportData.cash_flow_statement?.operating_activities?.cash_payments_to_suppliers) }}</td>
                          </tr>
                          <tr class="font-weight-bold">
                            <td class="pl-4">Net Cash from Operating</td>
                            <td class="text-right">{{ formatCurrency(reportData.cash_flow_statement?.operating_activities?.net_cash_from_operating) }}</td>
                          </tr>
                          <tr class="font-weight-bold">
                            <td>Net Change in Cash</td>
                            <td class="text-right">{{ formatCurrency(reportData.cash_flow_statement?.net_change_in_cash) }}</td>
                          </tr>
                          <tr>
                            <td>Beginning Cash</td>
                            <td class="text-right">{{ formatCurrency(reportData.cash_flow_statement?.beginning_cash) }}</td>
                          </tr>
                          <tr class="font-weight-bold">
                            <td>Ending Cash</td>
                            <td class="text-right">{{ formatCurrency(reportData.cash_flow_statement?.ending_cash) }}</td>
                          </tr>
                        </tbody>
                      </v-simple-table>
                    </v-card-text>
                  </v-card>
                </div>
              </div>
            </v-card-text>
          </v-card>
          
          <v-card v-else>
            <v-card-text class="text-center">
              <v-icon size="64" color="grey lighten-2">mdi-file-document-outline</v-icon>
              <div class="text-h6 mt-3">Select a report to get started</div>
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


/**
 * IntegratedReports Component
 * 
 * @component
 */

export default {
  name: 'IntegratedReports',
  setup() {
    const integrationStore = useIntegrationStore()
    const selectedReport = ref(null)
    const reportData = ref(null)
    const loading = ref(false)
    const dateRange = ref({
      start: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
      end: new Date().toISOString().split('T')[0]
    })
    
    const availableReports = ref([
      {
        id: 'executive-dashboard',
        title: 'Executive Dashboard',
        description: 'Comprehensive financial overview',
        icon: 'mdi-view-dashboard'
      },
      {
        id: 'cash-flow-statement',
        title: 'Cash Flow Statement',
        description: 'Integrated cash flow analysis',
        icon: 'mdi-cash-flow'
      },
      {
        id: 'financial-summary',
        title: 'Financial Summary',
        description: 'Cross-module financial summary',
        icon: 'mdi-chart-line'
      }
    ])
    
    const formatCurrency = (value) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value || 0)
    }
    
    const selectReport = (report) => {
      selectedReport.value = report
      reportData.value = null
    }
    
    const generateReport = async () => {
      if (!selectedReport.value) return
      
      loading.value = true
      try {
        let data
        
        if (selectedReport.value.id === 'executive-dashboard') {
          data = await integrationStore.getExecutiveDashboard(1, dateRange.value.start, dateRange.value.end)
        } else if (selectedReport.value.id === 'cash-flow-statement') {
          data = await integrationStore.getCashFlowStatement(1, dateRange.value.start, dateRange.value.end)
        } else if (selectedReport.value.id === 'financial-summary') {
          data = await integrationStore.getFinancialSummary(1)
        }
        
        reportData.value = data
      } catch (error) {
        console.error('Error generating report:', error)
      } finally {
        loading.value = false
      }
    }
    
    return {
      availableReports,
      selectedReport,
      reportData,
      loading,
      dateRange,
      selectReport,
      generateReport,
      formatCurrency
    }
  }
}
</script>