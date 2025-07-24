<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <h2>Financial Statements</h2>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              prepend-icon="mdi-refresh"
              @click="generateStatements"
              :loading="isGenerating"
            >
              Generate Statements
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-menu
                  ref="asOfDateMenu"
                  v-model="asOfDateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="formattedAsOfDate"
                      label="As of Date"
                      prepend-icon="mdi-calendar"
                      readonly
                      v-bind="props"
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="asOfDate"
                    @update:model-value="asOfDateMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-select
                  v-model="selectedCompany"
                  :items="companies"
                  item-title="name"
                  item-value="id"
                  label="Company"
                  prepend-icon="mdi-office-building"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-select
                  v-model="currency"
                  :items="currencies"
                  label="Currency"
                  prepend-icon="mdi-currency-usd"
                ></v-select>
              </v-col>
            </v-row>
            
            <v-row>
              <v-col cols="12" md="4">
                <v-checkbox
                  v-model="includeComparative"
                  label="Include Comparative Figures"
                ></v-checkbox>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-checkbox
                  v-model="includeYtd"
                  label="Include Year-to-Date Figures"
                ></v-checkbox>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-checkbox
                  v-model="formatCurrency"
                  label="Format as Currency"
                ></v-checkbox>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <v-row v-if="statements">
      <v-col cols="12">
        <v-tabs v-model="activeTab" bg-color="primary">
          <v-tab value="balance-sheet">Balance Sheet</v-tab>
          <v-tab value="income-statement">Income Statement</v-tab>
          <v-tab value="cash-flow">Cash Flow Statement</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab">
          <!-- Balance Sheet Tab -->
          <v-window-item value="balance-sheet">
            <v-card>
              <v-card-title class="d-flex align-center">
                <h3>Balance Sheet</h3>
                <v-spacer></v-spacer>
                <v-btn
                  icon
                  variant="text"
                  @click="exportStatement('balance_sheet', 'pdf')"
                >
                  <v-icon>mdi-file-pdf-box</v-icon>
                </v-btn>
                <v-btn
                  icon
                  variant="text"
                  @click="exportStatement('balance_sheet', 'excel')"
                >
                  <v-icon>mdi-file-excel</v-icon>
                </v-btn>
              </v-card-title>
              
              <v-card-text>
                <div v-if="statements.balance_sheet">
                  <h4 class="text-center mb-4">
                    Balance Sheet as of {{ formattedAsOfDate }}
                  </h4>
                  
                  <v-table>
                    <thead>
                      <tr>
                        <th>Account</th>
                        <th class="text-right">Amount</th>
                        <th v-if="includeComparative" class="text-right">Previous Period</th>
                      </tr>
                    </thead>
                    <tbody>
                      <template v-for="(section, sIndex) in statements.balance_sheet.sections" :key="sIndex">
                        <tr class="section-header">
                          <td colspan="3" class="text-h6">{{ section.name }}</td>
                        </tr>
                        
                        <template v-for="(line, lIndex) in section.lines" :key="`${sIndex}-${lIndex}`">
                          <tr :class="{ 'font-weight-bold': line.is_header || line.is_subtotal || line.is_total }">
                            <td :class="{ 'pl-6': !line.is_header && !line.is_subtotal && !line.is_total }">
                              {{ line.account_name || line.name }}
                            </td>
                            <td class="text-right">{{ line.amount }}</td>
                            <td v-if="includeComparative" class="text-right">
                              {{ line.amount_prev || '-' }}
                            </td>
                          </tr>
                        </template>
                      </template>
                      
                      <!-- Total Assets -->
                      <tr class="total-row">
                        <td class="text-h6">Total Assets</td>
                        <td class="text-right text-h6">
                          {{ statements.balance_sheet.total_assets?.amount || '-' }}
                        </td>
                        <td v-if="includeComparative" class="text-right text-h6">
                          {{ statements.balance_sheet.total_assets?.amount_prev || '-' }}
                        </td>
                      </tr>
                      
                      <!-- Total Liabilities and Equity -->
                      <tr class="total-row">
                        <td class="text-h6">Total Liabilities and Equity</td>
                        <td class="text-right text-h6">
                          {{ statements.balance_sheet.total_liabilities_equity?.amount || '-' }}
                        </td>
                        <td v-if="includeComparative" class="text-right text-h6">
                          {{ statements.balance_sheet.total_liabilities_equity?.amount_prev || '-' }}
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </div>
                <div v-else class="text-center pa-4">
                  No balance sheet data available
                </div>
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <!-- Income Statement Tab -->
          <v-window-item value="income-statement">
            <v-card>
              <v-card-title class="d-flex align-center">
                <h3>Income Statement</h3>
                <v-spacer></v-spacer>
                <v-btn
                  icon
                  variant="text"
                  @click="exportStatement('income_statement', 'pdf')"
                >
                  <v-icon>mdi-file-pdf-box</v-icon>
                </v-btn>
                <v-btn
                  icon
                  variant="text"
                  @click="exportStatement('income_statement', 'excel')"
                >
                  <v-icon>mdi-file-excel</v-icon>
                </v-btn>
              </v-card-title>
              
              <v-card-text>
                <div v-if="statements.income_statement">
                  <h4 class="text-center mb-4">
                    Income Statement for the Period Ending {{ formattedAsOfDate }}
                  </h4>
                  
                  <v-table>
                    <thead>
                      <tr>
                        <th>Account</th>
                        <th class="text-right">Amount</th>
                        <th v-if="includeComparative" class="text-right">Previous Period</th>
                        <th v-if="includeYtd" class="text-right">Year to Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      <template v-for="(section, sIndex) in statements.income_statement.sections" :key="sIndex">
                        <tr class="section-header">
                          <td :colspan="includeComparative && includeYtd ? 4 : (includeComparative || includeYtd ? 3 : 2)" class="text-h6">
                            {{ section.name }}
                          </td>
                        </tr>
                        
                        <template v-for="(line, lIndex) in section.lines" :key="`${sIndex}-${lIndex}`">
                          <tr :class="{ 'font-weight-bold': line.is_header || line.is_subtotal || line.is_total }">
                            <td :class="{ 'pl-6': !line.is_header && !line.is_subtotal && !line.is_total }">
                              {{ line.account_name || line.name }}
                            </td>
                            <td class="text-right">{{ line.amount }}</td>
                            <td v-if="includeComparative" class="text-right">
                              {{ line.amount_prev || '-' }}
                            </td>
                            <td v-if="includeYtd" class="text-right">
                              {{ line.amount_ytd || '-' }}
                            </td>
                          </tr>
                        </template>
                      </template>
                      
                      <!-- Gross Profit -->
                      <tr class="subtotal-row">
                        <td class="font-weight-bold">Gross Profit</td>
                        <td class="text-right font-weight-bold">
                          {{ statements.income_statement.gross_profit?.amount || '-' }}
                        </td>
                        <td v-if="includeComparative" class="text-right font-weight-bold">
                          {{ statements.income_statement.gross_profit?.amount_prev || '-' }}
                        </td>
                        <td v-if="includeYtd" class="text-right font-weight-bold">
                          {{ statements.income_statement.gross_profit?.amount_ytd || '-' }}
                        </td>
                      </tr>
                      
                      <!-- Operating Income -->
                      <tr class="subtotal-row">
                        <td class="font-weight-bold">Operating Income</td>
                        <td class="text-right font-weight-bold">
                          {{ statements.income_statement.operating_income?.amount || '-' }}
                        </td>
                        <td v-if="includeComparative" class="text-right font-weight-bold">
                          {{ statements.income_statement.operating_income?.amount_prev || '-' }}
                        </td>
                        <td v-if="includeYtd" class="text-right font-weight-bold">
                          {{ statements.income_statement.operating_income?.amount_ytd || '-' }}
                        </td>
                      </tr>
                      
                      <!-- Net Income -->
                      <tr class="total-row">
                        <td class="text-h6">Net Income</td>
                        <td class="text-right text-h6">
                          {{ statements.income_statement.net_income?.amount || '-' }}
                        </td>
                        <td v-if="includeComparative" class="text-right text-h6">
                          {{ statements.income_statement.net_income?.amount_prev || '-' }}
                        </td>
                        <td v-if="includeYtd" class="text-right text-h6">
                          {{ statements.income_statement.net_income?.amount_ytd || '-' }}
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </div>
                <div v-else class="text-center pa-4">
                  No income statement data available
                </div>
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <!-- Cash Flow Statement Tab -->
          <v-window-item value="cash-flow">
            <v-card>
              <v-card-title class="d-flex align-center">
                <h3>Cash Flow Statement</h3>
                <v-spacer></v-spacer>
                <v-btn
                  icon
                  variant="text"
                  @click="exportStatement('cash_flow', 'pdf')"
                >
                  <v-icon>mdi-file-pdf-box</v-icon>
                </v-btn>
                <v-btn
                  icon
                  variant="text"
                  @click="exportStatement('cash_flow', 'excel')"
                >
                  <v-icon>mdi-file-excel</v-icon>
                </v-btn>
              </v-card-title>
              
              <v-card-text>
                <div v-if="statements.cash_flow">
                  <h4 class="text-center mb-4">
                    Cash Flow Statement for the Period Ending {{ formattedAsOfDate }}
                  </h4>
                  
                  <v-table>
                    <thead>
                      <tr>
                        <th>Item</th>
                        <th class="text-right">Amount</th>
                        <th v-if="includeComparative" class="text-right">Previous Period</th>
                      </tr>
                    </thead>
                    <tbody>
                      <template v-for="(section, sIndex) in statements.cash_flow.sections" :key="sIndex">
                        <tr class="section-header">
                          <td colspan="3" class="text-h6">{{ section.name }}</td>
                        </tr>
                        
                        <template v-for="(line, lIndex) in section.lines" :key="`${sIndex}-${lIndex}`">
                          <tr :class="{ 'font-weight-bold': line.is_header || line.is_subtotal || line.is_total }">
                            <td :class="{ 'pl-6': !line.is_header && !line.is_subtotal && !line.is_total }">
                              {{ line.account_name || line.name }}
                            </td>
                            <td class="text-right">{{ line.amount }}</td>
                            <td v-if="includeComparative" class="text-right">
                              {{ line.amount_prev || '-' }}
                            </td>
                          </tr>
                        </template>
                        
                        <!-- Section Total -->
                        <tr v-if="section.show_totals" class="subtotal-row">
                          <td class="font-weight-bold">Total {{ section.name }}</td>
                          <td class="text-right font-weight-bold">{{ section.total }}</td>
                          <td v-if="includeComparative" class="text-right font-weight-bold">
                            {{ section.total_prev || '-' }}
                          </td>
                        </tr>
                      </template>
                      
                      <!-- Net Increase/Decrease in Cash -->
                      <tr class="total-row">
                        <td class="text-h6">Net Increase (Decrease) in Cash</td>
                        <td class="text-right text-h6">
                          {{ statements.cash_flow.net_increase_decrease || '-' }}
                        </td>
                        <td v-if="includeComparative" class="text-right text-h6">
                          {{ statements.cash_flow.metadata?.net_increase_decrease_prev || '-' }}
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </div>
                <div v-else class="text-center pa-4">
                  No cash flow statement data available
                </div>
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
    
    <!-- Previous Statements Section -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title>Previous Statements</v-card-title>
          <v-card-text>
            <v-data-table
              :headers="previousStatementsHeaders"
              :items="previousStatements"
              :loading="isLoadingPrevious"
              class="elevation-1"
            >
              <template v-slot:item.statement_type="{ item }">
                {{ formatStatementType(item.statement_type) }}
              </template>
              
              <template v-slot:item.generated_at="{ item }">
                {{ formatDate(item.generated_at) }}
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  variant="text"
                  @click="viewStatement(item)"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
                <v-btn
                  icon
                  variant="text"
                  @click="exportStatement(item.id, 'pdf')"
                >
                  <v-icon>mdi-file-pdf-box</v-icon>
                </v-btn>
                <v-btn
                  icon
                  variant="text"
                  @click="exportStatement(item.id, 'excel')"
                >
                  <v-icon>mdi-file-excel</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Loading Overlay -->
    <v-overlay
      :model-value="isGenerating"
      class="align-center justify-center"
    >
      <v-progress-circular
        indeterminate
        size="64"
        color="primary"
      ></v-progress-circular>
      <div class="mt-4">Generating Financial Statements...</div>
    </v-overlay>
  </v-container>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { format } from 'date-fns';
