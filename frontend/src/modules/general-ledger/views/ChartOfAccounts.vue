<template>
  <div class="chart-of-accounts">
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <Button icon="pi pi-arrow-left" class="p-button-text" @click="$router.go(-1)" />
          <div>
            <h1>Chart of Accounts</h1>
            <p class="subtitle">Manage your account structure and balances</p>
          </div>
        </div>
        <div class="header-actions">
          <Button label="Import Accounts" icon="pi pi-upload" class="p-button-outlined" @click="showImportDialog = true" />
          <Button label="New Account" icon="pi pi-plus" class="p-button-success" @click="showDialog = true" />
        </div>
      </div>
    </div>

    <div class="content-container">
      <Card>
        <template #content>
          <DataTable 
            :value="accounts" 
            :paginator="true" 
            :rows="20"
            :loading="loading"
            filterDisplay="menu"
            :globalFilterFields="['code', 'name', 'type']"
            responsiveLayout="scroll"
          >
            <template #header>
              <div class="flex justify-content-between align-items-center">
                <span class="p-input-icon-left">
                  <i class="pi pi-search" />
                  <InputText v-model="globalFilter" placeholder="Search accounts..." />
                </span>
                <div class="flex gap-2">
                  <Dropdown v-model="typeFilter" :options="accountTypes" optionLabel="label" optionValue="value" placeholder="Filter by Type" showClear />
                  <Button icon="pi pi-refresh" class="p-button-outlined" @click="loadAccounts" />
                </div>
              </div>
            </template>

            <Column field="code" header="Account Code" sortable style="width: 120px">
              <template #body="{ data }">
                <span class="font-mono">{{ data.code }}</span>
              </template>
            </Column>

            <Column field="name" header="Account Name" sortable>
              <template #body="{ data }">
                <div class="flex align-items-center gap-2">
                  <div class="account-type-indicator" :class="getTypeColor(data.type)"></div>
                  <span>{{ data.name }}</span>
                </div>
              </template>
            </Column>

            <Column field="type" header="Type" sortable style="width: 150px">
              <template #body="{ data }">
                <Tag :value="data.type" :severity="getTypeSeverity(data.type)" />
              </template>
            </Column>

            <Column field="balance" header="Balance" sortable style="width: 150px" class="text-right">
              <template #body="{ data }">
                <span :class="data.balance >= 0 ? 'text-green-600' : 'text-red-600'" class="font-medium">
                  {{ formatCurrency(data.balance) }}
                </span>
              </template>
            </Column>

            <Column field="status" header="Status" sortable style="width: 100px">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="data.status === 'Active' ? 'success' : 'warning'" />
              </template>
            </Column>

            <Column header="Actions" style="width: 120px">
              <template #body="{ data }">
                <div class="flex gap-1">
                  <Button icon="pi pi-eye" class="p-button-rounded p-button-text p-button-sm" @click="viewAccount(data)" />
                  <Button icon="pi pi-pencil" class="p-button-rounded p-button-text p-button-sm" @click="editAccount(data)" />
                  <Button icon="pi pi-trash" class="p-button-rounded p-button-text p-button-sm p-button-danger" @click="deleteAccount(data)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>

    <!-- Floating Action Button -->
    <Button 
      icon="pi pi-plus" 
      class="floating-add-btn"
      @click="showDialog = true"
      v-tooltip="'Add New Account'"
    />

    <!-- Account Dialog -->
    <Dialog v-model:visible="showDialog" modal :header="editingAccount ? 'Edit Account' : 'New Account'" :style="{width: '500px'}">
      <div class="p-fluid">
        <div class="field">
          <label for="code" class="required">Account Code *</label>
          <InputText id="code" v-model="form.code" :class="{ 'p-invalid': errors.code }" />
          <small v-if="errors.code" class="p-error">{{ errors.code }}</small>
        </div>

        <div class="field">
          <label for="name" class="required">Account Name *</label>
          <InputText id="name" v-model="form.name" :class="{ 'p-invalid': errors.name }" />
          <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
        </div>

        <div class="field">
          <label for="type" class="required">Account Type *</label>
          <div class="flex gap-2">
            <Dropdown 
              id="type" 
              v-model="form.type" 
              :options="accountTypes" 
              optionLabel="label" 
              optionValue="value" 
              :class="{ 'p-invalid': errors.type }"
              placeholder="Select Account Type"
              class="flex-1"
            />
            <Button 
              icon="pi pi-plus" 
              class="p-button-outlined p-button-sm" 
              @click="showTypeDialog = true"
              v-tooltip="'Add Custom Type'"
            />
          </div>
          <small v-if="errors.type" class="p-error">{{ errors.type }}</small>
        </div>

        <div class="field">
          <label for="description">Description</label>
          <Textarea id="description" v-model="form.description" rows="3" />
        </div>

        <div class="field">
          <div class="flex align-items-center gap-2">
            <Checkbox v-model="form.active" inputId="active" :binary="true" />
            <label for="active">Active</label>
          </div>
        </div>
      </div>

      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="closeDialog" />
        <Button label="Save" :loading="saving" @click="saveAccount" />
      </template>
    </Dialog>

    <!-- Import Accounts Dialog -->
    <Dialog v-model:visible="showImportDialog" modal header="Import Accounts" :style="{width: '500px'}">
      <div class="p-fluid">
        <div class="field">
          <label for="importFile">Select CSV File</label>
          <input 
            type="file" 
            accept=".csv" 
            @change="onFileSelect" 
            class="p-inputtext p-component w-full"
          />
          <small class="text-600">Upload a CSV file with columns: Code, Name, Type, Description</small>
        </div>
        <div v-if="importPreview.length > 0" class="field">
          <label>Preview (First 5 rows)</label>
          <DataTable :value="importPreview" class="p-datatable-sm">
            <Column field="code" header="Code" />
            <Column field="name" header="Name" />
            <Column field="type" header="Type" />
          </DataTable>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="closeImportDialog" />
        <Button label="Import" @click="importAccounts" :disabled="importPreview.length === 0" :loading="importing" />
      </template>
    </Dialog>

    <!-- Custom Account Type Dialog -->
    <Dialog v-model:visible="showTypeDialog" modal header="Add Custom Account Type" :style="{width: '400px'}">
      <div class="p-fluid">
        <div class="field">
          <label for="newType" class="required">Account Type Name *</label>
          <InputText 
            id="newType" 
            v-model="newTypeName" 
            placeholder="Enter account type name"
            @keyup.enter="addCustomType"
          />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="closeTypeDialog" />
        <Button label="Save" @click="addCustomType" :disabled="!newTypeName.trim()" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import chartOfAccountsService from '@/services/chartOfAccountsService'
