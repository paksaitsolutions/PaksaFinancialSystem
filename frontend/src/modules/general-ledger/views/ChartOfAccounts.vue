<template>
  <div class="chart-of-accounts">
    <Toast />
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>Chart of Accounts</h1>
            <p>Manage your chart of accounts structure</p>
          </div>
          <Button 
            icon="pi pi-plus" 
            label="Add Account" 
            @click="openCreateModal"
            :loading="loading"
          />
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
      <div class="card">
          <DataTable 
            :value="filteredAccounts" 
            :loading="tableLoading" 
            :paginator="true" 
            :rows="10"
            :rowsPerPageOptions="[5,10,25,50]"
            :globalFilterFields="['code', 'name', 'type', 'category']"
            :stripedRows="true"
            scrollable
            scrollHeight="flex"
            scrollDirection="both"
            class="p-datatable-sm"
            currentPageReportTemplate="Showing {first} to {last} of {totalRecords} accounts"
          >
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3>Accounts ({{ filteredAccounts.length }})</h3>
              <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText v-model="searchQuery" placeholder="Search accounts..." />
              </span>
            </div>
          </template>
          
          <template #empty>
            <div class="text-center p-4">
              <p>No accounts found</p>
            </div>
          </template>
          
          <Column field="code" header="Code" sortable>
            <template #body="{ data }: { data: Account }">
              <span class="font-medium">{{ data.code }}</span>
            </template>
          </Column>
          
          <Column field="name" header="Name" sortable>
            <template #body="{ data }: { data: Account }">
              <div class="flex align-items-center">
                <i :class="getAccountIcon(data.category)" class="mr-2"></i>
                {{ data.name }}
              </div>
            </template>
          </Column>
          
          <Column field="type" header="Type" sortable>
            <template #body="{ data }: { data: Account }">
              <Tag :value="data.type" :severity="getTypeSeverity(data.type)" />
            </template>
          </Column>
          <Column field="category" header="Category" sortable>
            <template #body="{ data }: { data: Account }">
              <Tag :value="formatCategory(data.category)" :severity="getCategorySeverity(data.category)" />
            </template>
          </Column>
          
          <Column field="balance" header="Balance" sortable>
            <template #body="{ data }: { data: Account }">
              <span :class="getBalanceClass(data.balance)">
                {{ formatCurrency(data.balance) }}
              </span>
            </template>
          </Column>
          
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <span :class="'status-badge status-' + data.status">
                {{ data.status }}
              </span>
            </template>
          </Column>
          
          <Column header="Actions" style="width: 200px">
            <template #body="{ data }: { data: Account }">
              <div class="flex gap-2">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-sm p-button-text" 
                  @click="editAccount(data)" 
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-sm p-button-text p-button-danger" 
                  @click="confirmDeleteAccount(data)" 
                />
                <Button 
                  icon="pi pi-list" 
                  class="p-button-sm p-button-text" 
                  @click="viewTransactions(data)" 
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Dialog 
      v-model:visible="showCreateModal" 
      :style="{ width: '600px' }" 
      :header="currentAccountId ? 'Edit Account' : 'Create Account'"
      :modal="true"
      :closable="!loading"
      :closeOnEscape="!loading"
      @hide="closeModal"
    >
      <form @submit.prevent="saveAccount">
        <div class="grid p-fluid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="code">Account Code <span class="required">*</span></label>
              <InputText 
                id="code" 
                v-model.trim="accountForm.code" 
                required 
                :disabled="loading"
                class="w-full"
              />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="name">Account Name <span class="required">*</span></label>
              <InputText 
                id="name" 
                v-model.trim="accountForm.name" 
                required 
                :disabled="loading"
                class="w-full"
              />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="type">Account Type <span class="required">*</span></label>
              <Dropdown 
                id="type"
                v-model="accountForm.type"
                :options="accountTypes"
                placeholder="Select a type"
                :disabled="loading"
                class="w-full"
                required
              />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="category">Category <span class="required">*</span></label>
              <Dropdown 
                id="category"
                v-model="accountForm.category"
                :options="accountCategories"
                placeholder="Select a category"
                :disabled="loading"
                class="w-full"
                required
              />
            </div>
          </div>
          <div class="col-12">
            <div class="field">
              <label for="description">Description</label>
              <Textarea 
                id="description" 
                v-model="accountForm.description" 
                :disabled="loading"
                rows="3"
                class="w-full"
                autoResize
              />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="status">Status</label>
              <Dropdown 
                id="status"
                v-model="accountForm.status"
                :options="statusOptions"
                optionLabel="label"
                optionValue="value"
                :disabled="loading"
                class="w-full"
              />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="parent">Parent Account</label>
              <Dropdown 
                id="parent"
                v-model="accountForm.parentId"
                :options="parentAccounts"
                optionLabel="name"
                optionValue="id"
                :disabled="loading"
                :filter="true"
                filterBy="name,code"
                :showClear="true"
                placeholder="Select a parent account"
                class="w-full"
              >
                <template #option="slotProps">
                  <div class="flex align-items-center">
                    <span>{{ slotProps.option.code }} - {{ slotProps.option.name }}</span>
                  </div>
                </template>
              </Dropdown>
            </div>
          </div>
        </div>
        <template #footer>
          <Button 
            label="Cancel" 
            icon="pi pi-times" 
            class="p-button-text" 
            :disabled="loading" 
            @click="closeModal" 
          />
          <Button 
            type="submit" 
            :label="currentAccountId ? 'Update' : 'Create'" 
            icon="pi pi-check" 
            :loading="loading"
          />
        </template>
      </form>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

