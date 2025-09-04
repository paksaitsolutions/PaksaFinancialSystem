<template>
  <div class="budget-view">
    <div class="dashboard-header">
      <h1>Budget Management</h1>
      <p>Create and manage your organization's budgets with comprehensive planning tools.</p>
    </div>

    <div class="summary-cards">
      <!-- Create Budget Form -->
      <Card class="create-budget-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-plus"></i>
            <span>Create Budget</span>
          </div>
        </template>
          <template #content>
            <form @submit.prevent="createBudget" class="p-fluid">
              <div class="field">
                <label for="name">Budget Name</label>
                <InputText
                  id="name"
                  v-model="budgetForm.name"
                  :class="{ 'p-invalid': submitted && !budgetForm.name }"
                  placeholder="Enter budget name"
                />
                <small v-if="submitted && !budgetForm.name" class="p-error">Budget name is required</small>
              </div>

              <div class="field">
                <label for="amount">Amount</label>
                <InputNumber
                  id="amount"
                  v-model="budgetForm.amount"
                  :class="{ 'p-invalid': submitted && (!budgetForm.amount || budgetForm.amount <= 0) }"
                  mode="currency"
                  currency="USD"
                  locale="en-US"
                  placeholder="0.00"
                />
                <small v-if="submitted && (!budgetForm.amount || budgetForm.amount <= 0)" class="p-error">
                  Amount must be greater than 0
                </small>
              </div>

              <div class="field">
                <label for="type">Budget Type</label>
                <Dropdown
                  id="type"
                  v-model="budgetForm.type"
                  :options="budgetTypes"
                  option-label="label"
                  option-value="value"
                  :class="{ 'p-invalid': submitted && !budgetForm.type }"
                  placeholder="Select budget type"
                />
                <small v-if="submitted && !budgetForm.type" class="p-error">Budget type is required</small>
              </div>

              <div class="grid">
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="startDate">Start Date</label>
                    <Calendar
                      id="startDate"
                      v-model="budgetForm.start_date"
                      :class="{ 'p-invalid': submitted && !budgetForm.start_date }"
                      date-format="yy-mm-dd"
                      placeholder="Select start date"
                    />
                    <small v-if="submitted && !budgetForm.start_date" class="p-error">Start date is required</small>
                  </div>
                </div>
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="endDate">End Date</label>
                    <Calendar
                      id="endDate"
                      v-model="budgetForm.end_date"
                      :class="{ 'p-invalid': submitted && !budgetForm.end_date }"
                      date-format="yy-mm-dd"
                      placeholder="Select end date"
                    />
                    <small v-if="submitted && !budgetForm.end_date" class="p-error">End date is required</small>
                  </div>
                </div>
              </div>

              <div class="field">
                <label for="description">Description</label>
                <Textarea
                  id="description"
                  v-model="budgetForm.description"
                  rows="3"
                  placeholder="Enter budget description"
                />
              </div>

              <Button
                type="submit"
                label="Create Budget"
                :loading="loading"
                class="w-full"
                icon="pi pi-plus"
              />
            </form>
          </template>
        </Card>
      </div>

      <!-- Budget Summary Cards -->
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-wallet text-blue"></i>
            <span>Total Budget</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-blue">{{ formatCurrency(totalBudget) }}</div>
          <div class="summary-date">Current Period</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-chart-line text-orange"></i>
            <span>Total Spent</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-orange">{{ formatCurrency(totalSpent) }}</div>
          <div class="summary-date">Year to Date</div>
        </template>
      </Card>
      
      <Card class="summary-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-check-circle text-green"></i>
            <span>Remaining</span>
          </div>
        </template>
        <template #content>
          <div class="summary-amount text-green">{{ formatCurrency(totalBudget - totalSpent) }}</div>
          <div class="summary-date">Available</div>
        </template>
      </Card>
    </div>

    <!-- Budget List -->
    <div class="main-content">
      <Card class="budget-list-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Budget List</span>
            <Button 
              label="View All" 
              icon="pi pi-arrow-right" 
              iconPos="right" 
              class="p-button-text p-button-sm" 
            />
          </div>
        </template>
          <template #content>
            <DataTable
              :value="budgets"
              :paginator="true"
              :rows="10"
              :loading="tableLoading"
              responsive-layout="scroll"
              class="p-datatable-sm"
            >
              <Column field="name" header="Name" sortable>
                <template #body="{ data }">
                  <span class="font-medium">{{ data.name }}</span>
                </template>
              </Column>
              <Column field="type" header="Type" sortable>
                <template #body="{ data }">
                  <Tag :value="data.type" :severity="getTypeSeverity(data.type)" />
                </template>
              </Column>
              <Column field="amount" header="Amount" sortable>
                <template #body="{ data }">
                  <span class="font-medium">{{ formatCurrency(data.amount) }}</span>
                </template>
              </Column>
              <Column field="spent" header="Spent" sortable>
                <template #body="{ data }">
                  <span class="text-orange-500">{{ formatCurrency(data.spent) }}</span>
                </template>
              </Column>
              <Column field="status" header="Status" sortable>
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column header="Actions">
                <template #body="{ data }">
                  <div class="flex gap-2">
                    <Button
                      icon="pi pi-pencil"
                      size="small"
                      outlined
                      @click="editBudget(data)"
                      v-tooltip="'Edit'"
                    />
                    <Button
                      icon="pi pi-trash"
                      size="small"
                      outlined
                      severity="danger"
                      @click="deleteBudget(data)"
                      v-tooltip="'Delete'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      
      <div class="create-budget-section">
        <Card class="create-budget-card">
          <template #title>
            <div class="card-title">
              <i class="pi pi-plus"></i>
              <span>Create New Budget</span>
            </div>
          </template>
          <template #content>
            <form @submit.prevent="createBudget" class="p-fluid">
              <div class="field">
                <label for="name">Budget Name</label>
                <InputText
                  id="name"
                  v-model="budgetForm.name"
                  :class="{ 'p-invalid': submitted && !budgetForm.name }"
                  placeholder="Enter budget name"
                />
                <small v-if="submitted && !budgetForm.name" class="p-error">Budget name is required</small>
              </div>

              <div class="field">
                <label for="amount">Amount</label>
                <InputNumber
                  id="amount"
                  v-model="budgetForm.amount"
                  :class="{ 'p-invalid': submitted && (!budgetForm.amount || budgetForm.amount <= 0) }"
                  mode="currency"
                  currency="USD"
                  locale="en-US"
                  placeholder="0.00"
                />
                <small v-if="submitted && (!budgetForm.amount || budgetForm.amount <= 0)" class="p-error">
                  Amount must be greater than 0
                </small>
              </div>

              <div class="field">
                <label for="type">Budget Type</label>
                <Dropdown
                  id="type"
                  v-model="budgetForm.type"
                  :options="budgetTypes"
                  option-label="label"
                  option-value="value"
                  :class="{ 'p-invalid': submitted && !budgetForm.type }"
                  placeholder="Select budget type"
                />
                <small v-if="submitted && !budgetForm.type" class="p-error">Budget type is required</small>
              </div>

              <Button
                type="submit"
                label="Create Budget"
                :loading="loading"
                class="w-full"
                icon="pi pi-plus"
              />
            </form>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

