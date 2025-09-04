<template>
  <div class="chart-accounts-config">
    <div class="dashboard-header">
      <h1>Chart of Accounts Configuration</h1>
      <p>Manage your chart of accounts structure and account types</p>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Account Categories</span>
            <Button label="Add Category" icon="pi pi-plus" @click="showAddCategory = true" />
          </div>
        </template>
        <template #content>
          <DataTable :value="accountCategories" responsiveLayout="scroll">
            <Column field="code" header="Code" />
            <Column field="name" header="Name" />
            <Column field="type" header="Type" />
            <Column field="description" header="Description" />
            <Column header="Actions">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button icon="pi pi-pencil" class="p-button-rounded p-button-text" @click="editCategory(data)" />
                  <Button icon="pi pi-trash" class="p-button-rounded p-button-text p-button-danger" @click="deleteCategory(data)" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>
          <span>Account Structure Settings</span>
        </template>
        <template #content>
          <div class="grid p-fluid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Account Code Format</label>
                <Dropdown v-model="accountSettings.codeFormat" :options="codeFormats" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Default Currency</label>
                <Dropdown v-model="accountSettings.defaultCurrency" :options="currencies" />
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="accountSettings.requireApproval" binary />
                  <span class="ml-2">Require approval for new accounts</span>
                </label>
              </div>
            </div>
          </div>
        </template>
        <template #footer>
          <Button label="Save Settings" icon="pi pi-check" @click="saveSettings" />
        </template>
      </Card>
    </div>

    <Dialog v-model:visible="showAddCategory" modal header="Add Account Category" :style="{ width: '500px' }">
      <div class="grid p-fluid">
        <div class="col-12">
          <div class="field">
            <label>Code</label>
            <InputText v-model="newCategory.code" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Name</label>
            <InputText v-model="newCategory.name" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Type</label>
            <Dropdown v-model="newCategory.type" :options="accountTypes" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Description</label>
            <Textarea v-model="newCategory.description" rows="3" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showAddCategory = false" />
        <Button label="Add" @click="addCategory" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showAddCategory = ref(false)

const accountCategories = ref([
  { code: '1000', name: 'Current Assets', type: 'Asset', description: 'Cash and assets convertible to cash within one year' },
  { code: '2000', name: 'Current Liabilities', type: 'Liability', description: 'Debts due within one year' },
  { code: '3000', name: 'Equity', type: 'Equity', description: 'Owner equity accounts' },
  { code: '4000', name: 'Revenue', type: 'Revenue', description: 'Income from business operations' },
  { code: '5000', name: 'Expenses', type: 'Expense', description: 'Operating expenses' }
])

const accountSettings = ref({
  codeFormat: '4-digit',
  defaultCurrency: 'USD',
  requireApproval: true
})

const newCategory = ref({
  code: '',
  name: '',
  type: '',
  description: ''
})

const codeFormats = ref(['3-digit', '4-digit', '5-digit', 'Custom'])
const currencies = ref(['USD', 'EUR', 'GBP', 'CAD'])
const accountTypes = ref(['Asset', 'Liability', 'Equity', 'Revenue', 'Expense'])

const addCategory = () => {
  accountCategories.value.push({ ...newCategory.value })
  newCategory.value = { code: '', name: '', type: '', description: '' }
  showAddCategory.value = false
}

const editCategory = (category: any) => {
  console.log('Editing category:', category)
}

const deleteCategory = (category: any) => {
  console.log('Deleting category:', category)
}

const saveSettings = () => {
  console.log('Saving account settings:', accountSettings.value)
}
</script>

<style scoped>
.chart-accounts-config {
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

.main-content {
  display: grid;
  grid-template-columns: 1fr;
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

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}

@media (max-width: 768px) {
  .chart-accounts-config {
    padding: 1rem;
  }
}
</style>