<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12">
        <v-card elevation="2" class="mb-6">
          <v-card-title class="d-flex align-center justify-space-between">
            <span class="text-h5 font-weight-bold">Bills</span>
            <v-btn color="primary" @click="openBillForm">
              <v-icon left>mdi-plus</v-icon> New Bill
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="bills"
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
                <v-btn icon @click="viewBill(item)"><v-icon>mdi-eye</v-icon></v-btn>
                <v-btn icon @click="editBill(item)"><v-icon>mdi-pencil</v-icon></v-btn>
                <v-btn icon color="error" @click="deleteBill(item)"><v-icon>mdi-delete</v-icon></v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <!-- Bill Form Dialog (modern, responsive) -->
    <BillForm v-model="showBillForm" :bill="selectedBill" @saved="fetchBills" />
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { fetchBills, deleteBill } from '@/services/accountsPayableService';
import BillForm from './BillForm.vue';

const bills = ref([]);
const loading = ref(false);
const search = ref('');
const showBillForm = ref(false);
const selectedBill = ref(null);

const headers = [
  { text: 'Bill #', value: 'bill_number', sortable: true },
  { text: 'Vendor', value: 'vendor_name', sortable: true },
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
function openBillForm() {
  selectedBill.value = null;
  showBillForm.value = true;
}
function viewBill(bill: any) {
  // Route to detail view
}
function editBill(bill: any) {
  selectedBill.value = bill;
  showBillForm.value = true;
}
async function deleteBill(bill: any) {
  await deleteBill(bill.id);
  fetchBills();
}
async function fetchBills() {
  loading.value = true;
  const { data } = await fetchBills();
  bills.value = data;
  loading.value = false;
}
onMounted(fetchBills);
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
