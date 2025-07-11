<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12" md="4">
        <v-card elevation="2" class="mb-6">
          <v-card-title class="font-weight-bold">Receivables Summary</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="6">
                <v-stat-card title="Total Invoices" :value="summary.totalInvoices" color="primary" />
              </v-col>
              <v-col cols="6">
                <v-stat-card title="Outstanding" :value="formatCurrency(summary.outstanding)" color="error" />
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="6">
                <v-stat-card title="Paid" :value="formatCurrency(summary.paid)" color="success" />
              </v-col>
              <v-col cols="6">
                <v-stat-card title="Overdue" :value="formatCurrency(summary.overdue)" color="warning" />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="8">
        <v-card elevation="2" class="mb-6">
          <v-card-title class="font-weight-bold">Aging Report</v-card-title>
          <v-card-text>
            <v-data-table :headers="agingHeaders" :items="agingReport" class="elevation-1" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { fetchAgingReport, fetchInvoices } from '@/services/accountsReceivableService';

const summary = ref({ totalInvoices: 0, outstanding: 0, paid: 0, overdue: 0 });
const agingReport = ref([]);
const agingHeaders = [
  { text: 'Customer', value: 'customer_name' },
  { text: 'Current', value: 'current' },
  { text: '1-30 Days', value: 'days_1_30' },
  { text: '31-60 Days', value: 'days_31_60' },
  { text: '61-90 Days', value: 'days_61_90' },
  { text: 'Over 90 Days', value: 'days_over_90' },
  { text: 'Total', value: 'total' },
];
function formatCurrency(amount: number) {
  return `$${amount?.toFixed(2)}`;
}
onMounted(async () => {
  const { data: invoices } = await fetchInvoices();
  summary.value.totalInvoices = invoices.length;
  summary.value.outstanding = invoices.filter((i: any) => i.status !== 'PAID').reduce((sum: number, i: any) => sum + i.balance_due, 0);
  summary.value.paid = invoices.filter((i: any) => i.status === 'PAID').reduce((sum: number, i: any) => sum + i.total_amount, 0);
  summary.value.overdue = invoices.filter((i: any) => i.status === 'OVERDUE').reduce((sum: number, i: any) => sum + i.balance_due, 0);
  const { data: aging } = await fetchAgingReport();
  agingReport.value = aging;
});
</script>
