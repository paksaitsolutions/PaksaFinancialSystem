<template>
  <div class="tax-returns-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>FBR Tax Returns Management</h1>
        <p class="text-color-secondary">Manage Income Tax, Sales Tax & Withholding Tax Returns</p>
      </div>
      <Button label="File New Return" icon="pi pi-plus" @click="openNew" />
    </div>

    <!-- Quick Stats -->
    <div class="grid mb-4">
      <div class="col-12 md:col-3">
        <Card class="text-center">
          <template #content>
            <div class="text-2xl font-bold text-green-500">{{ stats.filed }}</div>
            <div class="text-sm text-color-secondary">Filed Returns</div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card class="text-center">
          <template #content>
            <div class="text-2xl font-bold text-orange-500">{{ stats.pending }}</div>
            <div class="text-sm text-color-secondary">Pending Returns</div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card class="text-center">
          <template #content>
            <div class="text-2xl font-bold text-red-500">{{ stats.overdue }}</div>
            <div class="text-sm text-color-secondary">Overdue Returns</div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card class="text-center">
          <template #content>
            <div class="text-2xl font-bold text-blue-500">{{ stats.amendments }}</div>
            <div class="text-sm text-color-secondary">Amendments</div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Filters -->
    <Card class="mb-4">
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-3">
            <label class="block mb-2">Tax Year</label>
            <Dropdown v-model="filters.taxYear" :options="taxYears" placeholder="Select Tax Year" class="w-full" />
          </div>
          <div class="col-12 md:col-3">
            <label class="block mb-2">Return Type</label>
            <Dropdown v-model="filters.returnType" :options="returnTypes" optionLabel="label" optionValue="value" placeholder="All Types" class="w-full" />
          </div>
          <div class="col-12 md:col-3">
            <label class="block mb-2">Status</label>
            <Dropdown v-model="filters.status" :options="statuses" optionLabel="label" optionValue="value" placeholder="All Status" class="w-full" />
          </div>
          <div class="col-12 md:col-3">
            <label class="block mb-2">&nbsp;</label>
            <Button label="Apply Filters" icon="pi pi-filter" @click="applyFilters" class="w-full" />
          </div>
        </div>
      </template>
    </Card>

    <!-- Returns Table -->
    <Card>
      <template #content>
        <DataTable :value="taxReturns" :loading="loading" paginator :rows="10" responsiveLayout="scroll">
          <Column field="return_id" header="Return ID" sortable />
          <Column field="tax_year" header="Tax Year" sortable />
          <Column field="return_type" header="Type" sortable>
            <template #body="{ data }">
              <Tag :value="data.return_type" :severity="getReturnTypeSeverity(data.return_type)" />
            </template>
          </Column>
          <Column field="due_date" header="Due Date" sortable>
            <template #body="{ data }">
              {{ formatDate(data.due_date) }}
            </template>
          </Column>
          <Column field="filed_date" header="Filed Date" sortable>
            <template #body="{ data }">
              {{ data.filed_date ? formatDate(data.filed_date) : '-' }}
            </template>
          </Column>
          <Column field="tax_liability" header="Tax Liability" sortable>
            <template #body="{ data }">
              Rs. {{ formatCurrency(data.tax_liability) }}
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text" @click="viewReturn(data)" v-tooltip="'View Details'" />
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editReturn(data)" v-tooltip="'Edit Return'" v-if="data.status === 'draft'" />
              <Button icon="pi pi-download" class="p-button-text p-button-info" @click="downloadReturn(data)" v-tooltip="'Download PDF'" />
              <Button icon="pi pi-send" class="p-button-text p-button-success" @click="fileReturn(data)" v-tooltip="'File Return'" v-if="data.status === 'draft'" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- New/Edit Return Dialog -->
    <Dialog v-model:visible="returnDialog" header="Tax Return Details" :modal="true" :style="{width: '800px'}">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Return Type</label>
            <Dropdown v-model="taxReturn.return_type" :options="returnTypes" optionLabel="label" optionValue="value" class="w-full" :class="{'p-invalid': submitted && !taxReturn.return_type}" />
            <small class="p-error" v-if="submitted && !taxReturn.return_type">Return type is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Tax Year</label>
            <Dropdown v-model="taxReturn.tax_year" :options="taxYears" class="w-full" :class="{'p-invalid': submitted && !taxReturn.tax_year}" />
            <small class="p-error" v-if="submitted && !taxReturn.tax_year">Tax year is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>NTN Number</label>
            <InputText v-model="taxReturn.ntn" class="w-full" placeholder="e.g., 1234567-8" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>CNIC/NICOP</label>
            <InputText v-model="taxReturn.cnic" class="w-full" placeholder="e.g., 12345-1234567-1" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Gross Income (Rs.)</label>
            <InputNumber v-model="taxReturn.gross_income" class="w-full" :minFractionDigits="2" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Taxable Income (Rs.)</label>
            <InputNumber v-model="taxReturn.taxable_income" class="w-full" :minFractionDigits="2" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Tax Liability (Rs.)</label>
            <InputNumber v-model="taxReturn.tax_liability" class="w-full" :minFractionDigits="2" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Advance Tax Paid (Rs.)</label>
            <InputNumber v-model="taxReturn.advance_tax_paid" class="w-full" :minFractionDigits="2" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Remarks</label>
            <Textarea v-model="taxReturn.remarks" class="w-full" rows="3" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="hideDialog" />
        <Button label="Save as Draft" class="p-button-secondary" @click="saveDraft" />
        <Button label="File Return" @click="saveReturn" />
      </template>
    </Dialog>

    <!-- View Return Dialog -->
    <Dialog v-model:visible="viewDialog" header="Tax Return Details" :modal="true" :style="{width: '900px'}">
      <div class="grid" v-if="selectedReturn">
        <div class="col-12">
          <h3>Return Information</h3>
          <Divider />
        </div>
        <div class="col-6"><strong>Return ID:</strong> {{ selectedReturn.return_id }}</div>
        <div class="col-6"><strong>Tax Year:</strong> {{ selectedReturn.tax_year }}</div>
        <div class="col-6"><strong>Return Type:</strong> {{ selectedReturn.return_type }}</div>
        <div class="col-6"><strong>Status:</strong> <Tag :value="selectedReturn.status" :severity="getStatusSeverity(selectedReturn.status)" /></div>
        <div class="col-6"><strong>NTN:</strong> {{ selectedReturn.ntn || 'N/A' }}</div>
        <div class="col-6"><strong>CNIC:</strong> {{ selectedReturn.cnic || 'N/A' }}</div>
        <div class="col-12">
          <h3>Financial Details</h3>
          <Divider />
        </div>
        <div class="col-6"><strong>Gross Income:</strong> Rs. {{ formatCurrency(selectedReturn.gross_income) }}</div>
        <div class="col-6"><strong>Taxable Income:</strong> Rs. {{ formatCurrency(selectedReturn.taxable_income) }}</div>
        <div class="col-6"><strong>Tax Liability:</strong> Rs. {{ formatCurrency(selectedReturn.tax_liability) }}</div>
        <div class="col-6"><strong>Advance Tax Paid:</strong> Rs. {{ formatCurrency(selectedReturn.advance_tax_paid) }}</div>
        <div class="col-12" v-if="selectedReturn.remarks">
          <strong>Remarks:</strong><br>
          {{ selectedReturn.remarks }}
        </div>
      </div>
      <template #footer>
        <Button label="Close" @click="viewDialog = false" />
        <Button label="Download PDF" icon="pi pi-download" @click="downloadReturn(selectedReturn)" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import taxReturnService, { type TaxReturn, type TaxReturnStats, type TaxReturnFilters } from '@/api/taxReturnService';

