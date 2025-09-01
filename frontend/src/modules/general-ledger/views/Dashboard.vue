<template>
  <div class="gl-dashboard">
    <div class="dashboard-header">
      <h1>General Ledger Dashboard</h1>
      <p>Welcome to the General Ledger module. This dashboard provides an overview of your financial data.</p>
    </div>
      
    <!-- Quick Actions -->
    <Card class="quick-actions-card">
      <template #title>
        <div class="card-title">
          <i class="pi pi-bolt"></i>
          <span>Quick Actions</span>
        </div>
      </template>
      <template #content>
        <div class="quick-actions-grid">
          <Button 
            label="New Journal Entry" 
            icon="pi pi-plus" 
            class="p-button-outlined action-btn"
            @click="$router.push('/accounting/journal-entry')"
          />
          <Button 
            label="Chart of Accounts" 
            icon="pi pi-list" 
            class="p-button-outlined action-btn"
            @click="$router.push('/gl/chart-of-accounts')"
          />
          <Button 
            label="Trial Balance" 
            icon="pi pi-calculator" 
            class="p-button-outlined action-btn"
            @click="$router.push('/gl/trial-balance')"
          />
          <Button 
            label="General Ledger Report" 
            icon="pi pi-file-text" 
            class="p-button-outlined action-btn"
            @click="$router.push('/gl/general-ledger-report')"
          />
          <Button 
            label="Account Reconciliation" 
            icon="pi pi-check-circle" 
            class="p-button-outlined action-btn"
            @click="$router.push('/gl/reconciliation')"
          />
          <Button 
            label="Financial Statements" 
            icon="pi pi-chart-bar" 
            class="p-button-outlined action-btn"
            @click="$router.push('/gl/financial-statements')"
          />
          <Button 
            label="Period Close" 
            icon="pi pi-lock" 
            class="p-button-outlined action-btn"
            @click="$router.push('/gl/period-close')"
          />
          <Button 
            label="Budget vs Actual" 
            icon="pi pi-chart-line" 
            class="p-button-outlined action-btn"
            @click="$router.push('/gl/budget-actual')"
          />
        </div>
      </template>
    </Card>

    <!-- Summary Cards -->
    <div class="summary-cards">
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-wallet text-blue"></i>
            <span>Total Assets</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-blue">{{ formatCurrency(assetsTotal) }}</div>
          <div class="summary-date">as of {{ formatDate(today) }}</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-credit-card text-red"></i>
            <span>Total Liabilities</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-red">{{ formatCurrency(liabilitiesTotal) }}</div>
          <div class="summary-date">as of {{ formatDate(today) }}</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-chart-line text-green"></i>
            <span>Equity</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-green">{{ formatCurrency(equityTotal) }}</div>
          <div class="summary-date">as of {{ formatDate(today) }}</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-chart-bar" :class="netIncome >= 0 ? 'text-green' : 'text-red'"></i>
            <span>Net Income (MTD)</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount" :class="netIncome >= 0 ? 'text-green' : 'text-red'">
            {{ formatCurrency(netIncome) }}
          </div>
          <div class="summary-date">Month to Date</div>
        </template>
      </Card>
    </div>
      
    <!-- Main Content Area -->
    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Recent Journal Entries</span>
            <Button 
              label="View All" 
              icon="pi pi-arrow-right" 
              iconPos="right" 
              class="p-button-text p-button-sm" 
              @click="viewJournalEntry" 
            />
          </div>
        </template>
        <template #content>
          <DataTable 
            :value="recentEntries" 
            :rows="5" 
            :paginator="false"
            responsiveLayout="scroll"
          >
            <Column field="date" header="Date">
              <template #body="{ data }">
                <span>{{ formatDate(data.date) }}</span>
              </template>
            </Column>
            <Column field="reference" header="Reference" />
            <Column field="description" header="Description" />
            <Column field="total" header="Amount">
              <template #body="{ data }">
                <span :class="data.total >= 0 ? 'text-green' : 'text-red'">
                  {{ formatCurrency(data.total) }}
                </span>
              </template>
            </Column>
            <Column header="Actions">
              <template #body>
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-rounded p-button-text p-button-sm" 
                  @click="viewJournalEntry" 
                />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Top Accounts</span>
            <Button 
              label="View All" 
              icon="pi pi-arrow-right" 
              iconPos="right" 
              class="p-button-text p-button-sm" 
              @click="$router.push('/gl/chart-of-accounts')" 
            />
          </div>
        </template>
        <template #content>
          <DataTable 
            :value="topAccounts" 
            :paginator="false"
            responsiveLayout="scroll"
          >
            <Column field="name" header="Account">
              <template #body="{ data }">
                <div class="account-item">
                  <div class="account-indicator" :class="getAccountTypeColor(data.account_type)"></div>
                  <span>{{ data.name }}</span>
                </div>
              </template>
            </Column>
            <Column field="balance" header="Balance">
              <template #body="{ data }">
                <span :class="data.balance >= 0 ? 'text-green' : 'text-red'">
                  {{ formatCurrency(data.balance) }}
                </span>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// import { accountsApi, journalEntriesApi } from '@/services/api';
