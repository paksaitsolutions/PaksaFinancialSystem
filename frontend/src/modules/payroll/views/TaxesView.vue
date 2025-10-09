<template>
  <div class="taxes-view">
    <div class="grid">
      <div class="col-12">
        <div class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center mb-4 gap-3">
          <div>
            <h1>Payroll Taxes</h1>
            <Breadcrumb :home="home" :model="breadcrumbItems" class="mb-4" />
          </div>
          <div>
            <Button 
              label="New Tax Entry" 
              icon="pi pi-plus" 
              class="p-button-success" 
              @click="showNewTaxDialog" 
            />
          </div>
        </div>
      </div>

      <!-- Tax Entries List -->
      <div class="col-12">
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3>Tax Entries</h3>
              <div class="flex gap-2">
                <InputText 
                  v-model="filters['global'].value" 
                  placeholder="Search taxes..." 
                  class="p-inputtext-sm"
                />
                <Button 
                  icon="pi pi-refresh" 
                  class="p-button-text" 
                  @click="loadTaxes" 
                  :loading="loading"
                />
              </div>
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="taxes" 
              :paginator="true" 
              :rows="10"
              :loading="loading"
              :filters="filters"
              :globalFilterFields="['tax_type', 'employee.name', 'jurisdiction']"
              :rowsPerPageOptions="[5,10,25,50]"
              class="p-datatable-sm"
              responsiveLayout="scroll"
            >
              <template #empty>No tax entries found.</template>
              <Column field="tax_type" header="Tax Type" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.tax_type" :severity="getTaxTypeSeverity(data.tax_type)" />
                </template>
              </Column>
              <Column field="employee.name" header="Employee" :sortable="true" />
              <Column field="jurisdiction" header="Jurisdiction" :sortable="true" />
              <Column field="amount" header="Amount" :sortable="true">
                <template #body="{ data }">
                  <span class="font-medium">${{ formatCurrency(data.amount) }}</span>
                </template>
              </Column>
              <Column field="tax_period" header="Period" :sortable="true" />
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
                      @click="editTax(data)" 
                      v-tooltip.top="'Edit Tax'"
                    />
                    <Button 
                      icon="pi pi-trash" 
                      class="p-button-text p-button-sm p-button-danger" 
                      @click="confirmDeleteTax(data)" 
                      v-tooltip.top="'Delete Tax'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- Tax Dialog -->
    <Dialog 
      v-model:visible="taxDialog" 
      :style="{width: '650px', maxWidth: '95vw'}" 
      :header="editing ? 'Edit Tax Entry' : 'New Tax Entry'" 
      :modal="true"
      :closable="!submitting"
      class="p-fluid"
    >
      <div class="field">
        <label for="tax_type">Tax Type <span class="text-red-500">*</span></label>
        <Dropdown 
          id="tax_type" 
          v-model="tax.tax_type" 
          :options="taxTypes" 
          optionLabel="label" 
          optionValue="value" 
          placeholder="Select tax type"
          :class="{'p-invalid': submitted && !tax.tax_type}"
        />
        <small class="p-error" v-if="submitted && !tax.tax_type">Tax type is required.</small>
      </div>

      <div class="field">
        <label for="employee">Employee <span class="text-red-500">*</span></label>
        <Dropdown 
          id="employee" 
          v-model="tax.employeeId" 
          :options="employees" 
          optionLabel="name" 
          optionValue="id" 
          placeholder="Select employee"
          :class="{'p-invalid': submitted && !tax.employeeId}"
          filter
        />
        <small class="p-error" v-if="submitted && !tax.employeeId">Employee is required.</small>
      </div>

      <div class="field">
        <label for="jurisdiction">Jurisdiction</label>
        <Dropdown 
          id="jurisdiction" 
          v-model="tax.jurisdiction" 
          :options="jurisdictions" 
          optionLabel="label" 
          optionValue="value" 
          placeholder="Select jurisdiction"
        />
      </div>

      <div class="field">
        <label for="amount">Amount <span class="text-red-500">*</span></label>
        <InputNumber 
          id="amount" 
          v-model="tax.amount" 
          mode="currency" 
          currency="USD" 
          locale="en-US"
          :class="{'p-invalid': submitted && !tax.amount}"
        />
        <small class="p-error" v-if="submitted && !tax.amount">Amount is required.</small>
      </div>

      <div class="field">
        <label for="tax_period">Tax Period</label>
        <InputText 
          id="tax_period" 
          v-model="tax.tax_period" 
          placeholder="e.g., 2024-Q1, 2024-01"
        />
      </div>

      <div class="field">
        <label for="description">Description</label>
        <Textarea id="description" v-model="tax.description" rows="3" />
      </div>

      <div class="field">
        <label for="status">Status</label>
        <Dropdown 
          id="status" 
          v-model="tax.status" 
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
          @click="saveTax" 
          :loading="submitting"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deleteTaxDialog" 
      :style="{width: '450px'}" 
      header="Confirm" 
      :modal="true"
    >
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="tax">Are you sure you want to delete this tax entry?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="deleteTaxDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="deleteTax"
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
const taxes = ref([]);
const employees = ref([]);
const tax = ref({
  id: null,
  tax_type: '',
  employeeId: null,
  jurisdiction: 'federal',
  amount: 0,
  tax_period: '',
  description: '',
  status: 'active'
});