interface TaxReturnForm {
  id?: number;
  return_id: string;
  tax_year: string;
  return_type: string;
  ntn?: string;
  cnic?: string;
  gross_income: number;
  taxable_income: number;
  tax_liability: number;
  advance_tax_paid: number;
  due_date: string;
  filed_date?: string;
  status: string;
  remarks?: string;
}

const toast = useToast();
const loading = ref(false);
const returnDialog = ref(false);
const viewDialog = ref(false);
const submitted = ref(false);

const taxReturns = ref<TaxReturn[]>([]);
const selectedReturn = ref<TaxReturn | null>(null);
const taxReturn = ref<TaxReturnForm>({
  return_id: '',
  tax_year: '2024',
  return_type: 'income_tax',
  gross_income: 0,
  taxable_income: 0,
  tax_liability: 0,
  advance_tax_paid: 0,
  due_date: '',
  status: 'draft'
});

const stats = ref<TaxReturnStats>({
  filed: 0,
  pending: 0,
  overdue: 0,
  amendments: 0
});

const filters = ref({
  taxYear: '',
  returnType: '',
  status: ''
});

const taxYears = ref(['2024', '2023', '2022', '2021', '2020']);

const returnTypes = ref([
  { label: 'Income Tax Return', value: 'income_tax' },
  { label: 'Sales Tax Return', value: 'sales_tax' },
  { label: 'Withholding Tax Return', value: 'withholding_tax' },
  { label: 'Corporate Tax Return', value: 'corporate_tax' },
  { label: 'Wealth Statement', value: 'wealth_statement' }
]);

