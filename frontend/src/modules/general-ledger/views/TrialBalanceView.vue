<template>
  <v-container fluid class="fill-height">
    <v-card class="flex-grow-1 d-flex flex-column">
      <v-card-title class="d-flex align-center">
        <span class="text-h5">Trial Balance</span>
        <v-spacer />
        <v-menu offset-y>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              color="primary"
              class="mr-2"
              v-bind="attrs"
              v-on="on"
            >
              <v-icon left>mdi-calendar-range</v-icon>
              {{ formatDateRange }}
            </v-btn>
          </template>
          <v-date-picker
            v-model="dateRange"
            range
            no-title
            scrollable
          ></v-date-picker>
        </v-menu>
        <v-btn
          color="primary"
          @click="exportToExcel"
          class="mr-2"
        >
          <v-icon left>mdi-microsoft-excel</v-icon>
          Export
        </v-btn>
        <v-btn
          color="primary"
          @click="refreshData"
        >
          <v-icon left>mdi-refresh</v-icon>
          Refresh
        </v-btn>
      </v-card-title>
      
      <v-card-text class="pa-0 flex-grow-1" style="height: 0;">
        <v-data-table
          :headers="headers"
          :items="trialBalanceItems"
          :loading="loading"
          :items-per-page="-1"
          hide-default-footer
          class="elevation-1 flex-grow-1"
          fixed-header
          height="100%"
          calculate-widths
        >
          <template v-slot:item.account_name="{ item }">
            <div :class="{ 'font-weight-bold': item.is_header }">
              {{ item.account_name }}
            </div>
          </template>
          
          <template v-slot:item.debit_balance="{ item }">
            <div :class="{ 'font-weight-bold': item.is_header }">
              {{ formatCurrency(item.debit_balance) }}
            </div>
          </template>
          
          <template v-slot:item.credit_balance="{ item }">
            <div :class="{ 'font-weight-bold': item.is_header }">
              {{ formatCurrency(item.credit_balance) }}
            </div>
          </template>
          
          <template v-slot:no-data>
            <div class="text-center py-4">
              <div class="mb-2">No trial balance data available</div>
              <v-btn
                color="primary"
                small
                @click="refreshData"
              >
                <v-icon left small>mdi-refresh</v-icon>
                Refresh Data
              </v-btn>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
      
      <v-card-actions class="px-4 py-3">
        <v-spacer />
        <div class="text-subtitle-1 mr-4">
          <span class="font-weight-bold">Total Debit:</span> {{ formatCurrency(totalDebit) }}
        </div>
        <div class="text-subtitle-1">
          <span class="font-weight-bold">Total Credit:</span> {{ formatCurrency(totalCredit) }}
        </div>
        <v-spacer />
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { format } from 'date-fns';

export default defineComponent({
  name: 'TrialBalanceView',
  
  setup() {
    const loading = ref(false);
    const dateRange = ref([
      new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().substr(0, 10),
      new Date().toISOString().substr(0, 10)
    ]);
    
    const trialBalanceItems = ref([
      // This would be populated from the API
      { id: 1, account_code: '1000', account_name: 'Assets', is_header: true, debit_balance: 0, credit_balance: 0 },
      { id: 2, account_code: '1100', account_name: 'Current Assets', is_header: true, debit_balance: 0, credit_balance: 0 },
      { id: 3, account_code: '1110', account_name: 'Cash and Cash Equivalents', is_header: false, debit_balance: 50000, credit_balance: 0 },
      { id: 4, account_code: '1120', account_name: 'Accounts Receivable', is_header: false, debit_balance: 25000, credit_balance: 0 },
      { id: 5, account_code: '2000', account_name: 'Liabilities', is_header: true, debit_balance: 0, credit_balance: 0 },
      { id: 6, account_code: '2100', account_name: 'Current Liabilities', is_header: true, debit_balance: 0, credit_balance: 0 },
      { id: 7, account_code: '2110', account_name: 'Accounts Payable', is_header: false, debit_balance: 0, credit_balance: 15000 },
      { id: 8, account_code: '3000', account_name: 'Equity', is_header: true, debit_balance: 0, credit_balance: 0 },
      { id: 9, account_code: '3100', account_name: 'Retained Earnings', is_header: false, debit_balance: 0, credit_balance: 60000 },
      { id: 10, account_code: '4000', account_name: 'Revenue', is_header: true, debit_balance: 0, credit_balance: 0 },
      { id: 11, account_code: '5000', account_name: 'Expenses', is_header: true, debit_balance: 0, credit_balance: 0 },
    ]);
    
    const headers = [
      { text: 'Account Code', value: 'account_code', width: '15%' },
      { text: 'Account Name', value: 'account_name', width: '55%' },
      { text: 'Debit (PKR)', value: 'debit_balance', align: 'right', width: '15%' },
      { text: 'Credit (PKR)', value: 'credit_balance', align: 'right', width: '15%' },
    ];
    
    const formatDateRange = computed(() => {
      if (dateRange.value.length === 2) {
        return `${format(new Date(dateRange.value[0]), 'MMM d, yyyy')} - ${format(new Date(dateRange.value[1]), 'MMM d, yyyy')}`;
      }
      return 'Select Date Range';
    });
    
    const totalDebit = computed(() => {
      return trialBalanceItems.value
        .filter(item => !item.is_header)
        .reduce((sum, item) => sum + (item.debit_balance || 0), 0);
    });
    
    const totalCredit = computed(() => {
      return trialBalanceItems.value
        .filter(item => !item.is_header)
        .reduce((sum, item) => sum + (item.credit_balance || 0), 0);
    });
    
    const formatCurrency = (value: number) => {
      if (value === 0) return '-';
      return new Intl.NumberFormat('en-PK', {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
    };
    
    const refreshData = async () => {
      try {
        loading.value = true;
        // TODO: Call API to get trial balance data
        // const response = await get(`/api/gl/trial-balance?start_date=${dateRange.value[0]}&end_date=${dateRange.value[1]}`);
        // trialBalanceItems.value = response.data;
      } catch (error) {
        console.error('Error loading trial balance:', error);
      } finally {
        loading.value = false;
      }
    };
    
    const exportToExcel = () => {
      // TODO: Implement Excel export
      console.log('Exporting to Excel...');
    };
    
    onMounted(() => {
      refreshData();
    });
    
    return {
      loading,
      dateRange,
      trialBalanceItems,
      headers,
      formatDateRange,
      totalDebit,
      totalCredit,
      formatCurrency,
      refreshData,
      exportToExcel,
    };
  },
});
</script>
