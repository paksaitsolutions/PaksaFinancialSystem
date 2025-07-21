<template>
  <div class="budget-view">
    <!-- Header Section -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-2xl font-bold">Budget Management</h1>
        <p class="text-gray-600">View and manage your organization's budgets</p>
      </div>
      <div class="flex gap-2">
        <Button 
          label="New Budget" 
          icon="pi pi-plus" 
          @click="openCreateDialog"
          class="p-button-primary"
        />
        <Button 
          label="Export" 
          icon="pi pi-download" 
          @click="showExportDialog = true" 
          :disabled="!budgets.length"
          :loading="isExporting"
          class="p-button-secondary"
        />
      </div>
    </div>

    <!-- Budget List -->
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <span>Budgets</span>
        </div>
      </template>
      
      <template #content>
        <!-- Filters -->
        <div class="grid mb-4">
          <div class="col-12 md:col-3">
            <span class="p-float-label">
              <InputText id="search" v-model="filters.search" class="w-full" />
              <label for="search">Search</label>
            </span>
          </div>
          <div class="col-12 md:col-3">
            <span class="p-float-label">
              <Dropdown 
                v-model="filters.status" 
                :options="budgetStatuses" 
                optionLabel="name" 
                optionValue="value" 
                class="w-full"
                showClear
              />
              <label>Status</label>
            </span>
          </div>
          <div class="col-12 md:col-3">
            <span class="p-float-label">
              <Dropdown 
                v-model="filters.type" 
                :options="budgetTypes" 
                optionLabel="name" 
                optionValue="value" 
                class="w-full"
                showClear
              />
              <label>Type</label>
            </span>
          </div>
          <div class="col-12 md:col-3 flex align-items-end">
            <Button 
              label="Clear" 
              icon="pi pi-filter-slash" 
              class="p-button-outlined w-full"
              @click="clearFilters"
            />
          </div>
        </div>

        <!-- Budgets Table -->
        <DataTable 
          :value="filteredBudgets" 
          :loading="loading" 
          :paginator="true" 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          v-model:selection="selectedBudgets"
          dataKey="id"
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
          
          <Column field="name" header="Name" :sortable="true">
            <template #body="{ data }">
              <a href="#" @click.prevent="openEditDialog(data)" class="text-primary">{{ data.name }}</a>
            </template>
          </Column>
          
          <Column field="amount" header="Amount" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.amount) }}
            </template>
          </Column>
          
          <Column field="type" header="Type" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.type" :severity="getBudgetTypeSeverity(data.type)" />
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          
          <Column field="startDate" header="Start Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.startDate) }}
            </template>
          </Column>
          
          <Column field="endDate" header="End Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.endDate) }}
            </template>
          </Column>
          
          <Column headerStyle="width: 10rem; text-align: center" bodyStyle="text-align: center; overflow: visible">
            <template #body="{ data }">
              <Button 
                icon="pi pi-pencil" 
                class="p-button-rounded p-button-text p-button-sm" 
                @click="openEditDialog(data)"
                v-tooltip.top="'Edit'"
              />
              <Button 
                icon="pi pi-trash" 
                class="p-button-rounded p-button-text p-button-sm p-button-danger" 
                @click="confirmDelete(data.id)"
                v-tooltip.top="'Delete'"
              />
              <Button 
                v-if="data.status === 'PENDING_APPROVAL'"
                icon="pi pi-check" 
                class="p-button-rounded p-button-text p-button-sm p-button-success" 
                @click="openApprovalDialog(data)"
                v-tooltip.top="'Approve'"
              />
              <Button 
                v-if="data.status === 'PENDING_APPROVAL'"
                icon="pi pi-times" 
                class="p-button-rounded p-button-text p-button-sm p-button-warning" 
                @click="openRejectDialog(data)"
                v-tooltip.top="'Reject'"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Budget Form Dialog -->
    <Dialog 
      v-model:visible="dialog.visible" 
      :style="{width: '650px'}" 
      :header="dialog.mode === 'create' ? 'New Budget' : 'Edit Budget'"
      :modal="true"
      :closable="!dialog.loading" 
      :closeOnEscape="!dialog.loading"
    >
      <BudgetForm 
        v-if="dialog.visible"
        :budget="form"
        :loading="dialog.loading"
        @submit="handleSave"
        @cancel="dialog.visible = false"
      />
    </Dialog>

    <!-- Approval Dialog -->
    <Dialog 
      v-model:visible="approvalDialog.visible" 
      :style="{width: '450px'}" 
      header="Approve Budget" 
      :modal="true"
    >
      <div class="confirmation-content">
        <i class="pi pi-check-circle mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to approve this budget?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="approvalDialog.visible = false" 
          :disabled="approvalDialog.loading"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-success" 
          @click="handleApproval" 
          :loading="approvalDialog.loading" 
        />
      </template>
    </Dialog>

    <!-- Reject Dialog -->
    <Dialog 
      v-model:visible="rejectDialog.visible" 
      :style="{width: '450px'}" 
      header="Reject Budget" 
      :modal="true"
    >
      <div class="field">
        <label for="rejectReason">Reason for rejection</label>
        <Textarea 
          id="rejectReason" 
          v-model="rejectNotes" 
          :autoResize="true" 
          rows="3" 
          class="w-full"
          :class="{'p-invalid': rejectDialog.error}"
        />
        <small v-if="rejectDialog.error" class="p-error">{{ rejectDialog.error }}</small>
      </div>
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="rejectDialog.visible = false"
          :disabled="rejectDialog.loading"
        />
        <Button 
          label="Reject" 
          icon="pi pi-times" 
          class="p-button-danger" 
          @click="rejectBudget" 
          :loading="rejectDialog.loading"
        />
      </template>
    </Dialog>

    <!-- Export Dialog -->
    <ExportDialog 
      v-model:visible="showExportDialog"
      :formats="['pdf', 'excel', 'csv']"
      :loading="isExporting"
      @export="exportBudgets"
    />

    <!-- Delete Confirmation -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useBudgetStore } from '../store/budgetStore';
