<template>
  <div class="budget-dashboard">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Budget Management</h1>
        <p class="text-color-secondary">Manage organizational budgets and financial planning</p>
      </div>
      <Button label="Create Budget" icon="pi pi-plus" @click="showCreateDialog" />
    </div>

    <div class="grid">
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-blue-100 text-blue-600 mr-3">
                <i class="pi pi-chart-bar text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Total Budgets</div>
                <div class="text-2xl font-bold">{{ stats.totalBudgets }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-green-100 text-green-600 mr-3">
                <i class="pi pi-dollar text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Total Amount</div>
                <div class="text-2xl font-bold">${{ formatCurrency(stats.totalAmount) }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-orange-100 text-orange-600 mr-3">
                <i class="pi pi-clock text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Pending Approval</div>
                <div class="text-2xl font-bold">{{ stats.pendingApproval }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-purple-100 text-purple-600 mr-3">
                <i class="pi pi-check-circle text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Active Budgets</div>
                <div class="text-2xl font-bold">{{ stats.activeBudgets }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Card>
      <template #title>Budget Overview</template>
      <template #content>
        <DataTable :value="budgets" :loading="loading" paginator :rows="10">
          <Column field="name" header="Budget Name" sortable />
          <Column field="type" header="Type" sortable>
            <template #body="{ data }">
              <Tag :value="data.type" severity="info" />
            </template>
          </Column>
          <Column field="amount" header="Amount" sortable>
            <template #body="{ data }">
              ${{ formatCurrency(data.amount) }}
            </template>
          </Column>
          <Column field="period_start" header="Start Date" sortable>
            <template #body="{ data }">
              {{ formatDate(data.period_start) }}
            </template>
          </Column>
          <Column field="period_end" header="End Date" sortable>
            <template #body="{ data }">
              {{ formatDate(data.period_end) }}
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text" @click="viewBudget(data)" />
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editBudget(data)" />
              <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="deleteBudget(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="budgetDialog" header="Create Budget" :modal="true" :style="{width: '800px'}">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Budget Name</label>
            <InputText v-model="budget.name" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Budget Type</label>
            <Dropdown v-model="budget.type" :options="[{label: 'Operational', value: 'OPERATIONAL'}, {label: 'Capital', value: 'CAPITAL'}, {label: 'Project', value: 'PROJECT'}]" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Start Date</label>
            <Calendar v-model="budget.period_start" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>End Date</label>
            <Calendar v-model="budget.period_end" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Description</label>
            <Textarea v-model="budget.description" rows="3" class="w-full" />
          </div>
        </div>
      </div>
      
      <Divider />
      
      <div class="flex justify-content-between align-items-center mb-3">
        <h4>Budget Line Items</h4>
        <Button label="Add Line Item" icon="pi pi-plus" size="small" @click="addLineItem" />
      </div>
      
      <DataTable :value="budget.line_items" class="mb-4">
        <Column field="category" header="Category">
          <template #body="{ data, index }">
            <InputText v-model="data.category" class="w-full" />
          </template>
        </Column>
        <Column field="description" header="Description">
          <template #body="{ data, index }">
            <InputText v-model="data.description" class="w-full" />
          </template>
        </Column>
        <Column field="amount" header="Amount">
          <template #body="{ data, index }">
            <InputNumber v-model="data.amount" mode="currency" currency="USD" class="w-full" />
          </template>
        </Column>
        <Column header="Actions">
          <template #body="{ index }">
            <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="removeLineItem(index)" />
          </template>
        </Column>
      </DataTable>

      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="budgetDialog = false" />
        <Button label="Save Budget" @click="saveBudget" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { budgetService } from '@/api/budgetService';

interface Budget {
  id?: number
  name: string
  type: string
  amount: number
  period_start: string
  period_end: string
  status: string
  description?: string
  line_items: BudgetLineItem[]
}

interface BudgetLineItem {
  category: string
  description?: string
  amount: number
}

const toast = useToast();
const loading = ref(false);
const budgetDialog = ref(false);

const budgets = ref<Budget[]>([]);
const budget = ref<Budget>({
  name: '',
  type: 'OPERATIONAL',
  amount: 0,
  period_start: new Date().toISOString().split('T')[0],
  period_end: new Date(Date.now() + 365*24*60*60*1000).toISOString().split('T')[0],
  status: 'DRAFT',
  description: '',
  line_items: []
});

const stats = ref({
  totalBudgets: 0,
  totalAmount: 0,
  pendingApproval: 0,
  activeBudgets: 0
});

const showCreateDialog = () => {
  budget.value = {
    name: '',
    type: 'OPERATIONAL',
    amount: 0,
    period_start: new Date().toISOString().split('T')[0],
    period_end: new Date(Date.now() + 365*24*60*60*1000).toISOString().split('T')[0],
    status: 'DRAFT',
    description: '',
    line_items: []
  };
  budgetDialog.value = true;
};

const addLineItem = () => {
  budget.value.line_items.push({
    category: '',
    description: '',
    amount: 0
  });
};

const removeLineItem = (index: number) => {
  budget.value.line_items.splice(index, 1);
};

const saveBudget = async () => {
  try {
    budget.value.amount = budget.value.line_items.reduce((sum, item) => sum + item.amount, 0);
    await budgetService.createBudget(budget.value);
    toast.add({ severity: 'success', summary: 'Success', detail: 'Budget created successfully', life: 3000 });
    budgetDialog.value = false;
    loadBudgets();
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create budget', life: 3000 });
  }
};

const viewBudget = (budgetData: Budget) => {
  toast.add({ severity: 'info', summary: 'View Budget', detail: `Viewing ${budgetData.name}`, life: 3000 });
};

const editBudget = (budgetData: Budget) => {
  budget.value = { ...budgetData };
  budgetDialog.value = true;
};

const deleteBudget = async (budgetData: Budget) => {
  try {
    if (budgetData.id) {
      await budgetService.deleteBudget(budgetData.id);
      toast.add({ severity: 'success', summary: 'Success', detail: 'Budget deleted', life: 3000 });
      loadBudgets();
    }
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete budget', life: 3000 });
  }
};

const loadBudgets = async () => {
  loading.value = true;
  try {
    budgets.value = await budgetService.getBudgets();
    const summary = await budgetService.getBudgetSummary();
    stats.value = {
      totalBudgets: summary.total_budgets,
      totalAmount: summary.total_amount,
      pendingApproval: budgets.value.filter(b => b.status === 'PENDING_APPROVAL').length,
      activeBudgets: budgets.value.filter(b => b.status === 'APPROVED').length
    };
  } catch (error) {
    console.error('Error loading budgets:', error);
  } finally {
    loading.value = false;
  }
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US').format(amount);
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString();
};

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'APPROVED': return 'success';
    case 'DRAFT': return 'secondary';
    case 'PENDING_APPROVAL': return 'warning';
    case 'REJECTED': return 'danger';
    default: return 'info';
  }
};

onMounted(() => {
  loadBudgets();
});
</script>

<style scoped>
.budget-dashboard {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>