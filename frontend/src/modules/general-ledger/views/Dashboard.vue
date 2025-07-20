<template>
  <div class="gl-dashboard">
    <div class="grid">
      <div class="col-12">
        <h1>General Ledger Dashboard</h1>
        <p>Welcome to the General Ledger module. This dashboard provides an overview of your financial data.</p>
      </div>
      
      <!-- Summary Cards -->
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #title>Total Assets</template>
          <template #content>
            <div class="text-4xl font-bold text-primary">{{ formatCurrency(assetsTotal) }}</div>
            <div class="mt-2 text-sm text-500">as of {{ formatDate(today) }}</div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #title>Total Liabilities</template>
          <template #content>
            <div class="text-4xl font-bold text-red-500">{{ formatCurrency(liabilitiesTotal) }}</div>
            <div class="mt-2 text-sm text-500">as of {{ formatDate(today) }}</div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:3">
        <Card>
          <template #title>Equity</template>
          <template #content>
            <div class="text-4xl font-bold text-green-500">{{ formatCurrency(equityTotal) }}</div>
            <div class="mt-2 text-sm text-500">as of {{ formatDate(today) }}</div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-6 lg:3">
        <Card>
          <template #title>Net Income (MTD)</template>
          <template #content>
            <div class="text-4xl font-bold" :class="netIncomeClass">
              {{ formatCurrency(netIncome) }}
            </div>
            <div class="mt-2 text-sm text-500">Month to Date</div>
          </template>
        </Card>
      </div>
      
      <!-- Recent Journal Entries -->
      <div class="col-12 lg:8">
        <Card>
          <template #title>Recent Journal Entries</template>
          <template #content>
            <DataTable :value="recentEntries" :rows="5" :paginator="true" class="p-datatable-sm">
              <Column field="date" header="Date" style="width: 120px">
                <template #body="{ data }">
                  {{ formatDate(data.date) }}
                </template>
              </Column>
              <Column field="reference" header="Reference" style="width: 120px" />
              <Column field="description" header="Description" />
              <Column field="total" header="Amount" style="width: 150px">
                <template #body="{ data }">
                  {{ formatCurrency(data.total) }}
                </template>
              </Column>
              <Column headerStyle="width: 4rem; text-align: center" bodyStyle="text-align: center; overflow: visible">
                <template #body>
                  <Button icon="pi pi-eye" class="p-button-text" @click="viewJournalEntry" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
      
      <!-- Account Balances -->
      <div class="col-12 lg:4">
        <Card>
          <template #title>Account Balances</template>
          <template #content>
            <DataTable :value="accountBalances" :scrollable="true" scrollHeight="300px" class="p-datatable-sm">
              <Column field="name" header="Account" />
              <Column field="balance" header="Balance" style="width: 120px">
                <template #body="{ data }">
                  {{ formatCurrency(data.balance) }}
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import { useFormatting } from '@/composables/useFormatting';

const { formatCurrency, formatDate } = useFormatting();
const router = useRouter();

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
  'text-green-500': netIncome.value >= 0,
  'text-red-500': netIncome.value < 0
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
.gl-dashboard {
  padding: 1rem;
}

:deep(.p-card) {
  height: 100%;
}

:deep(.p-card .p-card-title) {
  font-size: 1.15rem;
  margin-bottom: 0.75rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  padding: 0.5rem 1rem;
  background: #f8f9fa;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 1rem;
}
</style>