import type { Budget, BudgetStatus } from '../types/budget.types';

// Initialize stores and utilities
const budgetStore = useBudgetStore();
const toast = useToast();

// Refs
const dialog = ref({
  visible: false,
  loading: false,
  mode: 'create' as 'create' | 'edit',
  budget: null as Budget | null
});

const approvalDialog = ref(false);
const rejectDialog = ref({
  visible: false,
  loading: false,
  error: ''
});
const rejectNotes = ref('');
const approvalNotes = ref('');
const selectedBudget = ref<Budget | null>(null);
const loading = ref(false);

// Computed
const budgets = computed(() => budgetStore.budgets);
const filteredBudgets = computed(() => {
  // Add filtering logic here
  return budgetStore.budgets;
});

// Methods
const openCreateDialog = () => {
  dialog.value = {
    visible: true,
    loading: false,
    mode: 'create',
    budget: null
  };
};

const openEditDialog = (budget: Budget) => {
  selectedBudget.value = budget;
  dialog.value = {
    visible: true,
    loading: false,
    mode: 'edit',
    budget: { ...budget }
  };
};

const openRejectDialog = (budget: Budget) => {
  selectedBudget.value = budget;
  rejectNotes.value = '';
  rejectDialog.value = {
    ...rejectDialog.value,
    visible: true,
    error: ''
  };
};

const approveBudget = async (): Promise<void> => {
  if (!selectedBudget.value) return;
  
  try {
    loading.value = true;
    await budgetStore.approveBudget(selectedBudget.value.id, approvalNotes.value);
    approvalDialog.value = false;
    await budgetStore.fetchBudgets();
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Budget approved successfully',
      life: 3000
    });
  } catch (error) {
    console.error('Error approving budget:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to approve budget',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

const rejectBudget = async (): Promise<void> => {
  if (!selectedBudget.value) {
    toast.add({
      severity: 'warn',
      summary: 'No Budget Selected',
      detail: 'Please select a budget to reject',
      life: 5000
    });
    return;
  }
  
  if (!rejectNotes.value?.trim()) {
    rejectDialog.value.error = 'Please provide a reason for rejection';
    return;
  }
  
  try {
    rejectDialog.value.loading = true;
    await budgetStore.rejectBudget(selectedBudget.value.id, rejectNotes.value);
    
    // Clear the form and close the dialog
    rejectNotes.value = '';
    rejectDialog.value.visible = false;
    
    // Refresh the budget list
    await budgetStore.fetchBudgets();
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Budget rejected successfully',
      life: 3000
    });
  } catch (error) {
    console.error('Error in rejectBudget:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error instanceof Error ? error.message : 'Failed to reject budget',
      life: 5000
    });
  } finally {
    rejectDialog.value.loading = false;
  }
};

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD', // TODO: Make this dynamic based on user preferences
    minimumFractionDigits: 2
  }).format(value);
};

const getStatusSeverity = (status: BudgetStatus): string => {
  switch (status) {
    case BudgetStatus.APPROVED: return 'success';
    case BudgetStatus.REJECTED: return 'danger';
    case BudgetStatus.SUBMITTED: return 'info';
    case BudgetStatus.ARCHIVED: return 'secondary';
    case BudgetStatus.DRAFT: return 'warning';
    default: return 'warning';
  }
};

const getStatusColor = (status: BudgetStatus): string => {
  switch (status) {
    case BudgetStatus.DRAFT: return 'blue';
    case BudgetStatus.APPROVED: return 'green';
    case BudgetStatus.REJECTED: return 'red';
    case BudgetStatus.ARCHIVED: return 'grey';
    default: return 'orange';
  }
};

// Lifecycle hooks
onMounted(async () => {
  try {
    loading.value = true;
    await budgetStore.fetchBudgets();
  } catch (error) {
    console.error('Error initializing budget view:', error);
    toast.add({
      severity: 'error',
      summary: 'Initialization Error',
      detail: 'Failed to load budget data',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
});
</script>
