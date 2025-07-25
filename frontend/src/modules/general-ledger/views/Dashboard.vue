<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">General Ledger Dashboard</h1>
        <p class="text-subtitle-1 mb-6">Welcome to the General Ledger module. This dashboard provides an overview of your financial data.</p>
      </v-col>
      
      <!-- Summary Cards -->
      <v-col cols="12" md="6" lg="3">
        <v-card>
          <v-card-title>Total Assets</v-card-title>
          <v-card-text>
            <div class="text-h4 font-weight-bold text-primary">{{ formatCurrency(assetsTotal) }}</div>
            <div class="text-caption text-medium-emphasis mt-2">as of {{ formatDate(today) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6" lg="3">
        <v-card>
          <v-card-title>Total Liabilities</v-card-title>
          <v-card-text>
            <div class="text-h4 font-weight-bold text-error">{{ formatCurrency(liabilitiesTotal) }}</div>
            <div class="text-caption text-medium-emphasis mt-2">as of {{ formatDate(today) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6" lg="3">
        <v-card>
          <v-card-title>Equity</v-card-title>
          <v-card-text>
            <div class="text-h4 font-weight-bold text-success">{{ formatCurrency(equityTotal) }}</div>
            <div class="text-caption text-medium-emphasis mt-2">as of {{ formatDate(today) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6" lg="3">
        <v-card>
          <v-card-title>Net Income (MTD)</v-card-title>
          <v-card-text>
            <div class="text-h4 font-weight-bold" :class="netIncomeClass">
              {{ formatCurrency(netIncome) }}
            </div>
            <div class="text-caption text-medium-emphasis mt-2">Month to Date</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Recent Journal Entries -->
      <v-col cols="12" lg="8">
        <v-card>
          <v-card-title>Recent Journal Entries</v-card-title>
          <v-card-text>
            <v-data-table :items="recentEntries" :headers="journalHeaders" items-per-page="5">
              <template #item.date="{ item }">
                {{ formatDate(item.date) }}
              </template>
              <template #item.total="{ item }">
                {{ formatCurrency(item.total) }}
              </template>
              <template #item.actions="{ item }">
                <v-btn icon="mdi-eye" variant="text" size="small" @click="viewJournalEntry" />
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Account Balances -->
      <v-col cols="12" lg="4">
        <v-card>
          <v-card-title>Account Balances</v-card-title>
          <v-card-text>
            <v-data-table :items="accountBalances" :headers="balanceHeaders" height="300" items-per-page="-1">
              <template #item.balance="{ item }">
                {{ formatCurrency(item.balance) }}
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const formatCurrency = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
const formatDate = (date: Date) => new Intl.DateTimeFormat('en-US').format(date);

const router = useRouter();

const journalHeaders = [
  { title: 'Date', key: 'date' },
  { title: 'Reference', key: 'reference' },
  { title: 'Description', key: 'description' },
  { title: 'Amount', key: 'total' },
  { title: 'Actions', key: 'actions', sortable: false }
];

const balanceHeaders = [
  { title: 'Account', key: 'name' },
  { title: 'Balance', key: 'balance' }
];

// Mock data - replace with actual API calls
const today = new Date();
const assetsTotal = ref(1250000);
const liabilitiesTotal = ref(450000);
const equityTotal = ref(800000);
const netIncome = ref(125000);

const recentEntries = ref([
  { id: 1, date: new Date('2025-07-15'), reference: 'JE-2025-001', description: 'Monthly accrual', total: 12500.75 },
  { id: 2, date: new Date('2025-07-14'), reference: 'JE-2025-002', description: 'Depreciation', total: 3500.25 },
  { id: 3, date: new Date('2025-07-10'), reference: 'JE-2025-003', description: 'Bank charges', total: 125.50 },
  { id: 4, date: new Date('2025-07-05'), reference: 'JE-2025-004', description: 'Revenue recognition', total: 45200.00 },
  { id: 5, date: new Date('2025-07-01'), reference: 'JE-2025-005', description: 'Payroll accrual', total: 32500.00 },
]);

const accountBalances = ref([
  { id: 1, name: 'Cash and Cash Equivalents', balance: 450000 },
  { id: 2, name: 'Accounts Receivable', balance: 325000 },
  { id: 3, name: 'Inventory', balance: 275000 },
  { id: 4, name: 'Property, Plant & Equipment', balance: 200000 },
  { id: 5, name: 'Accounts Payable', balance: -175000 },
  { id: 6, name: 'Short-term Loans', balance: -125000 },
  { id: 7, name: 'Long-term Debt', balance: -150000 },
]);

const netIncomeClass = computed(() => ({
  'text-success': netIncome.value >= 0,
  'text-error': netIncome.value < 0
}));

function viewJournalEntry() {
  // Navigate to journal entry detail view
  router.push('/gl/journal-entries');
}

// Fetch data when component mounts
onMounted(() => {
  // TODO: Replace with actual API calls
  console.log('GL Dashboard mounted');
});
</script>

<style scoped>
.v-card {
  height: 100%;
}
</style>