import { useAuthStore } from '@/stores/auth'
import { getAccountTypes } from '@/utils/constants'

const toast = useToast()
const authStore = useAuthStore()
const loading = ref(false)
const saving = ref(false)
const showDialog = ref(false)
const showTypeDialog = ref(false)
const showImportDialog = ref(false)
const editingAccount = ref(null)
const globalFilter = ref('')
const typeFilter = ref(null)
const newTypeName = ref('')
const importing = ref(false)
const importPreview = ref([])
const importFile = ref(null)
const accounts = ref([])
const accountTypes = ref([])
const currentCompany = computed(() => authStore.currentCompany)

const form = reactive({
  code: '',
  name: '',
  type: '',
  description: '',
  active: true
})

const errors = reactive({
  code: '',
  name: '',
  type: ''
})

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
}

const getTypeColor = (type: string) => {
  const colors = {
    Asset: 'bg-blue-500',
    Bank: 'bg-blue-600',
    'Accounts Receivable': 'bg-blue-400',
    Inventory: 'bg-indigo-500',
    'Fixed Asset': 'bg-purple-500',
    'Prepaid Expense': 'bg-blue-300',
    Liability: 'bg-red-500',
    'Accounts Payable': 'bg-red-600',
    'Credit Card': 'bg-red-400',
    'Accrued Expense': 'bg-red-300',
    'Deferred Revenue': 'bg-pink-500',
    'Long Term Liability': 'bg-red-700',
    Equity: 'bg-green-500',
    'Retained Earnings': 'bg-green-600',
    Revenue: 'bg-teal-500',
    'Other Income': 'bg-teal-400',
    Expense: 'bg-amber-500',
    COGS: 'bg-orange-500',
    'Other Expense': 'bg-amber-400',
    'Accumulated Depreciation': 'bg-gray-500'
  }
  return colors[type] || 'bg-gray-500'
}

