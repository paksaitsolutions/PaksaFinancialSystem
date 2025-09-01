<template>
  <div class="bank-accounts">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1>Bank Accounts</h1>
      <Button 
        label="Add Bank Account" 
        icon="pi pi-plus" 
        @click="openNewAccountDialog"
      />
    </div>

    <!-- Bank Accounts Summary Cards -->
    <div class="grid mb-4">
      <div class="col-12 md:col-6 lg:col-3">
        <Card class="h-full">
          <template #title>Total Balance</template>
          <template #content>
            <div class="text-4xl font-bold text-primary">
              {{ formatCurrency(totalBalance) }}
            </div>
            <div class="text-sm text-500 mt-2">Across all accounts</div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6 lg:col-3">
        <Card class="h-full">
          <template #title>Active Accounts</template>
          <template #content>
            <div class="text-4xl font-bold text-primary">
              {{ activeAccountsCount }}
            </div>
            <div class="text-sm text-500 mt-2">Out of {{ bankAccounts.length }} total</div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Bank Accounts Table -->
    <Card>
      <template #content>
        <DataTable 
          :value="bankAccounts" 
          :loading="loading"
          responsiveLayout="scroll"
        >
          <Column field="name" header="Account Name" :sortable="true">
            <template #body="{ data }">
              <div>
                <div class="font-medium">{{ data.name }}</div>
                <div class="text-500 text-sm">{{ data.account_number }}</div>
              </div>
            </template>
          </Column>
          
          <Column field="bank_name" header="Bank" :sortable="true" />
          
          <Column field="account_type" header="Type" :sortable="true">
            <template #body="{ data }">
              <Tag :value="formatAccountType(data.account_type)" />
            </template>
          </Column>
          
          <Column field="current_balance" header="Balance" :sortable="true">
            <template #body="{ data }">
              <div class="font-bold" :class="data.current_balance >= 0 ? 'text-green-500' : 'text-red-500'">
                {{ formatCurrency(data.current_balance) }}
              </div>
            </template>
          </Column>
          
          <Column field="is_active" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag 
                :value="data.is_active ? 'Active' : 'Inactive'" 
                :severity="data.is_active ? 'success' : 'danger'" 
              />
            </template>
          </Column>
          
          <Column>
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-sm" 
                  @click="editAccount(data)"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-danger" 
                  @click="confirmDeleteAccount(data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Account Dialog -->
    <Dialog 
      v-model:visible="accountDialog" 
      :header="editing ? 'Edit Bank Account' : 'New Bank Account'" 
      :modal="true"
      :style="{ width: '600px' }"
    >
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label for="name">Account Name</label>
            <InputText 
              id="name" 
              v-model="account.name" 
              class="w-full" 
            />
          </div>
        </div>
        
        <div class="col-12">
          <div class="field">
            <label for="account_number">Account Number</label>
            <InputText 
              id="account_number" 
              v-model="account.account_number" 
              class="w-full" 
            />
          </div>
        </div>
        
        <div class="col-12">
          <div class="field">
            <label for="bank_name">Bank Name</label>
            <InputText 
              id="bank_name" 
              v-model="account.bank_name" 
              class="w-full" 
            />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          class="p-button-text"
          @click="accountDialog = false"
        />
        <Button 
          :label="editing ? 'Update' : 'Create'" 
          @click="saveAccount"
          :loading="saving"
        />
      </template>
    </Dialog>
    
    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deleteAccountDialog" 
      header="Confirm Delete" 
      :modal="true" 
      :style="{ width: '450px' }"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="account">
          Are you sure you want to delete <b>{{ account.name }}</b>?
        </span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          class="p-button-text"
          @click="deleteAccountDialog = false"
        />
        <Button 
          label="Yes" 
          class="p-button-danger"
          @click="deleteAccount"
          :loading="deleting"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

interface BankAccount {
  id: string | number
  name: string
  account_number: string
  bank_name: string
  account_type: string
  current_balance: number
  is_active: boolean
}

const bankAccounts = ref<BankAccount[]>([])
const account = ref<Partial<BankAccount>>({})
const accountDialog = ref(false)
const deleteAccountDialog = ref(false)
const editing = ref(false)
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)

// Computed properties
const totalBalance = computed(() => {
  return bankAccounts.value.reduce((sum, acc) => sum + (acc.current_balance || 0), 0)
})

const activeAccountsCount = computed(() => {
  return bankAccounts.value.filter(acc => acc.is_active).length
})

// Methods
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const formatAccountType = (type: string) => {
  return type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')
}

const loadBankAccounts = async () => {
  loading.value = true
  try {
    // Mock data
    bankAccounts.value = [
      {
        id: 1,
        name: 'Main Business Account',
        account_number: '1234567890',
        bank_name: 'HBL',
        account_type: 'checking',
        current_balance: 150000,
        is_active: true
      },
      {
        id: 2,
        name: 'Savings Account',
        account_number: '9876543210',
        bank_name: 'Meezan Bank',
        account_type: 'savings',
        current_balance: 50000,
        is_active: true
      }
    ]
  } finally {
    loading.value = false
  }
}

const openNewAccountDialog = () => {
  account.value = {
    name: '',
    account_number: '',
    bank_name: '',
    account_type: 'checking',
    current_balance: 0,
    is_active: true
  }
  editing.value = false
  accountDialog.value = true
}

const editAccount = (acc: BankAccount) => {
  account.value = { ...acc }
  editing.value = true
  accountDialog.value = true
}

const saveAccount = async () => {
  saving.value = true
  try {
    if (editing.value) {
      const index = bankAccounts.value.findIndex(acc => acc.id === account.value.id)
      if (index !== -1) {
        bankAccounts.value[index] = { ...bankAccounts.value[index], ...account.value } as BankAccount
      }
    } else {
      const newAccount: BankAccount = {
        id: Date.now(),
        name: account.value.name || '',
        account_number: account.value.account_number || '',
        bank_name: account.value.bank_name || '',
        account_type: account.value.account_type || 'checking',
        current_balance: account.value.current_balance || 0,
        is_active: true
      }
      bankAccounts.value.push(newAccount)
    }
    accountDialog.value = false
  } finally {
    saving.value = false
  }
}

const confirmDeleteAccount = (acc: BankAccount) => {
  account.value = { ...acc }
  deleteAccountDialog.value = true
}

const deleteAccount = async () => {
  deleting.value = true
  try {
    bankAccounts.value = bankAccounts.value.filter(acc => acc.id !== account.value.id)
    deleteAccountDialog.value = false
  } finally {
    deleting.value = false
  }
}

onMounted(() => {
  loadBankAccounts()
})
</script>

<style scoped>
.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
</style>