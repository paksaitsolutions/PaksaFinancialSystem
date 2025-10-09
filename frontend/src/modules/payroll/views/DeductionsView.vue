<template>
  <div class="deductions-view">
    <div class="grid">
      <div class="col-12">
        <div class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center mb-4 gap-3">
          <div>
            <h1>Payroll Deductions</h1>
            <Breadcrumb :home="home" :model="breadcrumbItems" class="mb-4" />
          </div>
          <div>
            <Button 
              label="New Deduction" 
              icon="pi pi-plus" 
              class="p-button-success" 
              @click="showNewDeductionDialog" 
            />
          </div>
        </div>
      </div>

      <!-- Deductions List -->
      <div class="col-12">
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3>Deductions</h3>
              <div class="flex gap-2">
                <InputText 
                  v-model="filters['global'].value" 
                  placeholder="Search deductions..." 
                  class="p-inputtext-sm"
                />
                <Button 
                  icon="pi pi-refresh" 
                  class="p-button-text" 
                  @click="loadDeductions" 
                  :loading="loading"
                />
              </div>
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="deductions" 
              :paginator="true" 
              :rows="10"
              :loading="loading"
              :filters="filters"
              :globalFilterFields="['name', 'type', 'employee.name']"
              :rowsPerPageOptions="[5,10,25,50]"
              class="p-datatable-sm"
              responsiveLayout="scroll"
            >
              <template #empty>No deductions found.</template>
              <Column field="name" header="Deduction Name" :sortable="true">
                <template #body="{ data }">
                  <span class="font-medium">{{ data.name }}</span>
                </template>
              </Column>
              <Column field="type" header="Type" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.type" :severity="getTypeSeverity(data.type)" />
                </template>
              </Column>
              <Column field="employee.name" header="Employee" :sortable="true" />
              <Column field="amount" header="Amount" :sortable="true">
                <template #body="{ data }">
                  <span class="font-medium">${{ formatCurrency(data.amount) }}</span>
                </template>
              </Column>
              <Column field="frequency" header="Frequency" :sortable="true" />
              <Column field="status" header="Status" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column header="Actions" style="min-width: 10rem">
                <template #body="{ data }">
                  <div class="flex gap-2">
                    <Button 
                      icon="pi pi-pencil" 
                      class="p-button-text p-button-sm p-button-warning" 
                      @click="editDeduction(data)" 
                      v-tooltip.top="'Edit Deduction'"
                    />
                    <Button 
                      icon="pi pi-trash" 
                      class="p-button-text p-button-sm p-button-danger" 
                      @click="confirmDeleteDeduction(data)" 
                      v-tooltip.top="'Delete Deduction'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- Deduction Dialog -->
    <Dialog 
      v-model:visible="deductionDialog" 
      :style="{width: '650px', maxWidth: '95vw'}" 
      :header="editing ? 'Edit Deduction' : 'New Deduction'" 
      :modal="true"
      :closable="!submitting"
      class="p-fluid"
    >
      <div class="field">
        <label for="name">Deduction Name <span class="text-red-500">*</span></label>
        <InputText 
          id="name" 
          v-model.trim="deduction.name" 
          required="true" 
          autofocus 
          :class="{'p-invalid': submitted && !deduction.name}" 
        />
        <small class="p-error" v-if="submitted && !deduction.name">Name is required.</small>
      </div>

      <div class="field">
        <label for="type">Type <span class="text-red-500">*</span></label>
        <Dropdown 
          id="type" 
          v-model="deduction.type" 
          :options="deductionTypes" 
          optionLabel="label" 
          optionValue="value" 
          placeholder="Select deduction type"
          :class="{'p-invalid': submitted && !deduction.type}"
        />
        <small class="p-error" v-if="submitted && !deduction.type">Type is required.</small>
      </div>

      <div class="field">
        <label for="employee">Employee <span class="text-red-500">*</span></label>
        <Dropdown 
          id="employee" 
          v-model="deduction.employeeId" 
          :options="employees" 
          optionLabel="name" 
          optionValue="id" 
          placeholder="Select employee"
          :class="{'p-invalid': submitted && !deduction.employeeId}"
          filter
        />
        <small class="p-error" v-if="submitted && !deduction.employeeId">Employee is required.</small>
      </div>

      <div class="field">
        <label for="amount">Amount <span class="text-red-500">*</span></label>
        <InputNumber 
          id="amount" 
          v-model="deduction.amount" 
          mode="currency" 
          currency="USD" 
          locale="en-US"
          :class="{'p-invalid': submitted && !deduction.amount}"
        />
        <small class="p-error" v-if="submitted && !deduction.amount">Amount is required.</small>
      </div>

      <div class="field">
        <label for="frequency">Frequency</label>
        <Dropdown 
          id="frequency" 
          v-model="deduction.frequency" 
          :options="frequencies" 
          optionLabel="label" 
          optionValue="value" 
          placeholder="Select frequency"
        />
      </div>

      <div class="field">
        <label for="description">Description</label>
        <Textarea id="description" v-model="deduction.description" rows="3" />
      </div>

      <div class="field">
        <label for="status">Status</label>
        <Dropdown 
          id="status" 
          v-model="deduction.status" 
          :options="statuses" 
          optionLabel="label" 
          optionValue="value"
        />
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="hideDialog" 
          :disabled="submitting"
        />
        <Button 
          :label="editing ? 'Update' : 'Save'" 
          icon="pi pi-check" 
          class="p-button-text" 
          @click="saveDeduction" 
          :loading="submitting"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deleteDeductionDialog" 
      :style="{width: '450px'}" 
      header="Confirm" 
      :modal="true"
    >
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="deduction">Are you sure you want to delete <b>{{ deduction.name }}</b>?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="deleteDeductionDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="deleteDeduction"
          :loading="deleting"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'primevue/usetoast';