// UI State
const loading = ref(false);
const submitting = ref(false);
const deleting = ref(false);
const taxDialog = ref(false);
const deleteTaxDialog = ref(false);
const editing = ref(false);
const submitted = ref(false);

// Filters
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS }
});

// Breadcrumb
const home = ref({ icon: 'pi pi-home', to: '/' });
const breadcrumbItems = ref([
  { label: 'Payroll', to: '/payroll' },
  { label: 'Taxes' }
]);

// Options
const taxTypes = ref([
  { label: 'Federal Income Tax', value: 'federal_income' },
  { label: 'State Income Tax', value: 'state_income' },
  { label: 'Social Security', value: 'social_security' },
  { label: 'Medicare', value: 'medicare' },
  { label: 'State Unemployment', value: 'state_unemployment' },
  { label: 'Federal Unemployment', value: 'federal_unemployment' },
  { label: 'State Disability', value: 'state_disability' },
  { label: 'Local Tax', value: 'local' }
]);

const jurisdictions = ref([
  { label: 'Federal', value: 'federal' },
  { label: 'State', value: 'state' },
  { label: 'Local', value: 'local' }
]);

const statuses = ref([
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'Pending', value: 'pending' }
]);

// Methods
const loadTaxes = async () => {
  loading.value = true;
  try {
    const response = await payrollService.getTaxes();
    taxes.value = response.data || [];
  } catch (error) {
    console.error('Error loading taxes:', error);
    // Use mock data as fallback
    taxes.value = [
      {
        id: '1',
        tax_type: 'federal_income',
        jurisdiction: 'federal',
        amount: 1500.00,
        tax_period: '2024-Q1',
        status: 'active',
        employee: { name: 'John Doe' }
      },
      {
        id: '2',
        tax_type: 'state_income',
        jurisdiction: 'state',
        amount: 800.00,
        tax_period: '2024-Q1',
        status: 'active',
        employee: { name: 'Jane Smith' }
      }
    ];
    toast.add({
      severity: 'warn',
      summary: 'Warning',
      detail: 'Using sample data - API not available',
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
    // Use mock data as fallback
    employees.value = [
      { id: '1', name: 'John Doe' },
      { id: '2', name: 'Jane Smith' }
    ];
  }
};

const showNewTaxDialog = () => {
  tax.value = {
    id: null,
    tax_type: '',
    employeeId: null,
    jurisdiction: 'federal',
    amount: 0,
    tax_period: '',
    description: '',
    status: 'active'
  };
  editing.value = false;
  submitted.value = false;
  taxDialog.value = true;
};

const editTax = (data: any) => {
  tax.value = { ...data };
  editing.value = true;
  submitted.value = false;
  taxDialog.value = true;
};

const hideDialog = () => {
  taxDialog.value = false;
  submitted.value = false;
};

const saveTax = async () => {
  submitted.value = true;
  
  if (!tax.value.tax_type || !tax.value.employeeId || !tax.value.amount) {
    return;
  }

  submitting.value = true;
  try {
    if (editing.value) {
      await payrollService.updateTax(tax.value.id, tax.value);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Tax entry updated successfully',
        life: 3000
      });
    } else {
      await payrollService.createTax(tax.value);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Tax entry created successfully',
        life: 3000
      });
    }
    
    hideDialog();
    await loadTaxes();
  } catch (error) {
    console.error('Error saving tax:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save tax entry',
      life: 3000
    });
  } finally {
    submitting.value = false;
  }
};

const confirmDeleteTax = (data: any) => {
  tax.value = data;
  deleteTaxDialog.value = true;
};

const deleteTax = async () => {
  deleting.value = true;
  try {
    await payrollService.deleteTax(tax.value.id);
    deleteTaxDialog.value = false;
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Tax entry deleted successfully',
      life: 3000
    });
    await loadTaxes();
  } catch (error) {
    console.error('Error deleting tax:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete tax entry',
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

const getTaxTypeSeverity = (type: string) => {
  const severityMap: { [key: string]: string } = {
    federal_income: 'danger',
    state_income: 'warning',
    social_security: 'info',
    medicare: 'info',
    state_unemployment: 'secondary',
    federal_unemployment: 'secondary',
    state_disability: 'secondary',
    local: 'success'
  };
  return severityMap[type] || 'secondary';
};

const getStatusSeverity = (status: string) => {
  const severityMap: { [key: string]: string } = {
    active: 'success',
    inactive: 'secondary',
    pending: 'warning'
  };
  return severityMap[status] || 'secondary';
};

// Lifecycle
onMounted(() => {
  loadTaxes();
  loadEmployees();
});
</script>

<style scoped>
.taxes-view {
  padding: 1rem;
}
</style>