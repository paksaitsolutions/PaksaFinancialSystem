<template>
  <div class="chart-of-accounts">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>Chart of Accounts</h1>
            <p>Manage your chart of accounts structure</p>
          </div>
          <button class="btn btn-primary" @click="showCreateModal = true">
            + Add Account
          </button>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Filters -->
      <div class="filters-section">
        <div class="filters-grid">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search accounts..." 
            class="filter-input"
          >
          <select v-model="selectedType" class="filter-input">
            <option value="">All Types</option>
            <option v-for="type in accountTypes" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
          <select v-model="selectedCategory" class="filter-input">
            <option value="">All Categories</option>
            <option value="asset">Assets</option>
            <option value="liability">Liabilities</option>
            <option value="equity">Equity</option>
            <option value="revenue">Revenue</option>
            <option value="expense">Expenses</option>
          </select>
        </div>
      </div>

      <!-- Accounts Table -->
      <div class="table-card">
        <div class="table-header">
          <h3>Accounts ({{ filteredAccounts.length }})</h3>
          <div class="table-actions">
            <button class="btn btn-outline">Export</button>
            <button class="btn btn-outline">Import</button>
          </div>
        </div>
        
        <div class="table-container">
          <table class="accounts-table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Account Name</th>
                <th>Type</th>
                <th>Category</th>
                <th>Balance</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="account in filteredAccounts" :key="account.id">
                <td class="account-code">{{ account.code }}</td>
                <td class="account-name">{{ account.name }}</td>
                <td>{{ account.type }}</td>
                <td>
                  <span class="category-badge" :class="account.category">
                    {{ account.category }}
                  </span>
                </td>
                <td class="balance" :class="getBalanceClass(account.balance)">
                  {{ formatCurrency(account.balance) }}
                </td>
                <td>
                  <span class="status-badge" :class="account.status">
                    {{ account.status }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="btn-icon" @click="editAccount(account)" title="Edit">✏️</button>
                    <button class="btn-icon" @click="viewTransactions(account)" title="Transactions">📋</button>
                    <button class="btn-icon" @click="deleteAccount(account)" title="Delete">🗑️</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingAccount ? 'Edit' : 'Create' }} Account</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="saveAccount" class="account-form">
          <div class="form-grid">
            <div class="form-group">
              <label>Account Code *</label>
              <input 
                type="text" 
                v-model="accountForm.code" 
                required 
                class="form-input"
                placeholder="e.g., 1000"
              >
            </div>
            <div class="form-group">
              <label>Account Name *</label>
              <input 
                type="text" 
                v-model="accountForm.name" 
                required 
                class="form-input"
                placeholder="e.g., Cash"
              >
            </div>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label>Account Type *</label>
              <select v-model="accountForm.type" required class="form-input">
                <option value="">Select Type</option>
                <option v-for="type in accountTypes" :key="type" :value="type">
                  {{ type }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Category *</label>
              <select v-model="accountForm.category" required class="form-input">
                <option value="">Select Category</option>
                <option value="asset">Asset</option>
                <option value="liability">Liability</option>
                <option value="equity">Equity</option>
                <option value="revenue">Revenue</option>
                <option value="expense">Expense</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea 
              v-model="accountForm.description" 
              class="form-input" 
              rows="3"
              placeholder="Account description..."
            ></textarea>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label>Parent Account</label>
              <select v-model="accountForm.parentId" class="form-input">
                <option value="">None (Top Level)</option>
                <option v-for="account in parentAccounts" :key="account.id" :value="account.id">
                  {{ account.code }} - {{ account.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Status</label>
              <select v-model="accountForm.status" class="form-input">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Account</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const showCreateModal = ref(false)
const editingAccount = ref(null)
const searchQuery = ref('')
const selectedType = ref('')
const selectedCategory = ref('')

const accountTypes = [
  'Current Asset',
  'Fixed Asset',
  'Current Liability',
  'Long-term Liability',
  'Equity',
  'Revenue',
  'Cost of Goods Sold',
  'Operating Expense',
  'Other Income',
  'Other Expense'
]

const accountForm = ref({
  code: '',
  name: '',
  type: '',
  category: '',
  description: '',
  parentId: null,
  status: 'active'
})

const accounts = ref([
  // Assets
  { id: 1, code: '1010', name: 'Cash in Hand', type: 'Current Asset', category: 'asset', balance: 50000, status: 'active' },
  { id: 2, code: '1020', name: 'Cash in Bank - Local (PKR)', type: 'Current Asset', category: 'asset', balance: 2500000, status: 'active' },
  { id: 3, code: '1021', name: 'Cash in Bank - USD (International)', type: 'Current Asset', category: 'asset', balance: 150000, status: 'active' },
  { id: 4, code: '1022', name: 'Cash in Bank - SAR (KSA)', type: 'Current Asset', category: 'asset', balance: 75000, status: 'active' },
  { id: 5, code: '1030', name: 'Accounts Receivable (COD Payments Pending)', type: 'Current Asset', category: 'asset', balance: 125000, status: 'active' },
  { id: 6, code: '1031', name: 'COD Receivable - FedEx', type: 'Current Asset', category: 'asset', balance: 35000, status: 'active' },
  { id: 7, code: '1032', name: 'COD Receivable - DHL', type: 'Current Asset', category: 'asset', balance: 28000, status: 'active' },
  { id: 8, code: '1033', name: 'COD Receivable - TCS', type: 'Current Asset', category: 'asset', balance: 22000, status: 'active' },
  { id: 9, code: '1034', name: 'COD Receivable - LCS', type: 'Current Asset', category: 'asset', balance: 18000, status: 'active' },
  { id: 10, code: '1040', name: 'Inventory - Raw Materials (Fabric, Accessories)', type: 'Current Asset', category: 'asset', balance: 300000, status: 'active' },
  { id: 11, code: '1045', name: 'Inventory - Finished Goods (Products Ready for Sale)', type: 'Current Asset', category: 'asset', balance: 450000, status: 'active' },
  { id: 12, code: '1050', name: 'Prepaid Expenses (Logistics, Marketing Prepayments)', type: 'Current Asset', category: 'asset', balance: 85000, status: 'active' },
  { id: 13, code: '1200', name: 'Office Equipment', type: 'Fixed Asset', category: 'asset', balance: 120000, status: 'active' },
  { id: 14, code: '1220', name: 'Software Development Costs', type: 'Fixed Asset', category: 'asset', balance: 95000, status: 'active' },
  { id: 15, code: '1230', name: 'Vehicles (Logistics)', type: 'Fixed Asset', category: 'asset', balance: 180000, status: 'active' },
  
  // Liabilities
  { id: 16, code: '2010', name: 'Accounts Payable - Local Vendors', type: 'Current Liability', category: 'liability', balance: 180000, status: 'active' },
  { id: 17, code: '2020', name: 'Accounts Payable - International Vendors', type: 'Current Liability', category: 'liability', balance: 95000, status: 'active' },
  { id: 18, code: '2030', name: 'Salaries Payable', type: 'Current Liability', category: 'liability', balance: 85000, status: 'active' },
  { id: 19, code: '2040', name: 'Tax Payable (Income Tax, VAT, Zakat)', type: 'Current Liability', category: 'liability', balance: 125000, status: 'active' },
  { id: 20, code: '2050', name: 'Logistics Payable (Courier Partner Fees)', type: 'Current Liability', category: 'liability', balance: 45000, status: 'active' },
  { id: 21, code: '2060', name: 'Customer Refunds Payable', type: 'Current Liability', category: 'liability', balance: 32000, status: 'active' },
  { id: 22, code: '2200', name: 'Loans Payable', type: 'Long-term Liability', category: 'liability', balance: 500000, status: 'active' },
  
  // Equity
  { id: 23, code: '3010', name: 'Owner\'s Equity - Partner(s)', type: 'Equity', category: 'equity', balance: 800000, status: 'active' },
  { id: 24, code: '3020', name: 'Investor\'s Equity - Investor(s)', type: 'Equity', category: 'equity', balance: 600000, status: 'active' },
  { id: 25, code: '3030', name: 'Retained Earnings', type: 'Equity', category: 'equity', balance: 1500000, status: 'active' },
  
  // Revenue
  { id: 26, code: '4010', name: 'Sales - Local (Pakistan)', type: 'Revenue', category: 'revenue', balance: 2800000, status: 'active' },
  { id: 27, code: '4020', name: 'Sales - International (USA)', type: 'Revenue', category: 'revenue', balance: 1200000, status: 'active' },
  { id: 28, code: '4030', name: 'Sales - Middle East (KSA, UAE)', type: 'Revenue', category: 'revenue', balance: 800000, status: 'active' },
  { id: 29, code: '4040', name: 'Sales - Southeast Asia (India, Bangladesh)', type: 'Revenue', category: 'revenue', balance: 450000, status: 'active' },
  { id: 30, code: '4110', name: 'Interest Income', type: 'Other Income', category: 'revenue', balance: 25000, status: 'active' },
  { id: 31, code: '4120', name: 'Discounts Received', type: 'Other Income', category: 'revenue', balance: 18000, status: 'active' },
  
  // COGS
  { id: 32, code: '5010', name: 'Raw Material Costs (Fabric, Thread, Accessories)', type: 'Cost of Goods Sold', category: 'expense', balance: 800000, status: 'active' },
  { id: 33, code: '5020', name: 'Manufacturing Labor (Pattern Makers, Designers)', type: 'Cost of Goods Sold', category: 'expense', balance: 350000, status: 'active' },
  { id: 34, code: '5030', name: 'Direct Overheads (Production Utilities)', type: 'Cost of Goods Sold', category: 'expense', balance: 125000, status: 'active' },
  { id: 35, code: '5040', name: 'Freight Inwards (Import Costs for Raw Materials)', type: 'Cost of Goods Sold', category: 'expense', balance: 95000, status: 'active' },
  
  // Operating Expenses
  { id: 36, code: '6010', name: 'Digital Advertising (Google, Meta, TikTok Ads)', type: 'Operating Expense', category: 'expense', balance: 150000, status: 'active' },
  { id: 37, code: '6020', name: 'Marketplace Fees (Amazon, Noon, eBay)', type: 'Operating Expense', category: 'expense', balance: 95000, status: 'active' },
  { id: 38, code: '6030', name: 'Discounts and Promotions', type: 'Operating Expense', category: 'expense', balance: 75000, status: 'active' },
  { id: 39, code: '6040', name: 'Influencer and Affiliate Marketing Costs', type: 'Operating Expense', category: 'expense', balance: 65000, status: 'active' },
  { id: 40, code: '6110', name: 'Salaries and Wages', type: 'Operating Expense', category: 'expense', balance: 450000, status: 'active' },
  { id: 41, code: '6120', name: 'Rent and Utilities (Office and Warehouse)', type: 'Operating Expense', category: 'expense', balance: 120000, status: 'active' },
  { id: 42, code: '6130', name: 'Software Subscriptions (Shopify, ERP, SMM Tools)', type: 'Operating Expense', category: 'expense', balance: 35000, status: 'active' },
  { id: 43, code: '6140', name: 'Legal and Professional Fees', type: 'Operating Expense', category: 'expense', balance: 45000, status: 'active' },
  { id: 44, code: '6210', name: 'Local Delivery Charges (Pakistan)', type: 'Operating Expense', category: 'expense', balance: 85000, status: 'active' },
  { id: 45, code: '6220', name: 'International Shipping Costs (FedEx, DHL)', type: 'Operating Expense', category: 'expense', balance: 125000, status: 'active' },
  
  // Taxes
  { id: 46, code: '7010', name: 'Income Tax (Corporate Tax)', type: 'Tax Expense', category: 'expense', balance: 180000, status: 'active' },
  { id: 47, code: '7020', name: 'Sales Tax Payable (USA, PK, KSA)', type: 'Tax Expense', category: 'expense', balance: 95000, status: 'active' },
  { id: 48, code: '7030', name: 'VAT Payable (KSA)', type: 'Tax Expense', category: 'expense', balance: 45000, status: 'active' },
  { id: 49, code: '7040', name: 'Zakat Payable (KSA)', type: 'Tax Expense', category: 'expense', balance: 25000, status: 'active' }
])

const filteredAccounts = computed(() => {
  let filtered = accounts.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(account => 
      account.name.toLowerCase().includes(query) ||
      account.code.toLowerCase().includes(query)
    )
  }
  
  if (selectedType.value) {
    filtered = filtered.filter(account => account.type === selectedType.value)
  }
  
  if (selectedCategory.value) {
    filtered = filtered.filter(account => account.category === selectedCategory.value)
  }
  
  return filtered
})

const parentAccounts = computed(() => {
  return accounts.value.filter(account => account.id !== editingAccount.value?.id)
})

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const getBalanceClass = (balance: number) => {
  if (balance > 0) return 'positive'
  if (balance < 0) return 'negative'
  return 'zero'
}

const editAccount = (account: any) => {
  editingAccount.value = account
  accountForm.value = { ...account }
  showCreateModal.value = true
}

const viewTransactions = (account: any) => {
  console.log('Viewing transactions for account:', account.name)
  // Navigate to account transactions
}

const deleteAccount = (account: any) => {
  if (confirm(`Are you sure you want to delete account "${account.name}"?`)) {
    const index = accounts.value.findIndex(a => a.id === account.id)
    if (index > -1) {
      accounts.value.splice(index, 1)
    }
  }
}

const saveAccount = () => {
  if (editingAccount.value) {
    // Update existing account
    const index = accounts.value.findIndex(a => a.id === editingAccount.value.id)
    if (index > -1) {
      accounts.value[index] = { ...accountForm.value, id: editingAccount.value.id }
    }
  } else {
    // Create new account
    const newAccount = {
      ...accountForm.value,
      id: Math.max(...accounts.value.map(a => a.id)) + 1,
      balance: 0
    }
    accounts.value.push(newAccount)
  }
  closeModal()
}

const closeModal = () => {
  showCreateModal.value = false
  editingAccount.value = null
  accountForm.value = {
    code: '',
    name: '',
    type: '',
    category: '',
    description: '',
    parentId: null,
    status: 'active'
  }
}

onMounted(() => {
  // Load accounts data
})
</script>

<style scoped>
.chart-of-accounts {
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

.btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-outline {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #4a5568;
}

.filters-section {
  margin: 20px 0;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.filter-input {
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
}

.table-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
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

.table-actions {
  display: flex;
  gap: 12px;
}

.accounts-table {
  width: 100%;
  border-collapse: collapse;
}

.accounts-table th,
.accounts-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f7fafc;
}

.accounts-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #4a5568;
}

.account-code {
  font-family: monospace;
  font-weight: 600;
  color: #2d3748;
}

.account-name {
  font-weight: 500;
  color: #2d3748;
}

.balance {
  text-align: right;
  font-weight: 500;
}

.balance.positive {
  color: #38a169;
}

.balance.negative {
  color: #e53e3e;
}

.balance.zero {
  color: #718096;
}

.category-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.category-badge.asset {
  background: #e3f2fd;
  color: #1565c0;
}

.category-badge.liability {
  background: #ffebee;
  color: #c62828;
}

.category-badge.equity {
  background: #f3e5f5;
  color: #7b1fa2;
}

.category-badge.revenue {
  background: #e8f5e8;
  color: #2e7d32;
}

.category-badge.expense {
  background: #fff3e0;
  color: #ef6c00;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.active {
  background: #c6f6d5;
  color: #22543d;
}

.status-badge.inactive {
  background: #fed7d7;
  color: #742a2a;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.btn-icon:hover {
  background: #f7fafc;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.account-form {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #4a5568;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .table-actions {
    flex-direction: column;
    gap: 8px;
  }
}
</style>