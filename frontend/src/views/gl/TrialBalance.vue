<template>
  <div class="trial-balance">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>Trial Balance</h1>
            <p>View account balances and verify accounting equation</p>
          </div>
          <div class="header-actions">
            <select v-model="selectedPeriod" class="period-select">
              <option value="current">Current Month</option>
              <option value="ytd">Year to Date</option>
              <option value="custom">Custom Period</option>
            </select>
            <button class="btn btn-primary" @click="exportReport">Export PDF</button>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Summary Cards -->
      <div class="summary-section">
        <div class="summary-grid">
          <div class="summary-card">
            <h3>Total Debits</h3>
            <div class="amount">{{ formatCurrency(totals.debits) }}</div>
          </div>
          <div class="summary-card">
            <h3>Total Credits</h3>
            <div class="amount">{{ formatCurrency(totals.credits) }}</div>
          </div>
          <div class="summary-card" :class="{ 'balanced': isBalanced }">
            <h3>Difference</h3>
            <div class="amount">{{ formatCurrency(totals.difference) }}</div>
            <div class="status">{{ isBalanced ? 'Balanced' : 'Out of Balance' }}</div>
          </div>
        </div>
      </div>

      <!-- Trial Balance Table -->
      <div class="table-card">
        <div class="table-header">
          <h3>Trial Balance Report</h3>
          <div class="report-date">
            As of {{ formatDate(reportDate) }}
          </div>
        </div>
        
        <div class="table-container">
          <table class="trial-balance-table">
            <thead>
              <tr>
                <th>Account Code</th>
                <th>Account Name</th>
                <th>Account Type</th>
                <th class="amount-col">Debit Balance</th>
                <th class="amount-col">Credit Balance</th>
              </tr>
            </thead>
            <tbody>
              <!-- Assets -->
              <tr class="category-header">
                <td colspan="5"><strong>ASSETS</strong></td>
              </tr>
              <tr v-for="account in assetAccounts" :key="account.id">
                <td>{{ account.code }}</td>
                <td>{{ account.name }}</td>
                <td>{{ account.type }}</td>
                <td class="amount-col">{{ account.balance > 0 ? formatCurrency(account.balance) : '-' }}</td>
                <td class="amount-col">{{ account.balance < 0 ? formatCurrency(Math.abs(account.balance)) : '-' }}</td>
              </tr>
              
              <!-- Liabilities -->
              <tr class="category-header">
                <td colspan="5"><strong>LIABILITIES</strong></td>
              </tr>
              <tr v-for="account in liabilityAccounts" :key="account.id">
                <td>{{ account.code }}</td>
                <td>{{ account.name }}</td>
                <td>{{ account.type }}</td>
                <td class="amount-col">{{ account.balance < 0 ? formatCurrency(Math.abs(account.balance)) : '-' }}</td>
                <td class="amount-col">{{ account.balance > 0 ? formatCurrency(account.balance) : '-' }}</td>
              </tr>
              
              <!-- Equity -->
              <tr class="category-header">
                <td colspan="5"><strong>EQUITY</strong></td>
              </tr>
              <tr v-for="account in equityAccounts" :key="account.id">
                <td>{{ account.code }}</td>
                <td>{{ account.name }}</td>
                <td>{{ account.type }}</td>
                <td class="amount-col">{{ account.balance < 0 ? formatCurrency(Math.abs(account.balance)) : '-' }}</td>
                <td class="amount-col">{{ account.balance > 0 ? formatCurrency(account.balance) : '-' }}</td>
              </tr>
              
              <!-- Revenue -->
              <tr class="category-header">
                <td colspan="5"><strong>REVENUE</strong></td>
              </tr>
              <tr v-for="account in revenueAccounts" :key="account.id">
                <td>{{ account.code }}</td>
                <td>{{ account.name }}</td>
                <td>{{ account.type }}</td>
                <td class="amount-col">{{ account.balance < 0 ? formatCurrency(Math.abs(account.balance)) : '-' }}</td>
                <td class="amount-col">{{ account.balance > 0 ? formatCurrency(account.balance) : '-' }}</td>
              </tr>
              
              <!-- Expenses -->
              <tr class="category-header">
                <td colspan="5"><strong>EXPENSES</strong></td>
              </tr>
              <tr v-for="account in expenseAccounts" :key="account.id">
                <td>{{ account.code }}</td>
                <td>{{ account.name }}</td>
                <td>{{ account.type }}</td>
                <td class="amount-col">{{ account.balance > 0 ? formatCurrency(account.balance) : '-' }}</td>
                <td class="amount-col">{{ account.balance < 0 ? formatCurrency(Math.abs(account.balance)) : '-' }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="totals-row">
                <td colspan="3"><strong>TOTALS</strong></td>
                <td class="amount-col"><strong>{{ formatCurrency(totals.debits) }}</strong></td>
                <td class="amount-col"><strong>{{ formatCurrency(totals.credits) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <!-- Accounting Equation Verification -->
      <div class="equation-card">
        <h3>Accounting Equation Verification</h3>
        <div class="equation">
          <div class="equation-part">
            <span class="label">Assets</span>
            <span class="amount">{{ formatCurrency(equationTotals.assets) }}</span>
          </div>
          <div class="equation-operator">=</div>
          <div class="equation-part">
            <span class="label">Liabilities</span>
            <span class="amount">{{ formatCurrency(equationTotals.liabilities) }}</span>
          </div>
          <div class="equation-operator">+</div>
          <div class="equation-part">
            <span class="label">Equity</span>
            <span class="amount">{{ formatCurrency(equationTotals.equity) }}</span>
          </div>
        </div>
        <div class="equation-status" :class="{ 'valid': equationBalanced }">
          {{ equationBalanced ? '✓ Equation Balanced' : '⚠ Equation Not Balanced' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const selectedPeriod = ref('current')
const reportDate = ref(new Date().toISOString().split('T')[0])

const accounts = ref([
  // Assets
  { id: 1, code: '1000', name: 'Cash', type: 'Current Asset', category: 'asset', balance: 50000 },
  { id: 2, code: '1200', name: 'Accounts Receivable', type: 'Current Asset', category: 'asset', balance: 25000 },
  { id: 3, code: '1500', name: 'Inventory', type: 'Current Asset', category: 'asset', balance: 75000 },
  { id: 4, code: '1700', name: 'Equipment', type: 'Fixed Asset', category: 'asset', balance: 100000 },
  
  // Liabilities
  { id: 5, code: '2000', name: 'Accounts Payable', type: 'Current Liability', category: 'liability', balance: 15000 },
  { id: 6, code: '2500', name: 'Notes Payable', type: 'Long-term Liability', category: 'liability', balance: 50000 },
  
  // Equity
  { id: 7, code: '3000', name: 'Owner\'s Capital', type: 'Equity', category: 'equity', balance: 150000 },
  { id: 8, code: '3200', name: 'Retained Earnings', type: 'Equity', category: 'equity', balance: 20000 },
  
  // Revenue
  { id: 9, code: '4000', name: 'Sales Revenue', type: 'Revenue', category: 'revenue', balance: 85000 },
  { id: 10, code: '4100', name: 'Service Revenue', type: 'Revenue', category: 'revenue', balance: 35000 },
  
  // Expenses
  { id: 11, code: '5000', name: 'Cost of Goods Sold', type: 'Expense', category: 'expense', balance: 45000 },
  { id: 12, code: '6000', name: 'Rent Expense', type: 'Expense', category: 'expense', balance: 12000 },
  { id: 13, code: '6100', name: 'Utilities Expense', type: 'Expense', category: 'expense', balance: 3000 }
])

const assetAccounts = computed(() => 
  accounts.value.filter(acc => acc.category === 'asset')
)

const liabilityAccounts = computed(() => 
  accounts.value.filter(acc => acc.category === 'liability')
)

const equityAccounts = computed(() => 
  accounts.value.filter(acc => acc.category === 'equity')
)

const revenueAccounts = computed(() => 
  accounts.value.filter(acc => acc.category === 'revenue')
)

const expenseAccounts = computed(() => 
  accounts.value.filter(acc => acc.category === 'expense')
)

const totals = computed(() => {
  let debits = 0
  let credits = 0
  
  accounts.value.forEach(account => {
    if (account.category === 'asset' || account.category === 'expense') {
      if (account.balance > 0) debits += account.balance
      else credits += Math.abs(account.balance)
    } else {
      if (account.balance > 0) credits += account.balance
      else debits += Math.abs(account.balance)
    }
  })
  
  return {
    debits,
    credits,
    difference: Math.abs(debits - credits)
  }
})

const isBalanced = computed(() => totals.value.difference === 0)

const equationTotals = computed(() => {
  const assets = assetAccounts.value.reduce((sum, acc) => sum + acc.balance, 0)
  const liabilities = liabilityAccounts.value.reduce((sum, acc) => sum + acc.balance, 0)
  const equity = equityAccounts.value.reduce((sum, acc) => sum + acc.balance, 0)
  
  return { assets, liabilities, equity }
})

const equationBalanced = computed(() => 
  Math.abs(equationTotals.value.assets - (equationTotals.value.liabilities + equationTotals.value.equity)) < 0.01
)

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const exportReport = () => {
  console.log('Exporting trial balance report...')
}

onMounted(() => {
  // Load trial balance data
})
</script>

<style scoped>
.trial-balance {
  min-height: 100vh;
  background: #f5f7fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e0e6ed;
  padding: 20px 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.header-content p {
  color: #718096;
  margin: 5px 0 0 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.period-select {
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #1976D2;
  color: white;
}

.summary-section {
  margin: 30px 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.summary-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.summary-card.balanced {
  border: 2px solid #38a169;
}

.summary-card h3 {
  margin: 0 0 12px 0;
  color: #4a5568;
  font-size: 1rem;
}

.summary-card .amount {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 8px;
}

.summary-card .status {
  font-size: 0.9rem;
  font-weight: 500;
  color: #38a169;
}

.table-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
  margin-bottom: 30px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.table-header h3 {
  margin: 0;
  color: #2d3748;
}

.report-date {
  color: #718096;
  font-weight: 500;
}

.trial-balance-table {
  width: 100%;
  border-collapse: collapse;
}

.trial-balance-table th,
.trial-balance-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f7fafc;
}

.trial-balance-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #4a5568;
}

.amount-col {
  text-align: right;
  font-weight: 500;
}

.category-header {
  background: #edf2f7;
}

.category-header td {
  font-weight: 600;
  color: #2d3748;
  padding: 16px;
}

.totals-row {
  background: #f8f9fa;
  border-top: 2px solid #e2e8f0;
}

.totals-row td {
  font-weight: 600;
  color: #2d3748;
}

.equation-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.equation-card h3 {
  margin: 0 0 20px 0;
  color: #2d3748;
}

.equation {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.equation-part {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.equation-part .label {
  font-size: 0.9rem;
  color: #718096;
  font-weight: 500;
}

.equation-part .amount {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2d3748;
}

.equation-operator {
  font-size: 1.5rem;
  font-weight: bold;
  color: #4a5568;
}

.equation-status {
  font-size: 1.1rem;
  font-weight: 600;
  padding: 12px 24px;
  border-radius: 8px;
  display: inline-block;
}

.equation-status.valid {
  background: #c6f6d5;
  color: #22543d;
}

.equation-status:not(.valid) {
  background: #fed7d7;
  color: #742a2a;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .equation {
    flex-direction: column;
    gap: 12px;
  }
  
  .equation-operator {
    transform: rotate(90deg);
  }
}
</style>