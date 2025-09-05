<template>
  <div class="tax-codes-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Tax Codes Management</h1>
        <p class="text-color-secondary">Manage tax codes and their configurations</p>
      </div>
      <Button label="Add Tax Code" icon="pi pi-plus" @click="openNew" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="taxCodes" :loading="loading" paginator :rows="10">
          <Column field="code" header="Code" sortable />
          <Column field="name" header="Name" sortable />
          <Column field="description" header="Description" sortable />
          <Column field="rate" header="Rate (%)" sortable>
            <template #body="{ data }">
              {{ data.rate }}%
            </template>
          </Column>
          <Column field="type" header="Type" sortable>
            <template #body="{ data }">
              <Tag :value="data.type" :severity="getTypeSeverity(data.type)" />
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editTaxCode(data)" />
              <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="confirmDeleteTaxCode(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="taxCodeDialog" header="Tax Code Details" :modal="true" :style="{width: '500px'}">
      <div class="field">
        <label>Code</label>
        <InputText v-model="taxCode.code" class="w-full" :class="{'p-invalid': submitted && !taxCode.code}" />
        <small class="p-error" v-if="submitted && !taxCode.code">Code is required.</small>
      </div>
      <div class="field">
        <label>Name</label>
        <InputText v-model="taxCode.name" class="w-full" :class="{'p-invalid': submitted && !taxCode.name}" />
        <small class="p-error" v-if="submitted && !taxCode.name">Name is required.</small>
      </div>
      <div class="field">
        <label>Description</label>
        <Textarea v-model="taxCode.description" class="w-full" rows="3" />
      </div>
      <div class="field">
        <label>Rate (%)</label>
        <InputNumber v-model="taxCode.rate" class="w-full" :min="0" :max="100" :maxFractionDigits="2" />
      </div>
      <div class="field">
        <label>Type</label>
        <Dropdown v-model="taxCode.type" :options="taxTypes" optionLabel="label" optionValue="value" class="w-full" />
      </div>
      <div class="field">
        <label>Status</label>
        <Dropdown v-model="taxCode.status" :options="statuses" optionLabel="label" optionValue="value" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="hideDialog" />
        <Button label="Save" @click="saveTaxCode" />
      </template>
    </Dialog>

    <Dialog v-model:visible="deleteTaxCodeDialog" header="Confirm" :modal="true" :style="{width: '450px'}">
      <div class="flex align-items-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="taxCode">Are you sure you want to delete tax code <b>{{ taxCode.code }}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" class="p-button-text" @click="deleteTaxCodeDialog = false" />
        <Button label="Yes" class="p-button-danger" @click="deleteTaxCode" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface TaxCode {
  id?: string;
  code: string;
  name: string;
  description: string;
  rate: number;
  type: string;
  status: string;
}

const toast = useToast();
const loading = ref(false);
const taxCodeDialog = ref(false);
const deleteTaxCodeDialog = ref(false);
const submitted = ref(false);

const taxCodes = ref<TaxCode[]>([]);
const taxCode = ref<TaxCode>({
  code: '',
  name: '',
  description: '',
  rate: 0,
  type: 'sales',
  status: 'active'
});

const taxTypes = ref([
  { label: 'Sales Tax', value: 'sales' },
  { label: 'VAT', value: 'vat' },
  { label: 'GST', value: 'gst' },
  { label: 'Excise Tax', value: 'excise' },
  { label: 'Import Duty', value: 'import' },
  { label: 'Other', value: 'other' }
]);

const statuses = ref([
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'Suspended', value: 'suspended' }
]);

const openNew = () => {
  taxCode.value = {
    code: '',
    name: '',
    description: '',
    rate: 0,
    type: 'sales',
    status: 'active'
  };
  submitted.value = false;
  taxCodeDialog.value = true;
};

const editTaxCode = (code: TaxCode) => {
  taxCode.value = { ...code };
  taxCodeDialog.value = true;
};

const hideDialog = () => {
  taxCodeDialog.value = false;
  submitted.value = false;
};

const saveTaxCode = async () => {
  submitted.value = true;
  if (taxCode.value.code && taxCode.value.name) {
    try {
      if (taxCode.value.id) {
        // Update existing
        const index = taxCodes.value.findIndex(c => c.id === taxCode.value.id);
        if (index !== -1) {
          taxCodes.value[index] = { ...taxCode.value };
        }
        toast.add({ severity: 'success', summary: 'Success', detail: 'Tax code updated', life: 3000 });
      } else {
        // Create new
        const newCode = { ...taxCode.value, id: Date.now().toString() };
        taxCodes.value.push(newCode);
        toast.add({ severity: 'success', summary: 'Success', detail: 'Tax code created', life: 3000 });
      }
      taxCodeDialog.value = false;
    } catch (error: any) {
      toast.add({ severity: 'error', summary: 'Error', detail: error.message || 'Operation failed', life: 3000 });
    }
  }
};

const confirmDeleteTaxCode = (code: TaxCode) => {
  taxCode.value = { ...code };
  deleteTaxCodeDialog.value = true;
};

const deleteTaxCode = async () => {
  try {
    taxCodes.value = taxCodes.value.filter(c => c.id !== taxCode.value.id);
    deleteTaxCodeDialog.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Tax code deleted', life: 3000 });
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Delete failed', life: 3000 });
  }
};

const getTypeSeverity = (type: string) => {
  switch (type) {
    case 'sales': return 'success';
    case 'vat': return 'info';
    case 'gst': return 'warning';
    default: return 'secondary';
  }
};

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'active': return 'success';
    case 'inactive': return 'danger';
    case 'suspended': return 'warning';
    default: return 'info';
  }
};

const loadTaxCodes = async () => {
  loading.value = true;
  try {
    // Mock data for demo
    taxCodes.value = [
      { id: '1', code: 'VAT-STD', name: 'Standard VAT', description: 'Standard VAT rate', rate: 20, type: 'vat', status: 'active' },
      { id: '2', code: 'VAT-RED', name: 'Reduced VAT', description: 'Reduced VAT rate', rate: 5, type: 'vat', status: 'active' },
      { id: '3', code: 'GST-STD', name: 'Standard GST', description: 'Standard GST rate', rate: 18, type: 'gst', status: 'active' },
      { id: '4', code: 'SALES-LOC', name: 'Local Sales Tax', description: 'Local sales tax', rate: 8.5, type: 'sales', status: 'active' },
      { id: '5', code: 'EXC-ALC', name: 'Alcohol Excise', description: 'Excise tax on alcohol', rate: 15, type: 'excise', status: 'suspended' }
    ];
  } catch (error: any) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load tax codes', life: 3000 });
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadTaxCodes();
});
</script>

<style scoped>
.tax-codes-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>
