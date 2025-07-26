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
import { accountsApi, journalEntriesApi } from '@/services/api';
import { useLoadingState } from '@/composables/useStateManagement';

const formatCurrency = (value: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
const formatDate = (date: Date) => new Intl.DateTimeFormat('en-US').format(date);

const router = useRouter();
const { setLoading, setError } = useLoadingState();

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

// Real data from API
const today = new Date();
const assetsTotal = ref(0);
const liabilitiesTotal = ref(0);
const equityTotal = ref(0);
const netIncome = ref(0);
const recentEntries = ref([]);
const accountBalances = ref([]);

const netIncomeClass = computed(() => ({
  'text-success': netIncome.value >= 0,
  'text-error': netIncome.value < 0
}));

function viewJournalEntry() {
  // Navigate to journal entry detail view
  router.push('/gl/journal-entries');
}

// Fetch data from API
const fetchDashboardData = async () => {
  try {
    setLoading(true);
    
    // Fetch accounts and calculate totals
    const accountsResponse = await accountsApi.getAll();
    const accounts = accountsResponse.items || [];
    
    accountBalances.value = accounts.map(account => ({
      id: account.id,
      name: account.name,
      balance: account.balance || 0
    }));
    
    // Calculate totals by account type
    assetsTotal.value = accounts
      .filter(acc => acc.account_type === 'asset')
      .reduce((sum, acc) => sum + (acc.balance || 0), 0);
    
    liabilitiesTotal.value = accounts
      .filter(acc => acc.account_type === 'liability')
      .reduce((sum, acc) => sum + (acc.balance || 0), 0);
    
    equityTotal.value = accounts
      .filter(acc => acc.account_type === 'equity')
      .reduce((sum, acc) => sum + (acc.balance || 0), 0);
    
    // Fetch recent journal entries
    const entriesResponse = await journalEntriesApi.getAll({ limit: 5, sort: '-entry_date' });
    recentEntries.value = (entriesResponse.items || []).map(entry => ({
      id: entry.id,
      date: new Date(entry.entry_date),
      reference: entry.entry_number,
      description: entry.description,
      total: entry.total_debit || entry.total_credit || 0
    }));
    
    // Calculate net income (revenue - expenses)
    const revenue = accounts
      .filter(acc => acc.account_type === 'revenue')
      .reduce((sum, acc) => sum + (acc.balance || 0), 0);
    
    const expenses = accounts
      .filter(acc => acc.account_type === 'expense')
      .reduce((sum, acc) => sum + (acc.balance || 0), 0);
    
    netIncome.value = revenue - expenses;
    
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    setError('Failed to load dashboard data');
  } finally {
    setLoading(false);
  }
};

// Fetch data when component mounts
onMounted(() => {
  fetchDashboardData();
});
</script>

<style scoped>
.v-card {
  height: 100%;
}
</style>