const statuses = ref([
  { label: 'Draft', value: 'draft' },
  { label: 'Filed', value: 'filed' },
  { label: 'Accepted', value: 'accepted' },
  { label: 'Rejected', value: 'rejected' },
  { label: 'Amended', value: 'amended' },
  { label: 'Overdue', value: 'overdue' }
]);

const openNew = () => {
  taxReturn.value = {
    return_id: `TR${Date.now()}`,
    tax_year: '2024',
    return_type: 'income_tax',
    gross_income: 0,
    taxable_income: 0,
    tax_liability: 0,
    advance_tax_paid: 0,
    due_date: '2024-12-31',
    status: 'draft'
  };
  submitted.value = false;
  returnDialog.value = true;
};

const editReturn = (ret: TaxReturn) => {
  taxReturn.value = {
    id: ret.id,
    return_id: ret.return_id,
    tax_year: ret.tax_year,
    return_type: ret.return_type,
    ntn: ret.ntn,
    cnic: ret.cnic,
    gross_income: ret.gross_income,
    taxable_income: ret.taxable_income,
    tax_liability: ret.tax_liability,
    advance_tax_paid: ret.advance_tax_paid,
    due_date: ret.due_date,
    filed_date: ret.filed_date,
    status: ret.status,
    remarks: ret.remarks
  };
  returnDialog.value = true;
};

const viewReturn = (ret: TaxReturn) => {
  selectedReturn.value = ret;
  viewDialog.value = true;
};

const hideDialog = () => {
  returnDialog.value = false;
  submitted.value = false;
};

const saveDraft = async () => {
  submitted.value = true;
  if (taxReturn.value.return_type && taxReturn.value.tax_year) {
    try {
      taxReturn.value.status = 'draft';
      await saveReturnData();
      toast.add({ severity: 'success', summary: 'Success', detail: 'Return saved as draft', life: 3000 });
    } catch (error: any) {
      toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'Save failed', life: 3000 });
    }
  }
};

const saveReturn = async () => {
  submitted.value = true;
  if (taxReturn.value.return_type && taxReturn.value.tax_year) {
    try {
      taxReturn.value.status = 'filed';
      taxReturn.value.filed_date = new Date().toISOString().split('T')[0];
      await saveReturnData();
      toast.add({ severity: 'success', summary: 'Success', detail: 'Return filed successfully', life: 3000 });
    } catch (error: any) {
      toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'Filing failed', life: 3000 });
    }
  }
};

const saveReturnData = async () => {
  try {
    if (taxReturn.value.id) {
      await taxReturnService.updateTaxReturn(taxReturn.value.id, taxReturn.value);
    } else {
      await taxReturnService.createTaxReturn(taxReturn.value);
    }
    returnDialog.value = false;
    await loadTaxReturns();
    await loadStats();
  } catch (error: any) {
    throw new Error(error.response?.data?.detail || 'Save failed');
  }
};

const fileReturn = async (ret: TaxReturn) => {
  try {
    if (ret.id) {
      await taxReturnService.fileTaxReturn(ret.id);
      toast.add({ severity: 'success', summary: 'Success', detail: 'Return filed with FBR', life: 3000 });
      await loadTaxReturns();
      await loadStats();
    }
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Filing failed', life: 3000 });
  }
};

const downloadReturn = (ret: TaxReturn) => {
  toast.add({ severity: 'info', summary: 'Download', detail: `Downloading ${ret.return_id}.pdf`, life: 3000 });
};

const applyFilters = async () => {
  await loadTaxReturns();
};

const getReturnTypeSeverity = (type: string) => {
  switch (type) {
    case 'income_tax': return 'success';
    case 'sales_tax': return 'info';
    case 'withholding_tax': return 'warning';
    default: return 'secondary';
  }
};

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'filed': case 'accepted': return 'success';
    case 'draft': return 'info';
    case 'rejected': case 'overdue': return 'danger';
    case 'amended': return 'warning';
    default: return 'secondary';
  }
};

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-GB');
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-PK').format(amount);
};

const loadStats = async () => {
  try {
    stats.value = await taxReturnService.getTaxReturnStats();
  } catch (error: any) {
    console.error('Error loading stats:', error);
  }
};

const loadTaxReturns = async () => {
  loading.value = true;
  try {
    const filterParams: TaxReturnFilters = {
      tax_year: filters.value.taxYear || undefined,
      return_type: filters.value.returnType || undefined,
      status: filters.value.status || undefined
    };
    taxReturns.value = await taxReturnService.getTaxReturns(filterParams);
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load tax returns', life: 3000 });
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await loadTaxReturns();
  await loadStats();
});
</script>

<style scoped>
.tax-returns-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>