import { useLoadingState } from '@/composables/useStateManagement';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';

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

// Get top 5 accounts by absolute balance
const topAccounts = computed(() => {
  return [...accountBalances.value]
    .sort((a, b) => Math.abs(b.balance) - Math.abs(a.balance))
    .slice(0, 5);
});

// Get color based on account type
const getAccountTypeColor = (type) => {
  const colors = {
    asset: 'bg-blue-500',
    liability: 'bg-red-500',
    equity: 'bg-green-500',
    revenue: 'bg-teal-500',
    expense: 'bg-amber-500',
  };
  return colors[type] || 'bg-gray-500';
};

const netIncomeClass = computed(() => ({
  'text-green-500': netIncome.value >= 0,
  'text-red-500': netIncome.value < 0
}));

function viewJournalEntry() {
  // Navigate to journal entry view
  router.push('/accounting/journal-entry');
}

// Load mock data
const fetchDashboardData = async () => {
  try {
    setLoading(true);
    
    // Mock data
    const accounts = [
      { id: 1, name: 'Cash', balance: 50000, account_type: 'asset' },
      { id: 2, name: 'Accounts Receivable', balance: 25000, account_type: 'asset' },
      { id: 3, name: 'Inventory', balance: 75000, account_type: 'asset' },
      { id: 4, name: 'Accounts Payable', balance: 15000, account_type: 'liability' },
      { id: 5, name: 'Owner Equity', balance: 100000, account_type: 'equity' },
      { id: 6, name: 'Sales Revenue', balance: 45000, account_type: 'revenue' },
      { id: 7, name: 'Office Expenses', balance: 8000, account_type: 'expense' }
    ];
    
    accountBalances.value = accounts;
    
    // Calculate totals by account type
    assetsTotal.value = accounts
      .filter(acc => acc.account_type === 'asset')
      .reduce((sum, acc) => sum + acc.balance, 0);
    
    liabilitiesTotal.value = accounts
      .filter(acc => acc.account_type === 'liability')
      .reduce((sum, acc) => sum + acc.balance, 0);
    
    equityTotal.value = accounts
      .filter(acc => acc.account_type === 'equity')
      .reduce((sum, acc) => sum + acc.balance, 0);
    
    // Mock recent journal entries
    recentEntries.value = [
      { id: 1, date: new Date(), reference: 'JE-001', description: 'Office supplies purchase', total: 500 },
      { id: 2, date: new Date(), reference: 'JE-002', description: 'Client payment received', total: 2500 },
      { id: 3, date: new Date(), reference: 'JE-003', description: 'Rent payment', total: -1200 },
      { id: 4, date: new Date(), reference: 'JE-004', description: 'Equipment purchase', total: -5000 },
      { id: 5, date: new Date(), reference: 'JE-005', description: 'Service revenue', total: 3000 }
    ];
    
    // Calculate net income (revenue - expenses)
    const revenue = accounts
      .filter(acc => acc.account_type === 'revenue')
      .reduce((sum, acc) => sum + acc.balance, 0);
    
    const expenses = accounts
      .filter(acc => acc.account_type === 'expense')
      .reduce((sum, acc) => sum + acc.balance, 0);
    
    netIncome.value = revenue - expenses;
    
  } catch (error) {
    console.error('Error loading dashboard data:', error);
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
.gl-dashboard {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.dashboard-header p {
  color: #6b7280;
  margin: 0;
}

.quick-actions-card {
  margin-bottom: 2rem;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.card-title i {
  color: #3b82f6;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-btn {
  width: 100%;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  height: 100%;
}

.summary-amount {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.summary-date {
  font-size: 0.75rem;
  color: #6b7280;
}

.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.content-card {
  height: fit-content;
}

.card-title-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.account-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.account-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.text-blue { color: #3b82f6; }
.text-red { color: #ef4444; }
.text-green { color: #10b981; }

.bg-blue-500 { background-color: #3b82f6; }
.bg-red-500 { background-color: #ef4444; }
.bg-green-500 { background-color: #10b981; }
.bg-teal-500 { background-color: #14b8a6; }
.bg-amber-500 { background-color: #f59e0b; }
.bg-gray-500 { background-color: #6b7280; }

@media (max-width: 768px) {
  .gl-dashboard {
    padding: 1rem;
  }
  
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>
