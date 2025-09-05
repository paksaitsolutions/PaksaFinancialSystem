<template>
  <div class="budgeting-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Budget Planning</h1>
        <p class="text-color-secondary">Create and manage detailed budgets</p>
      </div>
      <div class="flex gap-2">
        <Button label="Import Template" icon="pi pi-upload" class="p-button-outlined" @click="importTemplate" />
        <Button label="Export Budget" icon="pi pi-download" class="p-button-outlined" @click="exportBudget" />
      </div>
    </div>

    <div class="grid">
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>Budget Details</template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label>Budget Name</label>
                  <InputText v-model="currentBudget.name" class="w-full" />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label>Fiscal Year</label>
                  <InputNumber v-model="currentBudget.fiscal_year" class="w-full" />
                </div>
              </div>
              <div class="col-12">
                <div class="field">
                  <label>Description</label>
                  <Textarea v-model="currentBudget.description" rows="3" class="w-full" />
                </div>
              </div>
            </div>

            <Divider />

            <div class="flex justify-content-between align-items-center mb-3">
              <h4>Budget Line Items</h4>
              <Button label="Add Item" icon="pi pi-plus" size="small" @click="addBudgetItem" />
            </div>

            <DataTable :value="currentBudget.line_items" editMode="cell" @cell-edit-complete="onCellEditComplete">
              <Column field="account_code" header="Account Code">
                <template #editor="{ data, field }">
                  <InputText v-model="data[field]" class="w-full" />
                </template>
              </Column>
              <Column field="account_name" header="Account Name">
                <template #editor="{ data, field }">
                  <InputText v-model="data[field]" class="w-full" />
                </template>
              </Column>
              <Column field="category" header="Category">
                <template #editor="{ data, field }">
                  <Dropdown v-model="data[field]" :options="categories" class="w-full" />
                </template>
              </Column>
              <Column field="budgeted_amount" header="Budgeted Amount">
                <template #body="{ data }">
                  ${{ formatCurrency(data.budgeted_amount) }}
                </template>
                <template #editor="{ data, field }">
                  <InputNumber v-model="data[field]" mode="currency" currency="USD" class="w-full" />
                </template>
              </Column>
              <Column field="actual_amount" header="Actual Amount">
                <template #body="{ data }">
                  ${{ formatCurrency(data.actual_amount || 0) }}
                </template>
              </Column>
              <Column field="variance" header="Variance">
                <template #body="{ data }">
                  <span :class="getVarianceClass(data.variance || 0)">
                    ${{ formatCurrency(data.variance || 0) }}
                  </span>
                </template>
              </Column>
              <Column header="Actions">
                <template #body="{ index }">
                  <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="removeBudgetItem(index)" />
                </template>
              </Column>
            </DataTable>

            <div class="flex justify-content-end mt-4">
              <div class="text-right">
                <div class="text-lg font-bold">
                  Total Budget: ${{ formatCurrency(totalBudget) }}
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 lg:col-4">
        <Card>
          <template #title>Budget Summary</template>
          <template #content>
            <div class="flex flex-column gap-3">
              <div class="flex justify-content-between">
                <span>Total Budgeted:</span>
                <span class="font-bold">${{ formatCurrency(totalBudget) }}</span>
              </div>
              <div class="flex justify-content-between">
                <span>Total Actual:</span>
                <span class="font-bold">${{ formatCurrency(totalActual) }}</span>
              </div>
              <div class="flex justify-content-between">
                <span>Variance:</span>
                <span :class="getVarianceClass(totalVariance)" class="font-bold">
                  ${{ formatCurrency(totalVariance) }}
                </span>
              </div>
              <Divider />
              <div class="flex justify-content-between">
                <span>Status:</span>
                <Tag :value="currentBudget.status || 'draft'" :severity="getStatusSeverity(currentBudget.status || 'draft')" />
              </div>
            </div>
          </template>
        </Card>

        <Card class="mt-4">
          <template #title>Actions</template>
          <template #content>
            <div class="flex flex-column gap-2">
              <Button label="Save Draft" icon="pi pi-save" class="w-full" @click="saveBudget" />
              <Button label="Submit for Approval" icon="pi pi-send" class="w-full p-button-success" @click="submitForApproval" />
              <Button label="Copy from Previous Year" icon="pi pi-copy" class="w-full p-button-outlined" @click="copyFromPrevious" />
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import budgetService, { type Budget, type BudgetLineItem } from '@/services/budgetService';

const toast = useToast();

const currentBudget = ref<Budget>({
  name: '',
  description: '',
  fiscal_year: new Date().getFullYear(),
  start_date: '',
  end_date: '',
  line_items: []
});

const categories = ref([
  'Revenue',
  'Cost of Goods Sold',
  'Operating Expenses',
  'Administrative Expenses',
  'Marketing Expenses',
  'Capital Expenditures'
]);

const totalBudget = computed(() => {
  return currentBudget.value.line_items.reduce((sum, item) => sum + (item.budgeted_amount || 0), 0);
});

const totalActual = computed(() => {
  return currentBudget.value.line_items.reduce((sum, item) => sum + (item.actual_amount || 0), 0);
});

const totalVariance = computed(() => {
  return totalActual.value - totalBudget.value;
});

const addBudgetItem = () => {
  currentBudget.value.line_items.push({
    account_code: '',
    account_name: '',
    category: '',
    budgeted_amount: 0,
    actual_amount: 0,
    variance: 0
  });
};

const removeBudgetItem = (index: number) => {
  currentBudget.value.line_items.splice(index, 1);
};

const onCellEditComplete = (event: any) => {
  const { data, newValue, field } = event;
  data[field] = newValue;
  
  // Recalculate variance if amounts change
  if (field === 'budgeted_amount' || field === 'actual_amount') {
    data.variance = (data.actual_amount || 0) - (data.budgeted_amount || 0);
  }
};

const saveBudget = async () => {
  try {
    if (currentBudget.value.id) {
      await budgetService.updateBudget(currentBudget.value.id, currentBudget.value);
      toast.add({ severity: 'success', summary: 'Success', detail: 'Budget updated', life: 3000 });
    } else {
      const saved = await budgetService.createBudget(currentBudget.value);
      currentBudget.value.id = saved.id;
      toast.add({ severity: 'success', summary: 'Success', detail: 'Budget saved', life: 3000 });
    }
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save budget', life: 3000 });
  }
};

const submitForApproval = async () => {
  try {
    currentBudget.value.status = 'pending_approval';
    await saveBudget();
    toast.add({ severity: 'success', summary: 'Success', detail: 'Budget submitted for approval', life: 3000 });
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to submit budget', life: 3000 });
  }
};

const copyFromPrevious = () => {
  toast.add({ severity: 'info', summary: 'Copy Budget', detail: 'Copying from previous year...', life: 3000 });
};

const importTemplate = () => {
  toast.add({ severity: 'info', summary: 'Import', detail: 'Import template functionality', life: 3000 });
};

const exportBudget = () => {
  toast.add({ severity: 'info', summary: 'Export', detail: 'Exporting budget...', life: 3000 });
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US').format(amount);
};

const getVarianceClass = (variance: number) => {
  if (variance > 0) return 'text-green-600';
  if (variance < 0) return 'text-red-600';
  return 'text-gray-600';
};

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'active': return 'success';
    case 'draft': return 'warning';
    case 'pending_approval': return 'info';
    default: return 'info';
  }
};

onMounted(() => {
  // Initialize with some sample data
  addBudgetItem();
});
</script>

<style scoped>
.budgeting-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>