// PrimeVue components are auto-imported by the project

// Types
type AccountType = 'Asset' | 'Liability' | 'Equity' | 'Revenue' | 'Expense';
type AccountCategory = 'asset' | 'liability' | 'equity' | 'revenue' | 'expense';

interface Account {
  id: string;
  code: string;
  name: string;
  type: AccountType;
  category: AccountCategory;
  description?: string;
  parentId: string | null;
  status: 'active' | 'inactive';
  balance: number;
  children?: Account[];
  level?: number;
  hasChildren?: boolean;
  createdAt?: string;
  updatedAt?: string;
}

interface AccountFormValues {
  code: string;
  name: string;
  type: string;
  category: string;
  description: string;
  parentId: string | null;
  status: string;
  balance: number;
}

// Services
const toast = useToast();
const confirm = useConfirm();

// Account type constants (unused but kept for future use)
// const ACCOUNT_TYPES = ['Asset', 'Liability', 'Equity', 'Revenue', 'Expense'] as const;
// const ACCOUNT_CATEGORIES = ['asset', 'liability', 'equity', 'revenue', 'expense'] as const;

// Form state with proper type
const accountForm = ref<AccountFormValues>({
  code: '',
  name: '',
  type: 'Asset',
  category: 'asset',
  description: '',
  parentId: null,
  status: 'active',
  balance: 0
});

// Component state
const loading = ref(false);
const showCreateModal = ref(false);
const currentAccountId = ref<string | null>(null);

// Accounts data
const accounts = ref<Account[]>([]);

// Methods

// saveAccount function is used in the template but TypeScript doesn't detect it

// Reset form to initial state
const resetAccountForm = () => {
  accountForm.value = {
    code: '',
    name: '',
    type: 'Asset',
    category: 'asset',
    description: '',
    parentId: null,
    status: 'active',
    balance: 0
  };
  currentAccountId.value = null;
};

// openCreateModal is used in the template but TypeScript doesn't detect it
const openCreateModal = (): void => {
  resetAccountForm();
  showCreateModal.value = true;
};

onMounted(() => {
  // Load accounts data
})

// Get account icon based on category (unused but kept for future use)
// const getAccountIcon = (category: string): string => {
//   const icons: Record<string, string> = {
//     asset: 'pi pi-wallet',
//     liability: 'pi pi-credit-card',
//     equity: 'pi pi-chart-line',
//     revenue: 'pi pi-money-bill',
//     expense: 'pi pi-shopping-cart'
//   };
//   return icons[category] || 'pi pi-question-circle';
// };

// Get severity for account category (unused but kept for future use)
// const getCategorySeverity = (category: string): string => {
//   if (!category) return 'info';
//   
//   switch (category.toLowerCase()) {
//     case 'asset': return 'success';
//     case 'liability': return 'warning';
//     case 'equity': return 'info';
//     case 'revenue': return 'help';
//     case 'expense': return 'danger';
//     default: return 'info';
//   }
// };
</script>

<style lang="scss" scoped>
.chart-of-accounts {
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