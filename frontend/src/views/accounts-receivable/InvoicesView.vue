<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12">
        <v-card elevation="2" class="mb-6">
          <v-card-title class="d-flex align-center justify-space-between">
            <span class="text-h5 font-weight-bold">Invoices</span>
            <v-btn color="primary" @click="openInvoiceForm">
              <v-icon left>mdi-plus</v-icon> New Invoice
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="invoices"
              :loading="loading"
              class="elevation-1"
              :items-per-page="10"
              :search="search"
              :footer-props="{ 'items-per-page-options': [10, 25, 50, 100] }"
            >
              <template v-slot:item.status="{ item }">
                <v-chip :color="statusColor(item.status)" dark>{{ item.status }}</v-chip>
              </template>
              <template v-slot:item.total_amount="{ item }">
                {{ formatCurrency(item.total_amount) }}
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn icon @click="viewInvoice(item)"><v-icon>mdi-eye</v-icon></v-btn>
                <v-btn icon @click="editInvoice(item)"><v-icon>mdi-pencil</v-icon></v-btn>
                <v-btn icon color="error" @click="deleteInvoice(item)"><v-icon>mdi-delete</v-icon></v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <!-- Invoice Form Dialog (modern, responsive) -->
    <InvoiceForm v-model="showInvoiceForm" :invoice="selectedInvoice" @saved="fetchInvoices" />
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { fetchInvoices, deleteInvoice } from '@/services/accountsReceivableService';
import InvoiceForm from './InvoiceForm.vue';

const invoices = ref([]);
const loading = ref(false);
const search = ref('');
const showInvoiceForm = ref(false);
const selectedInvoice = ref(null);

const headers = [
  { text: 'Invoice #', value: 'invoice_number', sortable: true },
  { text: 'Customer', value: 'customer_name', sortable: true },
  { text: 'Issue Date', value: 'issue_date', sortable: true },
  { text: 'Due Date', value: 'due_date', sortable: true },
  { text: 'Status', value: 'status', sortable: true },
  { text: 'Total', value: 'total_amount', sortable: true },
  { text: 'Actions', value: 'actions', sortable: false },
];

function statusColor(status: string) {
  switch (status) {
    case 'PAID': return 'green';
    case 'OVERDUE': return 'red';
    case 'DRAFT': return 'grey';
    default: return 'primary';
  }
}
function formatCurrency(amount: number) {
  return `$${amount.toFixed(2)}`;
}
function openInvoiceForm() {
  selectedInvoice.value = null;
  showInvoiceForm.value = true;
}
function viewInvoice(invoice: any) {
  // Route to detail view
}
function editInvoice(invoice: any) {
  selectedInvoice.value = invoice;
  showInvoiceForm.value = true;
}
async function deleteInvoice(invoice: any) {
  await deleteInvoice(invoice.id);
  fetchInvoices();
}
async function fetchInvoices() {
  loading.value = true;
  const { data } = await fetchInvoices();
  invoices.value = data;
  loading.value = false;
}
onMounted(fetchInvoices);
</script>

<style scoped>
.v-data-table {
  font-size: 1rem;
}
.v-card-title {
  background: linear-gradient(90deg, #1976d2 0%, #42a5f5 100%);
  color: white;
}
</style>