import { payrollService } from '@/services/payrollService';

const toast = useToast();

// Data
const deductions = ref([]);
const employees = ref([]);
const deduction = ref({
  id: null,
  name: '',
  type: '',
  employeeId: null,
  amount: 0,
  frequency: 'monthly',
  description: '',
  status: 'active'
});

// UI State
const loading = ref(false);
const submitting = ref(false);
const deleting = ref(false);
const deductionDialog = ref(false);
const deleteDeductionDialog = ref(false);
const editing = ref(false);
const submitted = ref(false);

// Filters
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS }
});

// Options
const deductionTypes = ref([
  { label: 'Health Insurance', value: 'health_insurance' },
  { label: 'Dental Insurance', value: 'dental_insurance' },
  { label: '401k Contribution', value: '401k' },
  { label: 'Life Insurance', value: 'life_insurance' },
  { label: 'Union Dues', value: 'union_dues' },
  { label: 'Parking', value: 'parking' },
  { label: 'Other', value: 'other' }
]);

const frequencies = ref([
  { label: 'Weekly', value: 'weekly' },
  { label: 'Bi-weekly', value: 'biweekly' },
  { label: 'Monthly', value: 'monthly' },
  { label: 'Quarterly', value: 'quarterly' },
  { label: 'Annually', value: 'annually' }
]);

const statuses = ref([
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'Suspended', value: 'suspended' }
]);

// Breadcrumb
const home = ref({ icon: 'pi pi-home', to: '/' });
const breadcrumbItems = ref([
  { label: 'Payroll', to: '/payroll' },
  { label: 'Deductions' }
]);

// Methods
const loadDeductions = async () => {
  loading.value = true;
  try {
    const response = await payrollService.getDeductions();
    deductions.value = response.data || [];
  } catch (error) {
    console.error('Error loading deductions:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load deductions',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};

const loadEmployees = async () => {
  try {
    const response = await payrollService.getEmployees();
    employees.value = response.data || [];
  } catch (error) {
    console.error('Error loading employees:', error);
  }
};

const showNewDeductionDialog = () => {
  deduction.value = {
    id: null,
    name: '',
    type: '',
    employeeId: null,
    amount: 0,
    frequency: 'monthly',
    description: '',
    status: 'active'
  };
  editing.value = false;
  submitted.value = false;
  deductionDialog.value = true;
};

const editDeduction = (data: any) => {
  deduction.value = { ...data };
  editing.value = true;
  submitted.value = false;
  deductionDialog.value = true;
};

const hideDialog = () => {
  deductionDialog.value = false;
  submitted.value = false;
};

const saveDeduction = async () => {
  submitted.value = true;
  
  if (!deduction.value.name || !deduction.value.type || !deduction.value.employeeId || !deduction.value.amount) {
    return;
  }

  submitting.value = true;
  try {
    if (editing.value) {
      await payrollService.updateDeduction(deduction.value.id, deduction.value);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Deduction updated successfully',
        life: 3000
      });
    } else {
      await payrollService.createDeduction(deduction.value);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Deduction created successfully',
        life: 3000
      });
    }
    
    hideDialog();
    await loadDeductions();
  } catch (error) {
    console.error('Error saving deduction:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save deduction',
      life: 3000
    });
  } finally {
    submitting.value = false;
  }
};

const confirmDeleteDeduction = (data: any) => {
  deduction.value = data;
  deleteDeductionDialog.value = true;
};

const deleteDeduction = async () => {
  deleting.value = true;
  try {
    await payrollService.deleteDeduction(deduction.value.id);
    deleteDeductionDialog.value = false;
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Deduction deleted successfully',
      life: 3000
    });
    await loadDeductions();
  } catch (error) {
    console.error('Error deleting deduction:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete deduction',
      life: 3000
    });
  } finally {
    deleting.value = false;
  }
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

const getTypeSeverity = (type: string) => {
  const severityMap: { [key: string]: string } = {
    health_insurance: 'info',
    dental_insurance: 'info',
    '401k': 'success',
    life_insurance: 'warning',
    union_dues: 'secondary',
    parking: 'secondary',
    other: 'secondary'
  };
  return severityMap[type] || 'secondary';
};

const getStatusSeverity = (status: string) => {
  const severityMap: { [key: string]: string } = {
    active: 'success',
    inactive: 'secondary',
    suspended: 'warning'
  };
  return severityMap[status] || 'secondary';
};

// Lifecycle
onMounted(async () => {
  await Promise.all([loadDeductions(), loadEmployees()]);
});
</script>

<style scoped>
.deductions-view {
  padding: 1rem;
}
</style>