import financialStatementService from '@/services/financialStatementService';
import { useSnackbar } from '@/composables/useSnackbar';

export default {
  name: 'FinancialStatementsView',
  
  setup() {
    const { showSnackbar } = useSnackbar();
    
    // Form data
    const asOfDate = ref(new Date().toISOString().substr(0, 10));
    const asOfDateMenu = ref(false);
    const selectedCompany = ref(null);
    const companies = ref([
      { id: '1', name: 'Main Company' },
      { id: '2', name: 'Subsidiary A' },
      { id: '3', name: 'Subsidiary B' }
    ]);
    const currency = ref('USD');
    const currencies = ref(['USD', 'EUR', 'GBP', 'CAD', 'AUD']);
    const includeComparative = ref(true);
    const includeYtd = ref(true);
    const formatCurrency = ref(true);
    
    // UI state
    const activeTab = ref('balance-sheet');
    const isGenerating = ref(false);
    const isLoadingPrevious = ref(false);
    const statements = ref(null);
    const previousStatements = ref([]);
    
    // Computed properties
    const formattedAsOfDate = computed(() => {
      return format(new Date(asOfDate.value), 'MMM dd, yyyy');
    });
    
    const previousStatementsHeaders = [
      { title: 'Name', key: 'name' },
      { title: 'Type', key: 'statement_type' },
      { title: 'Date', key: 'end_date' },
      { title: 'Generated', key: 'generated_at' },
      { title: 'Actions', key: 'actions', sortable: false }
    ];
    
    // Methods
    const generateStatements = async () => {
      if (!selectedCompany.value) {
        showSnackbar('Please select a company', 'error');
        return;
      }
      
      isGenerating.value = true;
      
      try {
        const response = await financialStatementService.generateAllStatements(
          selectedCompany.value,
          new Date(asOfDate.value),
          {
            includeComparative: includeComparative.value,
            includeYtd: includeYtd.value,
            currency: currency.value,
            formatCurrency: formatCurrency.value
          }
        );
        
        statements.value = response.data;
        showSnackbar('Financial statements generated successfully', 'success');
      } catch (error) {
        console.error('Error generating statements:', error);
        showSnackbar('Failed to generate financial statements', 'error');
      } finally {
        isGenerating.value = false;
      }
    };
    
    const loadPreviousStatements = async () => {
      if (!selectedCompany.value) return;
      
      isLoadingPrevious.value = true;
      
      try {
        const response = await financialStatementService.listFinancialStatements(
          selectedCompany.value,
          {
            limit: 10
          }
        );
        
        previousStatements.value = response.data;
      } catch (error) {
        console.error('Error loading previous statements:', error);
        showSnackbar('Failed to load previous statements', 'error');
      } finally {
        isLoadingPrevious.value = false;
      }
    };
    
    const viewStatement = async (statement) => {
      try {
        const response = await financialStatementService.getFinancialStatement(statement.id);
        
        // Determine which tab to show based on statement type
        if (statement.statement_type === 'balance_sheet') {
          activeTab.value = 'balance-sheet';
        } else if (statement.statement_type === 'income_statement') {
          activeTab.value = 'income-statement';
        } else if (statement.statement_type === 'cash_flow') {
          activeTab.value = 'cash-flow';
        }
        
        // Update the statements object with just this statement
        statements.value = {
          [statement.statement_type]: response.data
        };
      } catch (error) {
        console.error('Error viewing statement:', error);
        showSnackbar('Failed to load statement', 'error');
      }
    };
    
    const exportStatement = async (statementId, format) => {
      try {
        let response;
        
        if (format === 'pdf') {
          response = await financialStatementService.exportToPdf(statementId);
        } else {
          response = await financialStatementService.exportToExcel(statementId);
        }
        
        // Create a blob from the response data
        const blob = new Blob([response.data], {
          type: format === 'pdf' ? 'application/pdf' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });
        
        // Create a URL for the blob
        const url = window.URL.createObjectURL(blob);
        
        // Create a link element and trigger the download
        const link = document.createElement('a');
        link.href = url;
        link.download = `financial-statement.${format === 'pdf' ? 'pdf' : 'xlsx'}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showSnackbar(`Statement exported to ${format.toUpperCase()} successfully`, 'success');
      } catch (error) {
        console.error(`Error exporting to ${format}:`, error);
        showSnackbar(`Failed to export statement to ${format.toUpperCase()}`, 'error');
      }
    };
    
    const formatStatementType = (type) => {
      switch (type) {
        case 'balance_sheet':
          return 'Balance Sheet';
        case 'income_statement':
          return 'Income Statement';
        case 'cash_flow':
          return 'Cash Flow Statement';
        default:
          return type;
      }
    };
    
    const formatDate = (dateString) => {
      return format(new Date(dateString), 'MMM dd, yyyy');
    };
    
    // Lifecycle hooks
    onMounted(() => {
      // Set default company
      if (companies.value.length > 0) {
        selectedCompany.value = companies.value[0].id;
      }
      
      // Load previous statements
      loadPreviousStatements();
    });
    
    // Watch for company changes to reload previous statements
    watch(selectedCompany, () => {
      loadPreviousStatements();
    });
    
    return {
      // Form data
      asOfDate,
      asOfDateMenu,
      selectedCompany,
      companies,
      currency,
      currencies,
      includeComparative,
      includeYtd,
      formatCurrency,
      
      // UI state
      activeTab,
      isGenerating,
      isLoadingPrevious,
      statements,
      previousStatements,
      previousStatementsHeaders,
      
      // Computed
      formattedAsOfDate,
      
      // Methods
      generateStatements,
      loadPreviousStatements,
      viewStatement,
      exportStatement,
      formatStatementType,
      formatDate
    };
  }
};
</script>

<style scoped>
.section-header {
  background-color: rgba(0, 0, 0, 0.05);
}

.subtotal-row {
  background-color: rgba(0, 0, 0, 0.02);
}

.total-row {
  background-color: rgba(0, 0, 0, 0.08);
  border-top: 1px solid rgba(0, 0, 0, 0.12);
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}
</style>