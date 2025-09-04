<template>
  <div class="budget-planning">
    <div class="dashboard-header">
      <h1>Budget Planning</h1>
      <p>Plan and create budgets for different periods and departments.</p>
    </div>

    <div class="planning-content">
      <Card>
        <template #title>
          <div class="card-title">
            <i class="pi pi-calendar"></i>
            <span>Budget Planning Wizard</span>
          </div>
        </template>
        <template #content>
          <TabView>
            <TabPanel header="Basic Information">
              <div class="p-fluid">
                <div class="grid">
                  <div class="col-12 md:col-6">
                    <div class="field">
                      <label>Budget Name</label>
                      <InputText v-model="budgetForm.name" placeholder="Enter budget name" />
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field">
                      <label>Budget Type</label>
                      <Dropdown v-model="budgetForm.type" :options="budgetTypes" option-label="label" option-value="value" placeholder="Select type" />
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field">
                      <label>Start Date</label>
                      <Calendar v-model="budgetForm.start_date" date-format="yy-mm-dd" />
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field">
                      <label>End Date</label>
                      <Calendar v-model="budgetForm.end_date" date-format="yy-mm-dd" />
                    </div>
                  </div>
                </div>
              </div>
            </TabPanel>
            <TabPanel header="Budget Items">
              <div class="budget-items">
                <div class="flex justify-content-between align-items-center mb-3">
                  <h4>Budget Line Items</h4>
                  <Button label="Add Item" icon="pi pi-plus" @click="addBudgetItem" />
                </div>
                <DataTable :value="budgetForm.line_items" responsive-layout="scroll">
                  <Column field="category" header="Category">
                    <template #body="{ data, index }">
                      <InputText v-model="data.category" />
                    </template>
                  </Column>
                  <Column field="description" header="Description">
                    <template #body="{ data, index }">
                      <InputText v-model="data.description" />
                    </template>
                  </Column>
                  <Column field="amount" header="Amount">
                    <template #body="{ data, index }">
                      <InputNumber v-model="data.amount" mode="currency" currency="USD" />
                    </template>
                  </Column>
                  <Column header="Actions">
                    <template #body="{ index }">
                      <Button icon="pi pi-trash" severity="danger" @click="removeBudgetItem(index)" />
                    </template>
                  </Column>
                </DataTable>
              </div>
            </TabPanel>
            <TabPanel header="Review & Submit">
              <div class="review-section">
                <h4>Budget Summary</h4>
                <div class="summary-grid">
                  <div class="summary-item">
                    <label>Total Amount:</label>
                    <span class="amount">{{ formatCurrency(totalAmount) }}</span>
                  </div>
                  <div class="summary-item">
                    <label>Number of Items:</label>
                    <span>{{ budgetForm.line_items.length }}</span>
                  </div>
                </div>
                <div class="actions mt-4">
                  <Button label="Save as Draft" icon="pi pi-save" class="mr-2" @click="saveDraft" />
                  <Button label="Submit for Approval" icon="pi pi-check" @click="submitBudget" />
                </div>
              </div>
            </TabPanel>
          </TabView>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useBudgetStore } from '../store/budgetStore'

// PrimeVue Components
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'

const toast = useToast()
const budgetStore = useBudgetStore()

const budgetForm = ref({
  name: '',
  type: '',
  start_date: null,
  end_date: null,
  line_items: []
})

const budgetTypes = [
  { label: 'Operational', value: 'OPERATIONAL' },
  { label: 'Capital', value: 'CAPITAL' },
  { label: 'Project', value: 'PROJECT' },
  { label: 'Department', value: 'DEPARTMENT' }
]

const totalAmount = computed(() => 
  budgetForm.value.line_items.reduce((sum, item) => sum + (item.amount || 0), 0)
)

const addBudgetItem = () => {
  budgetForm.value.line_items.push({
    category: '',
    description: '',
    amount: 0
  })
}

const removeBudgetItem = (index) => {
  budgetForm.value.line_items.splice(index, 1)
}

const formatCurrency = (amount) => 
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

const saveDraft = async () => {
  try {
    await budgetStore.createBudget({ ...budgetForm.value, status: 'DRAFT' })
    toast.add({ severity: 'success', summary: 'Success', detail: 'Budget saved as draft' })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save budget' })
  }
}

const submitBudget = async () => {
  try {
    await budgetStore.createBudget({ ...budgetForm.value, status: 'PENDING_APPROVAL' })
    toast.add({ severity: 'success', summary: 'Success', detail: 'Budget submitted for approval' })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to submit budget' })
  }
}
</script>

<style scoped>
.budget-planning {
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

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
}

.amount {
  font-weight: 600;
  color: #3b82f6;
}
</style>