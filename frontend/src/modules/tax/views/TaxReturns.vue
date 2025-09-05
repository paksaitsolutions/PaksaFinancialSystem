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
          <Column field="returnId" header="Return ID" sortable />
          <Column field="taxYear" header="Tax Year" sortable />
          <Column field="returnType" header="Type" sortable>
            <template #body="{ data }">
              <Tag :value="data.returnType" :severity="getReturnTypeSeverity(data.returnType)" />
            </template>
          </Column>
          <Column field="dueDate" header="Due Date" sortable>
            <template #body="{ data }">
              {{ formatDate(data.dueDate) }}
            </template>
          </Column>
          <Column field="filedDate" header="Filed Date" sortable>
            <template #body="{ data }">
              {{ data.filedDate ? formatDate(data.filedDate) : '-' }}
            </template>
          </Column>
          <Column field="taxLiability" header="Tax Liability" sortable>
            <template #body="{ data }">
              Rs. {{ formatCurrency(data.taxLiability) }}
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
            <Dropdown v-model="taxReturn.returnType" :options="returnTypes" optionLabel="label" optionValue="value" class="w-full" :class="{'p-invalid': submitted && !taxReturn.returnType}" />
            <small class="p-error" v-if="submitted && !taxReturn.returnType">Return type is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Tax Year</label>
            <Dropdown v-model="taxReturn.taxYear" :options="taxYears" class="w-full" :class="{'p-invalid': submitted && !taxReturn.taxYear}" />
            <small class="p-error" v-if="submitted && !taxReturn.taxYear">Tax year is required.</small>
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
            <InputNumber v-model="taxReturn.grossIncome" class="w-full" :minFractionDigits="2" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Taxable Income (Rs.)</label>
            <InputNumber v-model="taxReturn.taxableIncome" class="w-full" :minFractionDigits="2" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Tax Liability (Rs.)</label>
            <InputNumber v-model="taxReturn.taxLiability" class="w-full" :minFractionDigits="2" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Advance Tax Paid (Rs.)</label>
            <InputNumber v-model="taxReturn.advanceTaxPaid" class="w-full" :minFractionDigits="2" />
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
        <div class="col-6"><strong>Return ID:</strong> {{ selectedReturn.returnId }}</div>
        <div class="col-6"><strong>Tax Year:</strong> {{ selectedReturn.taxYear }}</div>
        <div class="col-6"><strong>Return Type:</strong> {{ selectedReturn.returnType }}</div>
        <div class="col-6"><strong>Status:</strong> <Tag :value="selectedReturn.status" :severity="getStatusSeverity(selectedReturn.status)" /></div>
        <div class="col-6"><strong>NTN:</strong> {{ selectedReturn.ntn || 'N/A' }}</div>
        <div class="col-6"><strong>CNIC:</strong> {{ selectedReturn.cnic || 'N/A' }}</div>
        <div class="col-12">
          <h3>Financial Details</h3>
          <Divider />
        </div>
        <div class="col-6"><strong>Gross Income:</strong> Rs. {{ formatCurrency(selectedReturn.grossIncome) }}</div>
        <div class="col-6"><strong>Taxable Income:</strong> Rs. {{ formatCurrency(selectedReturn.taxableIncome) }}</div>
        <div class="col-6"><strong>Tax Liability:</strong> Rs. {{ formatCurrency(selectedReturn.taxLiability) }}</div>
        <div class="col-6"><strong>Advance Tax Paid:</strong> Rs. {{ formatCurrency(selectedReturn.advanceTaxPaid) }}</div>
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