const getTypeSeverity = (type: string) => {
  const severities = {
    Asset: 'info',
    Bank: 'info',
    'Accounts Receivable': 'info',
    Inventory: 'info',
    'Fixed Asset': 'info',
    'Prepaid Expense': 'info',
    Liability: 'danger',
    'Accounts Payable': 'danger',
    'Credit Card': 'danger',
    'Accrued Expense': 'danger',
    'Deferred Revenue': 'danger',
    'Long Term Liability': 'danger',
    Equity: 'success',
    'Retained Earnings': 'success',
    Revenue: 'success',
    'Other Income': 'success',
    Expense: 'warning',
    COGS: 'warning',
    'Other Expense': 'warning',
    'Accumulated Depreciation': 'secondary'
  }
  return severities[type] || 'secondary'
}

const loadAccounts = async () => {
  if (!currentCompany.value?.id) return
  
  loading.value = true
  try {
    const response = await chartOfAccountsService.getAccounts(currentCompany.value.id)
    accounts.value = response.data.map(account => ({
      ...account,
      type: account.account_type,
      status: account.is_active ? 'Active' : 'Inactive'
    }))
  } catch (error) {
    console.error('Error loading accounts:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load accounts' })
  } finally {
    loading.value = false
  }
}

const loadAccountTypes = async () => {
  try {
    const types = await getAccountTypes()
    accountTypes.value = types.map(type => ({
      label: type.name,
      value: type.code
    }))
  } catch (error) {
    console.error('Error loading account types:', error)
    // Fallback to basic types
    accountTypes.value = [
      { label: 'Asset', value: 'ASSET' },
      { label: 'Liability', value: 'LIABILITY' },
      { label: 'Equity', value: 'EQUITY' },
      { label: 'Revenue', value: 'REVENUE' },
      { label: 'Expense', value: 'EXPENSE' }
    ]
  }
}

const viewAccount = (account: any) => {
  toast.add({ severity: 'info', summary: 'Account Details', detail: `Viewing ${account.name}` })
}

const editAccount = (account: any) => {
  editingAccount.value = account
  form.code = account.code
  form.name = account.name
  form.type = account.type
  form.description = account.description || ''
  form.active = account.status === 'Active'
  showDialog.value = true
}

const deleteAccount = (account: any) => {
  toast.add({ severity: 'warn', summary: 'Delete Account', detail: `Delete ${account.name}?` })
}

const closeDialog = () => {
  showDialog.value = false
  editingAccount.value = null
  // Reset form
  form.code = ''
  form.name = ''
  form.type = ''
  form.description = ''
  form.active = true
  // Clear errors
  Object.keys(errors).forEach(key => errors[key] = '')
}

const saveAccount = async () => {
  // Clear errors
  Object.keys(errors).forEach(key => errors[key] = '')
  
  // Validate
  if (!form.code) errors.code = 'Account code is required'
  if (!form.name) errors.name = 'Account name is required'
  if (!form.type) errors.type = 'Account type is required'
  
  if (Object.values(errors).some(error => error)) return
  
  saving.value = true
  try {
    const accountData = {
      code: form.code,
      name: form.name,
      type: form.type,
      account_type: form.type,
      description: form.description,
      is_active: form.active
    }
    
    console.log('Saving account data:', accountData)
    
    if (editingAccount.value) {
      await chartOfAccountsService.updateAccount(editingAccount.value.id, accountData)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Account updated successfully' })
    } else {
      await chartOfAccountsService.createAccount('dummy-company-id', accountData)
      toast.add({ severity: 'success', summary: 'Success', detail: 'Account created successfully' })
    }
    
    closeDialog()
    await loadAccounts()
  } catch (error) {
    console.error('Error saving account:', error)
    console.error('Error details:', error.response?.data)
    toast.add({ severity: 'error', summary: 'Error', detail: error.response?.data?.detail || 'Failed to save account' })
  } finally {
    saving.value = false
  }
}

