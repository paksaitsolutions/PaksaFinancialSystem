<template>
  <div class="financial-statements">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2>Financial Statements</h2>
      <div>
        <Button 
          label="Generate Report" 
          icon="pi pi-file-pdf" 
          @click="showReportDialog = true"
          class="p-button-success"
        />
      </div>
    </div>

    <div class="grid">
      <!-- Balance Sheet Card -->
      <div class="col-12 lg:col-6">
        <div class="card h-full">
          <div class="flex justify-content-between align-items-center mb-4">
            <h3>Balance Sheet</h3>
            <Button 
              icon="pi pi-download" 
              class="p-button-text" 
              @click="exportToPdf('balance-sheet')"
              v-tooltip.top="'Export to PDF'"
            />
          </div>
          
          <DataTable 
            :value="balanceSheetData" 
            :loading="loading"
            :rowHover="true"
            :stripedRows="true"
            class="p-datatable-sm"
            :scrollable="true"
            scrollHeight="400px"
          >
            <Column field="account" header="Account" style="min-width:200px">
              <template #body="{ data }">
                <span :class="{ 'font-bold': data.isHeader }">
                  {{ data.account }}
                </span>
              </template>
            </Column>
            <Column field="amount" header="Amount" style="width:150px">
              <template #body="{ data }">
                <span :class="{ 'font-bold': data.isHeader }">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
            
            <template #footer>
              <div class="flex justify-content-between p-2 border-top-1 border-gray-300">
                <div class="font-bold">Total Assets</div>
                <div class="font-bold">{{ formatCurrency(totalAssets) }}</div>
              </div>
              <div class="flex justify-content-between p-2 border-top-1 border-gray-300">
                <div class="font-bold">Total Liabilities & Equity</div>
                <div class="font-bold">{{ formatCurrency(totalLiabilitiesEquity) }}</div>
              </div>
            </template>
          </DataTable>
          
          <div class="mt-4 text-sm text-gray-600">
            <i class="pi pi-info-circle mr-1"></i>
            As of {{ formatDate(new Date()) }}
          </div>
        </div>
      </div>
      
      <!-- Income Statement Card -->
      <div class="col-12 lg:col-6">
        <div class="card h-full">
          <div class="flex justify-content-between align-items-center mb-4">
            <h3>Income Statement</h3>
            <Button 
              icon="pi pi-download" 
              class="p-button-text" 
              @click="exportToPdf('income-statement')"
              v-tooltip.top="'Export to PDF'"
            />
          </div>
          
          <DataTable 
            :value="incomeStatementData" 
            :loading="loading"
            :rowHover="true"
            :stripedRows="true"
            class="p-datatable-sm"
            :scrollable="true"
            scrollHeight="400px"
          >
            <Column field="account" header="Account" style="min-width:200px">
              <template #body="{ data }">
                <span :class="{ 'font-bold': data.isHeader }">
                  {{ data.account }}
                </span>
              </template>
            </Column>
            <Column field="amount" header="Amount" style="width:150px">
              <template #body="{ data }">
                <span :class="{ 'font-bold': data.isHeader }">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
            
            <template #footer>
              <div class="flex justify-content-between p-2 border-top-1 border-gray-300">
                <div class="font-bold">Net Income</div>
                <div class="font-bold" :class="{ 'text-green-600': netIncome >= 0, 'text-red-600': netIncome < 0 }">
                  {{ formatCurrency(netIncome) }}
                </div>
              </div>
            </template>
          </DataTable>
          
          <div class="mt-4 text-sm text-gray-600">
            <i class="pi pi-info-circle mr-1"></i>
            For the period {{ formatDateRange(reportParams.start_date, reportParams.end_date) }}
          </div>
        </div>
      </div>
      
      <!-- Cash Flow Card -->
      <div class="col-12">
        <div class="card mt-4">
          <div class="flex justify-content-between align-items-center mb-4">
            <h3>Cash Flow Statement</h3>
            <Button 
              icon="pi pi-download" 
              class="p-button-text" 
              @click="exportToPdf('cash-flow')"
              v-tooltip.top="'Export to PDF'"
            />
          </div>
          
          <DataTable 
            :value="cashFlowData" 
            :loading="loading"
            :rowHover="true"
            :stripedRows="true"
            class="p-datatable-sm"
            :scrollable="true"
            scrollHeight="300px"
          >
            <Column field="activity" header="Activity" style="min-width:200px">
              <template #body="{ data }">
                <span :class="{ 'font-bold': data.isHeader }">
                  {{ data.activity }}
                </span>
              </template>
            </Column>
            <Column field="amount" header="Amount" style="width:150px">
              <template #body="{ data }">
                <span :class="{ 'font-bold': data.isHeader }">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
            
            <template #footer>
              <div class="flex justify-content-between p-2 border-top-1 border-gray-300">
                <div class="font-bold">Net Increase in Cash</div>
                <div class="font-bold" :class="{ 'text-green-600': netCashFlow >= 0, 'text-red-600': netCashFlow < 0 }">
                  {{ formatCurrency(netCashFlow) }}
                </div>
              </div>
              <div class="flex justify-content-between p-2 border-top-1 border-gray-300">
                <div class="font-bold">Cash at Beginning of Period</div>
                <div class="font-bold">{{ formatCurrency(cashBeginning) }}</div>
              </div>
              <div class="flex justify-content-between p-2 border-top-1 border-gray-300">
                <div class="font-bold">Cash at End of Period</div>
                <div class="font-bold">{{ formatCurrency(cashEnd) }}</div>
              </div>
            </template>
          </DataTable>
          
          <div class="mt-4 text-sm text-gray-600">
            <i class="pi pi-info-circle mr-1"></i>
            For the period {{ formatDateRange(reportParams.start_date, reportParams.end_date) }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Report Generation Dialog -->
    <Dialog 
      v-model:visible="showReportDialog" 
      header="Generate Financial Statements"
      :modal="true"
      :style="{ width: '500px' }"
    >
      <div class="field">
        <label>Report Type</label>
        <div class="flex flex-column gap-2 mt-2">
          <div class="flex align-items-center">
            <RadioButton 
              id="report-type-balance" 
              v-model="reportParams.report_type" 
              value="balance-sheet" 
              class="mr-2" 
            />
            <label for="report-type-balance">Balance Sheet</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="report-type-income" 
              v-model="reportParams.report_type" 
              value="income-statement" 
              class="mr-2" 
            />
            <label for="report-type-income">Income Statement</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="report-type-cash" 
              v-model="reportParams.report_type" 
              value="cash-flow" 
              class="mr-2" 
            />
            <label for="report-type-cash">Cash Flow Statement</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="report-type-all" 
              v-model="reportParams.report_type" 
              value="all" 
              class="mr-2" 
            />
            <label for="report-type-all">All Statements</label>
          </div>
        </div>
      </div>
      
      <div class="field mt-4">
        <label>Date Range</label>
        <div class="flex flex-column gap-2 mt-2">
          <div class="flex align-items-center">
            <RadioButton 
              id="period-month" 
              v-model="reportParams.period" 
              value="month" 
              class="mr-2" 
            />
            <label for="period-month">This Month</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="period-quarter" 
              v-model="reportParams.period" 
              value="quarter" 
              class="mr-2" 
            />
            <label for="period-quarter">This Quarter</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="period-year" 
              v-model="reportParams.period" 
              value="year" 
              class="mr-2" 
            />
            <label for="period-year">This Fiscal Year</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="period-custom" 
              v-model="reportParams.period" 
              value="custom" 
              class="mr-2" 
            />
            <label for="period-custom">Custom Range</label>
          </div>
          
          <div v-if="reportParams.period === 'custom'" class="grid mt-2">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Start Date</label>
                <Calendar 
                  v-model="reportParams.start_date" 
                  :showIcon="true" 
                  dateFormat="yy-mm-dd"
                  class="w-full"
                />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>End Date</label>
                <Calendar 
                  v-model="reportParams.end_date" 
                  :showIcon="true" 
                  dateFormat="yy-mm-dd"
                  class="w-full"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="field mt-4">
        <label>Format</label>
        <div class="flex flex-column gap-2 mt-2">
          <div class="flex align-items-center">
            <RadioButton 
              id="format-pdf" 
              v-model="reportParams.format" 
              value="pdf" 
              class="mr-2" 
            />
            <label for="format-pdf">PDF Document</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="format-excel" 
              v-model="reportParams.format" 
              value="excel" 
              class="mr-2" 
            />
            <label for="format-excel">Excel Spreadsheet</label>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          @click="showReportDialog = false"
          class="p-button-text"
        />
        <Button 
          label="Generate Report" 
          @click="generateReport"
          class="p-button-primary"
          :loading="generating"
        />
      </template>
  <div class="financial-statements">
    <v-card>
      <v-tabs v-model="activeTab" grow>
        <v-tab value="balance-sheet">Balance Sheet</v-tab>
        <v-tab value="income-statement">Income Statement</v-tab>
        <v-tab value="cash-flow">Cash Flow</v-tab>
      </v-tabs>

      <v-card-text>
        <div class="d-flex align-center mb-4">
          <v-menu
            v-model="startDateMenu"
            :close-on-content-click="false"
            :nudge-right="40"
            transition="scale-transition"
            offset-y
            min-width="auto"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="formattedStartDate"
                label="Start Date"
                prepend-icon="mdi-calendar"
                readonly
                v-bind="attrs"
                v-on="on"
                class="mr-4"
                style="max-width: 200px"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="dateRange.start"
              @input="startDateMenu = false"
            ></v-date-picker>
          </v-menu>

          <v-menu
            v-model="endDateMenu"
            :close-on-content-click="false"
            :nudge-right="40"
            transition="scale-transition"
            offset-y
            min-width="auto"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="formattedEndDate"
                label="End Date"
                prepend-icon="mdi-calendar"
                readonly
                v-bind="attrs"
                v-on="on"
                class="mr-4"
                style="max-width: 200px"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="dateRange.end"
              @input="endDateMenu = false"
            ></v-date-picker>
          </v-menu>

          <v-btn
            color="primary"
            class="mr-2"
            @click="fetchFinancialData"
            :loading="loading"
          >
            <v-icon left>mdi-refresh</v-icon>
            {{ t('common.refresh') }}
          </v-btn>

          <v-btn
            color="secondary"
            @click="showExportDialog = true"
            :loading="loading"
          >
            <v-icon left>mdi-download</v-icon>
            {{ t('common.export') }}
          </v-btn>
        </div>

        <v-window v-model="activeTab">
          <!-- Balance Sheet Tab -->
          <v-window-item value="balance-sheet">
            <v-card v-if="balanceSheetData" flat>
              <v-card-title class="text-h5">
                {{ t('financialStatements.balanceSheet') }}
                <v-spacer></v-spacer>
                <span class="text-subtitle-1">
                  {{ t('financialStatements.asOf') }} {{ formattedEndDate }}
                </span>
              </v-card-title>
              
              <v-card-text>
                <v-row>
                  <!-- Assets -->
                  <v-col cols="12" md="6">
                    <v-card outlined class="mb-4">
                      <v-card-title class="text-h6 primary--text">
                        {{ t('financialStatements.assets') }}
                      </v-card-title>
                      <v-card-text>
                        <v-simple-table dense>
                          <template v-slot:default>
                            <tbody>
                              <tr v-for="(item, index) in balanceSheetData.assets" :key="`asset-${index}`">
                                <td :class="{ 'font-weight-bold': item.isHeader, 'pl-4': !item.isHeader }">
                                  {{ item.account }}
                                </td>
                                <td class="text-right">
                                  {{ formatCurrency(item.amount) }}
                                </td>
                              </tr>
                              <tr class="font-weight-bold">
                                <td>{{ t('financialStatements.totalAssets') }}</td>
                                <td class="text-right">
                                  {{ formatCurrency(totalAssets) }}
                                </td>
                              </tr>
                            </tbody>
                          </template>
                        </v-simple-table>
                      </v-card-text>
                    </v-card>
                  </v-col>

                  <!-- Liabilities & Equity -->
                  <v-col cols="12" md="6">
                    <v-card outlined class="mb-4">
                      <v-card-title class="text-h6 primary--text">
                        {{ t('financialStatements.liabilitiesAndEquity') }}
                      </v-card-title>
                      <v-card-text>
                        <v-simple-table dense>
                          <template v-slot:default>
                            <tbody>
                              <!-- Liabilities -->
                              <tr v-for="(item, index) in balanceSheetData.liabilities" :key="`liability-${index}`">
                                <td :class="{ 'font-weight-bold': item.isHeader, 'pl-4': !item.isHeader }">
                                  {{ item.account }}
                                </td>
                                <td class="text-right">
                                  {{ formatCurrency(item.amount) }}
                                </td>
                              </tr>
                              <tr class="font-weight-bold">
                                <td>{{ t('financialStatements.totalLiabilities') }}</td>
                                <td class="text-right">
                                  {{ formatCurrency(totalLiabilities) }}
                                </td>
                              </tr>

                              <!-- Equity -->
                              <tr v-for="(item, index) in balanceSheetData.equity" :key="`equity-${index}`">
                                <td :class="{ 'font-weight-bold': item.isHeader, 'pl-4': !item.isHeader }">
                                  {{ item.account }}
                                </td>
                                <td class="text-right">
                                  {{ formatCurrency(item.amount) }}
                                </td>
                              </tr>
                              <tr class="font-weight-bold">
                                <td>{{ t('financialStatements.totalEquity') }}</td>
                                <td class="text-right">
                                  {{ formatCurrency(totalEquity) }}
                                </td>
                              </tr>

                              <!-- Total Liabilities & Equity -->
                              <tr class="font-weight-bold">
                                <td>{{ t('financialStatements.totalLiabilitiesAndEquity') }}</td>
                                <td class="text-right">
                                  {{ formatCurrency(totalLiabilities + totalEquity) }}
                                </td>
                              </tr>
                            </tbody>
                          </template>
                        </v-simple-table>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
            <v-skeleton-loader
              v-else
              type="article, actions"
              class="mt-4"
            ></v-skeleton-loader>
          </v-window-item>

          <!-- Income Statement Tab -->
          <v-window-item value="income-statement">
            <v-card v-if="incomeStatementData" flat>
              <v-card-title class="text-h5">
                {{ t('financialStatements.incomeStatement') }}
                <v-spacer></v-spacer>
                <span class="text-subtitle-1">
                  {{ t('financialStatements.forThePeriod') }} {{ formattedStartDate }} - {{ formattedEndDate }}
                </span>
              </v-card-title>
              
              <v-card-text>
                <v-card outlined class="mb-4">
                  <v-simple-table dense>
                    <template v-slot:default>
                      <tbody>
                        <!-- Revenues -->
                        <tr>
                          <td colspan="2" class="font-weight-bold primary--text">
                            {{ t('financialStatements.revenue') }}
                          </td>
                        </tr>
                        <tr v-for="(item, index) in incomeStatementData.revenues" :key="`revenue-${index}`">
                          <td :class="{ 'pl-4': !item.isHeader }">
                            {{ item.account }}
                          </td>
                          <td class="text-right">
                            {{ formatCurrency(item.amount) }}
                          </td>
                        </tr>
                        <tr class="font-weight-bold">
                          <td>{{ t('financialStatements.totalRevenue') }}</td>
                          <td class="text-right">
                            {{ formatCurrency(incomeStatementData.grossProfit) }}
                          </td>
                        </tr>

                        <!-- Expenses -->
                        <tr>
                          <td colspan="2" class="font-weight-bold primary--text mt-4">
                            {{ t('financialStatements.expenses') }}
                          </td>
                        </tr>
                        <tr v-for="(item, index) in incomeStatementData.expenses" :key="`expense-${index}`">
                          <td :class="{ 'pl-4': !item.isHeader }">
                            {{ item.account }}
                          </td>
                          <td class="text-right">
                            ({{ formatCurrency(Math.abs(item.amount)) }})
                          </td>
                        </tr>
                        <tr class="font-weight-bold">
                          <td>{{ t('financialStatements.totalExpenses') }}</td>
                          <td class="text-right">
                            ({{ formatCurrency(Math.abs(incomeStatementData.expenses.reduce((sum, item) => sum + item.amount, 0))) }})
                          </td>
                        </tr>

                        <!-- Net Income -->
                        <tr class="font-weight-bold" :class="{ 'success--text': incomeStatementData.netIncome >= 0, 'error--text': incomeStatementData.netIncome < 0 }">
                          <td>{{ t('financialStatements.netIncome') }}</td>
                          <td class="text-right">
                            {{ formatCurrency(incomeStatementData.netIncome) }}
                          </td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </v-card>
              </v-card-text>
            </v-card>
            <v-skeleton-loader
              v-else
              type="article, actions"
              class="mt-4"
            ></v-skeleton-loader>
          </v-window-item>

          <!-- Cash Flow Tab -->
          <v-window-item value="cash-flow">
            <v-card v-if="cashFlowData" flat>
              <v-card-title class="text-h5">
                {{ t('financialStatements.cashFlow') }}
                <v-spacer></v-spacer>
                <span class="text-subtitle-1">
                  {{ t('financialStatements.forThePeriod') }} {{ formattedStartDate }} - {{ formattedEndDate }}
                </span>
              </v-card-title>
              
              <v-card-text>
                <v-card outlined class="mb-4">
                  <v-simple-table dense>
                    <template v-slot:default>
                      <tbody>
                        <!-- Operating Activities -->
                        <tr>
                          <td colspan="2" class="font-weight-bold primary--text">
                            {{ t('financialStatements.cashFromOperatingActivities') }}
                          </td>
                        </tr>
                        <tr v-for="(item, index) in cashFlowData.operatingActivities" :key="`operating-${index}`">
                          <td :class="{ 'pl-4': !item.isHeader }">
                            {{ item.activity }}
                          </td>
                          <td class="text-right">
                            {{ formatCurrency(item.amount) }}
                          </td>
                        </tr>
                        <tr class="font-weight-bold">
                          <td>{{ t('financialStatements.netCashFromOperating') }}</td>
                          <td class="text-right">
                            {{ formatCurrency(cashFlowData.operatingActivities.reduce((sum, item) => sum + item.amount, 0)) }}
                          </td>
                        </tr>

                        <!-- Investing Activities -->
                        <tr>
                          <td colspan="2" class="font-weight-bold primary--text mt-4">
                            {{ t('financialStatements.cashFromInvestingActivities') }}
                          </td>
                        </tr>
                        <tr v-for="(item, index) in cashFlowData.investingActivities" :key="`investing-${index}`">
                          <td :class="{ 'pl-4': !item.isHeader }">
                            {{ item.activity }}
                          </td>
                          <td class="text-right">
                            {{ formatCurrency(item.amount) }}
                          </td>
                        </tr>
                        <tr class="font-weight-bold">
                          <td>{{ t('financialStatements.netCashFromInvesting') }}</td>
                          <td class="text-right">
                            {{ formatCurrency(cashFlowData.investingActivities.reduce((sum, item) => sum + item.amount, 0)) }}
                          </td>
                        </tr>

                        <!-- Financing Activities -->
                        <tr>
                          <td colspan="2" class="font-weight-bold primary--text mt-4">
                            {{ t('financialStatements.cashFromFinancingActivities') }}
                          </td>
                        </tr>
                        <tr v-for="(item, index) in cashFlowData.financingActivities" :key="`financing-${index}`">
                          <td :class="{ 'pl-4': !item.isHeader }">
                            {{ item.activity }}
                          </td>
                          <td class="text-right">
                            {{ formatCurrency(item.amount) }}
                          </td>
                        </tr>
                        <tr class="font-weight-bold">
                          <td>{{ t('financialStatements.netCashFromFinancing') }}</td>
                          <td class="text-right">
                            {{ formatCurrency(cashFlowData.financingActivities.reduce((sum, item) => sum + item.amount, 0)) }}
                          </td>
                        </tr>

                        <!-- Net Increase in Cash -->
                        <tr class="font-weight-bold" :class="{ 'success--text': cashFlowData.netCashFlow >= 0, 'error--text': cashFlowData.netCashFlow < 0 }">
                          <td>{{ t('financialStatements.netIncreaseInCash') }}</td>
                          <td class="text-right">
                            {{ formatCurrency(cashFlowData.netCashFlow) }}
                          </td>
                        </tr>

                        <!-- Cash at Beginning of Period -->
                        <tr>
                          <td>{{ t('financialStatements.cashAtBeginning') }}</td>
                          <td class="text-right">
                            {{ formatCurrency(cashFlowData.cashBeginning) }}
                          </td>
                        </tr>

                        <!-- Cash at End of Period -->
                        <tr class="font-weight-bold">
                          <td>{{ t('financialStatements.cashAtEnd') }}</td>
                          <td class="text-right">
                            {{ formatCurrency(cashFlowData.cashEnd) }}
                          </td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </v-card>
              </v-card-text>
            </v-card>
            <v-skeleton-loader
              v-else
              type="article, actions"
              class="mt-4"
            ></v-skeleton-loader>
          </v-window-item>
        </v-window>
      </v-card-text>
    </v-card>

    <!-- Export Dialog -->
    <v-dialog v-model="showExportDialog" max-width="500">
      <v-card>
        <v-card-title>{{ t('common.exportReport') }}</v-card-title>
        <v-card-text>
          <v-select
            v-model="selectedExportFormat"
            :items="exportFormats"
            :label="t('common.exportFormat')"
            outlined
            dense
          ></v-select>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="showExportDialog = false">{{ t('common.cancel') }}</v-btn>
          <v-btn 
            color="primary" 
            @click="handleExport"
            :loading="loading"
          >
            {{ t('common.export') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { format, parseISO } from 'date-fns';
import { useI18n } from 'vue-i18n';
import { useToast } from 'vue-toastification';
import { useGLStore } from '@/stores/gl';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

declare module 'jspdf' {
  interface jsPDF {
    autoTable: (options: any) => jsPDF;
    lastAutoTable: {
      finalY: number;
    };
  }
}

// Types
interface FinancialStatementParams {
  report_type: string;
  period: string;
  start_date: Date | string;
  end_date: Date | string;
  format: string;
  currency: string;
}

interface DateRange {
  start: Date | string;
  end: Date | string;
}

interface BalanceSheetData {
  assets: Array<{ account: string; amount: number; isHeader?: boolean }>;
  liabilities: Array<{ account: string; amount: number; isHeader?: boolean }>;
  equity: Array<{ account: string; amount: number; isHeader?: boolean }>;
  totalAssets: number;
  totalLiabilities: number;
  totalEquity: number;
  asOfDate: string;
}

interface IncomeStatementData {
  revenues: Array<{ account: string; amount: number; isHeader?: boolean }>;
  expenses: Array<{ account: string; amount: number; isHeader?: boolean }>;
  grossProfit: number;
  operatingIncome: number;
  netIncome: number;
  period: string;
}

interface CashFlowData {
  operatingActivities: Array<{ activity: string; amount: number; isHeader?: boolean }>;
  investingActivities: Array<{ activity: string; amount: number; isHeader?: boolean }>;
  financingActivities: Array<{ activity: string; amount: number; isHeader?: boolean }>;
  netCashFlow: number;
  cashBeginning: number;
  cashEnd: number;
  period: string;
}

type ReportType = 'balance-sheet' | 'income-statement' | 'cash-flow';
type ExportFormat = 'pdf' | 'excel' | 'csv';

declare module 'jspdf' {
  interface jsPDF {
    autoTable: (options: any) => jsPDF;
  }
}

// Initialize composables
const { t } = useI18n();
const toast = useToast();
const glStore = useGLStore();

// Component state
const loading = ref(false);
const activeTab = ref<ReportType>('balance-sheet');
const showExportDialog = ref(false);
const selectedExportFormat = ref<ExportFormat>('pdf');
const exportFormats = [
  { text: 'PDF', value: 'pdf' },
  { text: 'Excel', value: 'excel' },
  { text: 'CSV', value: 'csv' }
];

// Date range state
const startDateMenu = ref(false);
const endDateMenu = ref(false);
const dateRange = ref<DateRange>({
  start: new Date(new Date().getFullYear(), 0, 1), // Start of current year
  end: new Date() // Today
});

// Financial data
const balanceSheetData = ref<BalanceSheetData | null>(null);
const incomeStatementData = ref<IncomeStatementData | null>(null);
const cashFlowData = ref<CashFlowData | null>(null);

// Computed properties
const formattedStartDate = computed(() => {
  if (!dateRange.value.start) return '';
  const date = typeof dateRange.value.start === 'string' 
    ? new Date(dateRange.value.start) 
    : dateRange.value.start;
  return format(date, 'yyyy-MM-dd');
});

const formattedEndDate = computed(() => {
  if (!dateRange.value.end) return '';
  const date = typeof dateRange.value.end === 'string' 
    ? new Date(dateRange.value.end) 
    : dateRange.value.end;
  return format(date, 'yyyy-MM-dd');
});

const totalAssets = computed(() => {
  if (!balanceSheetData.value) return 0;
  return balanceSheetData.value.assets.reduce((sum, item) => sum + item.amount, 0);
});

const totalLiabilities = computed(() => {
  if (!balanceSheetData.value) return 0;
  return balanceSheetData.value.liabilities.reduce((sum, item) => sum + item.amount, 0);
});

const totalEquity = computed(() => {
  if (!balanceSheetData.value) return 0;
  return balanceSheetData.value.equity.reduce((sum, item) => sum + item.amount, 0);
});

// Methods
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

const fetchFinancialData = async () => {
  try {
    loading.value = true;
    
    // Convert string dates to Date objects if needed
    const start = typeof dateRange.value.start === 'string' 
      ? new Date(dateRange.value.start) 
      : dateRange.value.start;
    const end = typeof dateRange.value.end === 'string'
      ? new Date(dateRange.value.end)
      : dateRange.value.end;

    // Format dates for API
    const startDate = format(start, 'yyyy-MM-dd');
    const endDate = format(end, 'yyyy-MM-dd');

    // Fetch balance sheet data
    const balanceSheetParams: FinancialStatementParams = {
      report_type: 'balance-sheet',
      period: 'custom',
      start_date: startDate,
      end_date: endDate,
      format: 'json',
      currency: 'USD'
    };
    
    balanceSheetData.value = await glStore.getFinancialStatement(balanceSheetParams);

    // Fetch income statement data
    const incomeStatementParams: FinancialStatementParams = {
      report_type: 'income-statement',
      period: 'custom',
      start_date: startDate,
      end_date: endDate,
      format: 'json',
      currency: 'USD'
    };
    
    incomeStatementData.value = await glStore.getFinancialStatement(incomeStatementParams);

    // Fetch cash flow data
    const cashFlowParams: FinancialStatementParams = {
      report_type: 'cash-flow',
      period: 'custom',
      start_date: startDate,
      end_date: endDate,
      format: 'json',
      currency: 'USD'
    };
    
    cashFlowData.value = await glStore.getFinancialStatement(cashFlowParams);
    
  } catch (error) {
    console.error('Error fetching financial data:', error);
    toast.error(t('error.fetchingFinancialData'));
  } finally {
    loading.value = false;
  }
};

const handleExport = async () => {
  try {
    loading.value = true;
    
    const startDate = format(
      typeof dateRange.value.start === 'string' 
        ? new Date(dateRange.value.start) 
        : dateRange.value.start, 
      'yyyy-MM-dd'
    );
    
    const endDate = format(
      typeof dateRange.value.end === 'string' 
        ? new Date(dateRange.value.end) 
        : dateRange.value.end, 
      'yyyy-MM-dd'
    );

    const params: FinancialStatementParams = {
      report_type: activeTab.value,
      period: 'custom',
      start_date: startDate,
      end_date: endDate,
      format: selectedExportFormat.value,
      currency: 'USD'
    };

    let data: any;
    let filename = `${activeTab.value}-${startDate}-to-${endDate}`;

    switch (selectedExportFormat.value) {
      case 'pdf':
        // Generate PDF using jsPDF
        const doc = new jsPDF();
        
        // Add title
        doc.setFontSize(18);
        doc.text(
          `${activeTab.value} - ${startDate} to ${endDate}`.toUpperCase(),
          14,
          22
        );
        
        // Add table
        doc.autoTable({
          startY: 30,
          head: [['Account', 'Amount']],
          body: getExportData(),
          theme: 'grid',
          headStyles: {
            fillColor: [41, 128, 185],
            textColor: 255,
            fontStyle: 'bold'
          },
          alternateRowStyles: {
            fillColor: [245, 245, 245]
          },
          margin: { top: 10 }
        });
        
        // Save the PDF
        doc.save(`${filename}.pdf`);
        break;
        
      case 'excel':
      case 'csv':
        data = await glStore.exportFinancialStatement(params);
        
        // Create download link
        const blob = new Blob([data], { type: 'application/octet-stream' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}.${selectedExportFormat.value}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
        break;
    }
    
    showExportDialog.value = false;
    toast.success(t('success.exportSuccessful'));
    
  } catch (error) {
    console.error('Error exporting data:', error);
    toast.error(t('error.exportFailed'));
  } finally {
    loading.value = false;
  }
};

const getExportData = (): string[][] => {
  switch (activeTab.value) {
    case 'balance-sheet':
      if (!balanceSheetData.value) return [];
      
      const balanceSheetRows: string[][] = [];
      
      // Add assets
      balanceSheetRows.push(['Assets', '']);
      balanceSheetData.value.assets.forEach(item => {
        balanceSheetRows.push([
          `${item.isHeader ? '' : '  '}${item.account}`,
          formatCurrency(item.amount)
        ]);
      });
      
      // Add liabilities
      balanceSheetRows.push(['', '']);
      balanceSheetRows.push(['Liabilities', '']);
      balanceSheetData.value.liabilities.forEach(item => {
        balanceSheetRows.push([
          `${item.isHeader ? '' : '  '}${item.account}`,
          formatCurrency(item.amount)
        ]);
      });
      
      // Add equity
      balanceSheetRows.push(['', '']);
      balanceSheetRows.push(['Equity', '']);
      balanceSheetData.value.equity.forEach(item => {
        balanceSheetRows.push([
          `${item.isHeader ? '' : '  '}${item.account}`,
          formatCurrency(item.amount)
        ]);
      });
      
      // Add totals
      balanceSheetRows.push(['', '']);
      balanceSheetRows.push(['Total Assets', formatCurrency(totalAssets.value)]);
      balanceSheetRows.push(['Total Liabilities & Equity', 
        formatCurrency(totalLiabilities.value + totalEquity.value)]);
      
      return balanceSheetRows;
      
    case 'income-statement':
      if (!incomeStatementData.value) return [];
      
      const incomeStatementRows: string[][] = [];
      
      // Add revenues
      incomeStatementRows.push(['Revenues', '']);
      incomeStatementData.value.revenues.forEach(item => {
        incomeStatementRows.push([
          `${item.isHeader ? '' : '  '}${item.account}`,
          formatCurrency(item.amount)
        ]);
      });
      
      // Add expenses
      incomeStatementRows.push(['', '']);
      incomeStatementRows.push(['Expenses', '']);
      incomeStatementData.value.expenses.forEach(item => {
        incomeStatementRows.push([
          `${item.isHeader ? '' : '  '}${item.account}`,
          formatCurrency(item.amount)
        ]);
      });
      
      // Add net income
      incomeStatementRows.push(['', '']);
      incomeStatementRows.push(['Net Income', 
        formatCurrency(incomeStatementData.value.netIncome)]);
      
      return incomeStatementRows;
      
    case 'cash-flow':
      if (!cashFlowData.value) return [];
      
      const cashFlowRows: string[][] = [];
      
      // Add operating activities
      cashFlowRows.push(['Operating Activities', '']);
      cashFlowData.value.operatingActivities.forEach(item => {
        cashFlowRows.push([
          `${item.isHeader ? '' : '  '}${item.activity}`,
          formatCurrency(item.amount)
        ]);
      });
      
      // Add investing activities
      cashFlowRows.push(['', '']);
      cashFlowRows.push(['Investing Activities', '']);
      cashFlowData.value.investingActivities.forEach(item => {
        cashFlowRows.push([
          `${item.isHeader ? '' : '  '}${item.activity}`,
          formatCurrency(item.amount)
        ]);
      });
      
      // Add financing activities
      cashFlowRows.push(['', '']);
      cashFlowRows.push(['Financing Activities', '']);
      cashFlowData.value.financingActivities.forEach(item => {
        cashFlowRows.push([
          `${item.isHeader ? '' : '  '}${item.activity}`,
          formatCurrency(item.amount)
        ]);
      });
      
      // Add summary
      cashFlowRows.push(['', '']);
      cashFlowRows.push(['Net Increase in Cash', 
        formatCurrency(cashFlowData.value.netCashFlow)]);
      cashFlowRows.push(['Cash at Beginning of Period', 
        formatCurrency(cashFlowData.value.cashBeginning)]);
      cashFlowRows.push(['Cash at End of Period', 
        formatCurrency(cashFlowData.value.cashEnd)]);
      
      return cashFlowRows;
      
    default:
      return [];
  }
};

// Lifecycle hooks
onMounted(() => {
  fetchFinancialData();
});

// Watchers
watch([() => dateRange.value.start, () => dateRange.value.end], () => {
  if (dateRange.value.start && dateRange.value.end) {
    fetchFinancialData();
  }
});
  
  setup() {
    // Initialize composables
    const { t } = useI18n();
    const toast = useToast();
    const glStore = useGLStore();
    
    // Refs
    const loading = ref(false);
    const generating = ref(false);
    const activeTab = ref<ReportType>('balance-sheet');
    const startDateMenu = ref(false);
    const endDateMenu = ref(false);
    
    // Date range for reports
    const dateRange = ref<DateRange>({
      start: new Date(new Date().getFullYear(), 0, 1), // Start of current year
      end: new Date() // Today
    });
    
    // Format dates for display
    const formattedStartDate = computed(() => {
      return formatDate(dateRange.value.start);
    });
    
    const formattedEndDate = computed(() => {
      return formatDate(dateRange.value.end);
    });
    
    // Report data
    const balanceSheetData = ref<BalanceSheetData | null>(null);
    const incomeStatementData = ref<IncomeStatementData | null>(null);
    const cashFlowData = ref<CashFlowData | null>(null);
    
    // Export formats
    const exportFormats = [
      { text: 'PDF', value: 'pdf' },
      { text: 'Excel', value: 'excel' },
      { text: 'CSV', value: 'csv' }
    ];
    
    const selectedExportFormat = ref<ExportFormat>('pdf');
    
    // Computed properties
    const totalAssets = computed(() => balanceSheetData.value?.totalAssets || 0);
    const totalLiabilities = computed(() => balanceSheetData.value?.totalLiabilities || 0);
    const totalEquity = computed(() => balanceSheetData.value?.totalEquity || 0);
    const netIncome = computed(() => incomeStatementData.value?.netIncome || 0);
    const netCashFlow = computed(() => cashFlowData.value?.netCashFlow || 0);
    const cashBeginning = computed(() => cashFlowData.value?.cashBeginning || 0);
    const cashEnd = computed(() => cashFlowData.value?.cashEnd || 0);

    // Format date for display
    const formatDate = (date: Date | string): string => {
      try {
        const dateObj = typeof date === 'string' ? new Date(date) : date;
        if (isNaN(dateObj.getTime())) return 'Invalid Date';
        
        return dateObj.toLocaleDateString('en-US', { 
          year: 'numeric', 
          month: 'short', 
          day: 'numeric' 
        });
      } catch (error) {
        console.error('Error formatting date:', error);
        return 'Invalid Date';
      }
    };
    
    // Format date range for display
    const formatDateRange = (start: Date | string, end: Date | string): string => {
      return `${formatDate(start)} - ${formatDate(end)}`;
    };
    
    // Format currency
    const formatCurrency = (value: number): string => {
      try {
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD', // Default currency
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }).format(value);
      } catch (error) {
        console.error('Error formatting currency:', error);
        return '$0.00';
      }
    };

    // Generate financial statement report
    const generateReport = async () => {
      generating.value = true;
      try {
        // Update report params with current date range
        const reportParams = {
          report_type: activeTab.value,
          period: 'year',
          start_date: dateRange.value.start.toISOString().split('T')[0],
          end_date: dateRange.value.end.toISOString().split('T')[0],
          format: selectedExportFormat.value,
          currency: 'USD'
        };
        
        // Call API to generate report
        const response = await axios.get('/api/gl/financial-statements', {
          params: reportParams,
          responseType: 'blob'
        });
        
        // Fetch financial statements
        const fetchFinancialStatements = async () => {
          if (!dateRange.value.start || !dateRange.value.end) return;
          
          loading.value = true;
          
          try {
            // Convert dates to ISO strings for the API
            const params = {
              start_date: dateRange.value.start instanceof Date 
                ? dateRange.value.start.toISOString().split('T')[0]
                : dateRange.value.start,
              end_date: dateRange.value.end instanceof Date
                ? dateRange.value.end.toISOString().split('T')[0]
                : dateRange.value.end
            };
            
            // TODO: Replace with actual API calls
            // const response = await glStore.fetchFinancialStatements(params);
            // balanceSheetData.value = response.balanceSheet;
            // incomeStatementData.value = response.incomeStatement;
            // cashFlowData.value = response.cashFlow;
            
            // Mock data for now
            balanceSheetData.value = {
              assets: [
                { account: 'Cash', amount: 10000 },
                { account: 'Accounts Receivable', amount: 5000 },
                { account: 'Total Assets', amount: 15000, isHeader: true }
              ],
              liabilities: [
                { account: 'Accounts Payable', amount: 3000 },
                { account: 'Total Liabilities', amount: 3000, isHeader: true }
              ],
              equity: [
                { account: 'Retained Earnings', amount: 12000 },
                { account: 'Total Equity', amount: 12000, isHeader: true }
              ],
              totalAssets: 15000,
              totalLiabilities: 3000,
              totalEquity: 12000,
              asOfDate: new Date().toISOString()
            };
            
            incomeStatementData.value = {
              revenues: [
                { account: 'Sales', amount: 50000 },
                { account: 'Total Revenue', amount: 50000, isHeader: true }
              ],
              expenses: [
                { account: 'Cost of Goods Sold', amount: 30000 },
                { account: 'Operating Expenses', amount: 15000 },
                { account: 'Total Expenses', amount: 45000, isHeader: true }
              ],
              grossProfit: 20000,
              operatingIncome: 5000,
              netIncome: 5000,
              period: formatDateRange(dateRange.value.start, dateRange.value.end)
            };
            
            cashFlowData.value = {
              operatingActivities: [
                { activity: 'Net Income', amount: 5000 },
                { activity: 'Depreciation', amount: 2000 },
                { activity: 'Net Cash from Operations', amount: 7000, isHeader: true }
              ],
              investingActivities: [
                { activity: 'Capital Expenditures', amount: -3000 },
                { activity: 'Net Cash from Investing', amount: -3000, isHeader: true }
              ],
              financingActivities: [
                { activity: 'Debt Issued', amount: 2000 },
                { activity: 'Net Cash from Financing', amount: 2000, isHeader: true }
              ],
              netCashFlow: 6000,
              cashBeginning: 4000,
              cashEnd: 10000,
              period: formatDateRange(dateRange.value.start, dateRange.value.end)
            };
            
          } catch (error) {
            console.error('Error fetching financial statements:', error);
            toast.error('Failed to load financial statements');
          } finally {
            loading.value = false;
          }
        };
        
        // Export statement to selected format
        const exportStatement = (format: ExportFormat) => {
          switch (format) {
            case 'pdf':
              exportToPdf(activeTab.value);
              break;
            case 'excel':
              // TODO: Implement Excel export
              toast.info('Export to Excel coming soon');
              break;
            case 'csv':
              // TODO: Implement CSV export
              toast.info('Export to CSV coming soon');
              break;
            default:
              toast.error('Unsupported export format');
          }
        };
        
        // Export to PDF
        const exportToPdf = (reportType: ReportType) => {
          try {
            const doc = new jsPDF();
            const title = reportType.split('-').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
            
            // Add title and date range
            doc.setFontSize(16);
            doc.text(`${title} Report`, 14, 20);
            doc.setFontSize(10);
            doc.text(`Period: ${formatDateRange(dateRange.value.start, dateRange.value.end)}`, 14, 30);
            
            // Add content based on report type
            let yPos = 50;
            
            switch (reportType) {
              case 'balance-sheet':
                if (balanceSheetData.value) {
                  // Add Assets
                  doc.setFontSize(12);
                  doc.text('Assets', 14, yPos);
                  yPos += 10;
                  
                  balanceSheetData.value.assets.forEach(item => {
                    doc.setFont(item.isHeader ? 'bold' : 'normal');
                    doc.text(item.account, 20, yPos);
                    doc.text(formatCurrency(item.amount), 150, yPos, { align: 'right' });
                    yPos += 10;
                  });
                  
                  // Add Liabilities
                  yPos += 10;
                  doc.setFontSize(12);
                  doc.text('Liabilities', 14, yPos);
                  yPos += 10;
                  
                  balanceSheetData.value.liabilities.forEach(item => {
                    doc.setFont(item.isHeader ? 'bold' : 'normal');
                    doc.text(item.account, 20, yPos);
                    doc.text(formatCurrency(item.amount), 150, yPos, { align: 'right' });
                    yPos += 10;
                  });
                  
                  // Add Equity
                  yPos += 10;
                  doc.setFontSize(12);
                  doc.text('Equity', 14, yPos);
                  yPos += 10;
                  
                  balanceSheetData.value.equity.forEach(item => {
                    doc.setFont(item.isHeader ? 'bold' : 'normal');
                    doc.text(item.account, 20, yPos);
                    doc.text(formatCurrency(item.amount), 150, yPos, { align: 'right' });
                    yPos += 10;
                  });
                  
                  // Add totals
                  yPos += 10;
                  doc.setFont('bold');
                  doc.text('Total Assets', 20, yPos);
                  doc.text(formatCurrency(balanceSheetData.value.totalAssets), 150, yPos, { align: 'right' });
                  
                  yPos += 10;
                  doc.text('Total Liabilities & Equity', 20, yPos);
                  doc.text(
                    formatCurrency(balanceSheetData.value.totalLiabilities + balanceSheetData.value.totalEquity), 
                    150, 
                    yPos, 
                    { align: 'right' }
                  );
                }
                break;
                
              // Add cases for other report types (income statement, cash flow)
              
              default:
                doc.text('Report type not supported', 14, yPos);
            }
            
            // Save the PDF
            doc.save(`${title.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`);
            
            toast.success('Report exported successfully');
          } catch (error) {
            console.error('Error exporting to PDF:', error);
            toast.error('Failed to export report');
          }
        };
        
        // Watch for date range changes
        watch(() => [dateRange.value.start, dateRange.value.end], () => {
          if (dateRange.value.start && dateRange.value.end) {
            fetchFinancialStatements();
          }
        }, { immediate: true });
        
        // Initial data fetch
        onMounted(() => {
          fetchFinancialStatements();
        });
        
        return {
          balanceSheet,
          incomeStatement,
          cashFlowStatement,
          trialBalance,
          exportFormats,
          selectedExportFormat,
          formatDate,
          formatCurrency,
          exportStatement
        };
      } catch (error) {
        console.error('Error generating report:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to generate report',
          life: 3000
        });
      } finally {
        generating.value = false;
      }
      formatDate,
      formatCurrency,
      exportStatement
    };
  } catch (error) {
    console.error('Error generating report:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to generate report',
      life: 3000
    });
  } finally {
    generating.value = false;
      balanceSheetData,
      incomeStatementData,
      cashFlowData,
      totalAssets,
      totalLiabilitiesEquity,
      netIncome,
      netCashFlow,
      cashBeginning,
      cashEnd,
      formatDate,
      formatDateRange,
      formatCurrency,
      generateReport,
      exportToPdf,
      updateDateRange
    };
  }
};
</script>

<style scoped>
:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 1rem;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background-color: #f8f9fa;
}

.border-top-1 {
  border-top: 1px solid #e5e7eb;
}

.border-gray-300 {
  border-color: #e5e7eb;
}

.text-green-600 {
  color: #059669;
}

.text-red-600 {
  color: #dc2626;
}

.text-gray-600 {
  color: #4b5563;
}

.h-full {
  height: 100%;
}
</style>