interface TaxReturn {
  id?: string;
  returnId: string;
  taxYear: string;
  returnType: string;
  ntn?: string;
  cnic?: string;
  grossIncome: number;
  taxableIncome: number;
  taxLiability: number;
  advanceTaxPaid: number;
  dueDate: string;
  filedDate?: string;
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
const taxReturn = ref<TaxReturn>({
  returnId: '',
  taxYear: '2024',
  returnType: 'income_tax',
  grossIncome: 0,
  taxableIncome: 0,
  taxLiability: 0,
  advanceTaxPaid: 0,
  dueDate: '',
  status: 'draft'
});

const stats = ref({
  filed: 12,
  pending: 3,
  overdue: 1,
  amendments: 2
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
    returnId: `TR${Date.now()}`,
    taxYear: '2024',
    returnType: 'income_tax',
    grossIncome: 0,
    taxableIncome: 0,
    taxLiability: 0,
    advanceTaxPaid: 0,
    dueDate: '2024-12-31',
    status: 'draft'
  };
  submitted.value = false;
  returnDialog.value = true;
};

const editReturn = (ret: TaxReturn) => {
  taxReturn.value = { ...ret };
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
  if (taxReturn.value.returnType && taxReturn.value.taxYear) {
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
  if (taxReturn.value.returnType && taxReturn.value.taxYear) {
    try {
      taxReturn.value.status = 'filed';
      taxReturn.value.filedDate = new Date().toISOString().split('T')[0];
      await saveReturnData();
      toast.add({ severity: 'success', summary: 'Success', detail: 'Return filed successfully', life: 3000 });
    } catch (error: any) {
      toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'Filing failed', life: 3000 });
    }
  }
};

const saveReturnData = async () => {
  if (taxReturn.value.id) {
    const index = taxReturns.value.findIndex(r => r.id === taxReturn.value.id);
    if (index !== -1) {
      taxReturns.value[index] = { ...taxReturn.value };
    }
  } else {
    const newReturn = { ...taxReturn.value, id: Date.now().toString() };
    taxReturns.value.push(newReturn);
  }
  returnDialog.value = false;
  updateStats();
};

const fileReturn = async (ret: TaxReturn) => {
  try {
    ret.status = 'filed';
    ret.filedDate = new Date().toISOString().split('T')[0];
    toast.add({ severity: 'success', summary: 'Success', detail: 'Return filed with FBR', life: 3000 });
    updateStats();
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Filing failed', life: 3000 });
  }
};

const downloadReturn = (ret: TaxReturn) => {
  toast.add({ severity: 'info', summary: 'Download', detail: `Downloading ${ret.returnId}.pdf`, life: 3000 });
};

const applyFilters = () => {
  loadTaxReturns();
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

const updateStats = () => {
  stats.value = {
    filed: taxReturns.value.filter(r => ['filed', 'accepted'].includes(r.status)).length,
    pending: taxReturns.value.filter(r => r.status === 'draft').length,
    overdue: taxReturns.value.filter(r => r.status === 'overdue').length,
    amendments: taxReturns.value.filter(r => r.status === 'amended').length
  };
};

const loadTaxReturns = async () => {
  loading.value = true;
  try {
    // Mock FBR Pakistan tax returns data
    taxReturns.value = [
      {
        id: '1',
        returnId: 'ITR-2024-001',
        taxYear: '2024',
        returnType: 'income_tax',
        ntn: '1234567-8',
        cnic: '12345-1234567-1',
        grossIncome: 2500000,
        taxableIncome: 2200000,
        taxLiability: 165000,
        advanceTaxPaid: 150000,
        dueDate: '2024-12-31',
        filedDate: '2024-11-15',
        status: 'filed',
        remarks: 'Regular income tax return for salaried individual'
      },
      {
        id: '2',
        returnId: 'STR-2024-002',
        taxYear: '2024',
        returnType: 'sales_tax',
        ntn: '1234567-8',
        grossIncome: 5000000,
        taxableIncome: 4500000,
        taxLiability: 810000,
        advanceTaxPaid: 800000,
        dueDate: '2024-11-15',
        status: 'draft',
        remarks: 'Monthly sales tax return'
      },
      {
        id: '3',
        returnId: 'WTR-2024-003',
        taxYear: '2024',
        returnType: 'withholding_tax',
        ntn: '1234567-8',
        grossIncome: 1200000,
        taxableIncome: 1200000,
        taxLiability: 120000,
        advanceTaxPaid: 120000,
        dueDate: '2024-10-15',
        filedDate: '2024-10-10',
        status: 'accepted',
        remarks: 'Withholding tax on contracts'
      },
      {
        id: '4',
        returnId: 'CTR-2023-004',
        taxYear: '2023',
        returnType: 'corporate_tax',
        ntn: '1234567-8',
        grossIncome: 15000000,
        taxableIncome: 12000000,
        taxLiability: 3480000,
        advanceTaxPaid: 3200000,
        dueDate: '2023-12-31',
        status: 'overdue',
        remarks: 'Corporate tax return - pending submission'
      }
    ];
    updateStats();
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load tax returns', life: 3000 });
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadTaxReturns();
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