const closeTypeDialog = () => {
  showTypeDialog.value = false
  newTypeName.value = ''
}

const addCustomType = () => {
  if (!newTypeName.value.trim()) return
  
  const newType = {
    label: newTypeName.value.trim(),
    value: newTypeName.value.trim()
  }
  
  // Check if type already exists
  if (!accountTypes.value.find(type => type.value === newType.value)) {
    accountTypes.value.push(newType)
    form.type = newType.value
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: `Account type '${newType.label}' added successfully` 
    })
  } else {
    toast.add({ 
      severity: 'warn', 
      summary: 'Warning', 
      detail: 'Account type already exists' 
    })
  }
  
  closeTypeDialog()
}

const onFileSelect = (event: any) => {
  const file = event.target.files[0]
  if (!file) return
  
  importFile.value = file
  const reader = new FileReader()
  reader.onload = (e) => {
    const csv = e.target?.result as string
    const lines = csv.split('\n')
    
    const preview = lines.slice(1, 6).map(line => {
      const values = line.split(',')
      return {
        code: values[0]?.trim(),
        name: values[1]?.trim(),
        type: values[2]?.trim(),
        description: values[3]?.trim()
      }
    }).filter(row => row.code && row.name)
    
    importPreview.value = preview
  }
  reader.readAsText(file)
}

const closeImportDialog = () => {
  showImportDialog.value = false
  importPreview.value = []
  importFile.value = null
}

const importAccounts = async () => {
  if (!importFile.value || !currentCompany.value?.id) return
  
  importing.value = true
  try {
    const reader = new FileReader()
    reader.onload = async (e) => {
      const csv = e.target?.result as string
      const lines = csv.split('\n')
      const accounts = lines.slice(1).map(line => {
        const values = line.split(',')
        return {
          code: values[0]?.trim(),
          name: values[1]?.trim(),
          account_type: values[2]?.trim(),
          description: values[3]?.trim(),
          is_active: true
        }
      }).filter(account => account.code && account.name)
      
      let successCount = 0
      for (const account of accounts) {
        try {
          await chartOfAccountsService.createAccount(currentCompany.value.id, account)
          successCount++
        } catch (error) {
          console.error(`Failed to import account ${account.code}:`, error)
        }
      }
      
      toast.add({
        severity: 'success',
        summary: 'Import Complete',
        detail: `Successfully imported ${successCount} of ${accounts.length} accounts`
      })
      
      closeImportDialog()
      await loadAccounts()
    }
    reader.readAsText(importFile.value)
  } catch (error) {
    console.error('Error importing accounts:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to import accounts' })
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  await loadAccountTypes()
  await loadAccounts()
})
</script>

<style scoped>
.chart-of-accounts {
  padding: 0;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-left h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: #1f2937;
}

.subtitle {
  margin: 0.25rem 0 0 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.header-actions .p-button {
  font-weight: 500;
  padding: 0.75rem 1.5rem;
}

.header-actions .p-button-success {
  background: #10b981;
  border-color: #10b981;
}

.header-actions .p-button-success:hover {
  background: #059669;
  border-color: #059669;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem 2rem;
}

.account-type-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.required::after {
  content: ' *';
  color: #ef4444;
}

.floating-add-btn {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #10b981;
  border-color: #10b981;
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.floating-add-btn:hover {
  background: #059669;
  border-color: #059669;
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.5);
}

.floating-add-btn i {
  font-size: 1.25rem;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .content-container {
    padding: 0 1rem 2rem;
  }
  
  .floating-add-btn {
    bottom: 1rem;
    right: 1rem;
  }
}
</style>