// PrimeVue Components
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'

const toast = useToast()
const loading = ref(false)
const tableLoading = ref(false)
const submitted = ref(false)

const budgetForm = ref({
  name: '',
  amount: null as number | null,
  type: '',
  start_date: null as Date | null,
  end_date: null as Date | null,
  description: ''
})

const budgetTypes = [
  { label: 'Operational', value: 'OPERATIONAL' },
  { label: 'Capital', value: 'CAPITAL' },
  { label: 'Project', value: 'PROJECT' },
  { label: 'Department', value: 'DEPARTMENT' }
]

const budgets = ref([
  { 
    id: 1, 
    name: 'Marketing Q1', 
    type: 'OPERATIONAL', 
    amount: 50000, 
    spent: 35000, 
    status: 'APPROVED' 
  },
  { 
    id: 2, 
    name: 'IT Infrastructure', 
    type: 'CAPITAL', 
    amount: 100000, 
    spent: 75000, 
    status: 'DRAFT' 
  }
])

const totalBudget = computed(() => budgets.value.reduce((sum, b) => sum + b.amount, 0))
const totalSpent = computed(() => budgets.value.reduce((sum, b) => sum + b.spent, 0))

const validateForm = () => {
  return budgetForm.value.name && 
         budgetForm.value.amount && 
         budgetForm.value.amount > 0 &&
         budgetForm.value.type &&
         budgetForm.value.start_date &&
         budgetForm.value.end_date
}

const createBudget = async () => {
  submitted.value = true
  
  if (!validateForm()) {
    toast.add({
      severity: 'error',
      summary: 'Validation Error',
      detail: 'Please fill in all required fields',
      life: 3000
    })
    return
  }
  
  loading.value = true
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    budgets.value.push({
      id: Date.now(),
      name: budgetForm.value.name,
      type: budgetForm.value.type,
      amount: budgetForm.value.amount!,
      spent: 0,
      status: 'DRAFT'
    })
    
    // Reset form
    budgetForm.value = {
      name: '',
      amount: null,
      type: '',
      start_date: null,
      end_date: null,
      description: ''
    }
    submitted.value = false
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Budget created successfully',
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to create budget',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const editBudget = (budget: any) => {
  toast.add({
    severity: 'info',
    summary: 'Edit Budget',
    detail: `Editing ${budget.name}`,
    life: 3000
  })
}

const deleteBudget = (budget: any) => {
  toast.add({
    severity: 'warn',
    summary: 'Delete Budget',
    detail: `Deleting ${budget.name}`,
    life: 3000
  })
}

const getTypeSeverity = (type: string) => {
  switch (type) {
    case 'OPERATIONAL': return 'info'
    case 'CAPITAL': return 'warning'
    case 'PROJECT': return 'success'
    case 'DEPARTMENT': return 'secondary'
    default: return 'info'
  }
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'APPROVED': return 'success'
    case 'DRAFT': return 'secondary'
    case 'PENDING_APPROVAL': return 'warning'
    case 'REJECTED': return 'danger'
    default: return 'secondary'
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD' 
  }).format(amount)
}

onMounted(() => {
  // Load initial data
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
  }, 500)
})
</script>

<style scoped>
.budget-view {
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

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  height: 100%;
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

.budget-list-card,
.create-budget-card {
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

.field > label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.text-blue { color: #3b82f6; }
.text-orange { color: #f59e0b; }
.text-green { color: #10b981; }

@media (max-width: 768px) {
  .budget-view {
    padding: 1rem;
  }
  
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>