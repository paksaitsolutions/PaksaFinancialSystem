<template>
  <div class="p-4">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Tax Exemptions</h1>
      <Button 
        v-if="hasPermission('create_tax_exemptions')"
        @click="showAddExemptionDialog = true"
      >
        <template #icon>
          <PlusIcon class="w-5 h-5 mr-2" />
        </template>
        Add Exemption
      </Button>
    </div>

    <Card>
      <template #content>
        <DataTable 
          :value="exemptions" 
          :loading="loading"
          :paginator="true" 
          :rows="10"
          :rowsPerPageOptions="[10, 20, 50]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Showing {first} to {last} of {totalRecords} exemptions"
          responsiveLayout="scroll"
        >
          <Column field="code" header="Code" :sortable="true">
            <template #body="{ data }">
              <span class="font-semibold">{{ data.code }}</span>
            </template>
          </Column>
          <Column field="name" header="Name" :sortable="true" />
          <Column field="description" header="Description" />
          <Column field="rate" header="Rate" :sortable="true">
            <template #body="{ data }">
              {{ formatPercentage(data.rate) }}
            </template>
          </Column>
          <Column field="effectiveDate" header="Effective Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.effectiveDate) }}
            </template>
          </Column>
          <Column field="expiryDate" header="Expiry Date" :sortable="true">
            <template #body="{ data }">
              {{ data.expiryDate ? formatDate(data.expiryDate) : 'N/A' }}
            </template>
          </Column>
          <Column header="Actions" :exportable="false" style="min-width: 12rem">
            <template #body="slotProps">
              <div class="flex space-x-2">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-rounded p-button-text p-button-sm"
                  v-tooltip.top="'Edit'"
                  @click="editExemption(slotProps.data)"
                  v-if="hasPermission('edit_tax_exemptions')"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-rounded p-button-text p-button-sm p-button-danger"
                  v-tooltip.top="'Delete'"
                  @click="confirmDelete(slotProps.data)"
                  v-if="hasPermission('delete_tax_exemptions')"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Add/Edit Exemption Dialog -->
    <Dialog 
      v-model:visible="showExemptionDialog" 
      :header="editingExemption ? 'Edit Tax Exemption' : 'Add New Tax Exemption'"
      :modal="true"
      :style="{ width: '600px' }"
    >
      <div class="grid grid-cols-1 gap-4">
        <div class="field">
          <label for="code">Code <span class="text-red-500">*</span></label>
          <InputText 
            id="code" 
            v-model="exemptionForm.code" 
            class="w-full" 
            :class="{ 'p-invalid': submitted && !exemptionForm.code }"
          />
          <small class="p-error" v-if="submitted && !exemptionForm.code">Code is required.</small>
        </div>
        
        <div class="field">
          <label for="name">Name <span class="text-red-500">*</span></label>
          <InputText 
            id="name" 
            v-model="exemptionForm.name" 
            class="w-full" 
            :class="{ 'p-invalid': submitted && !exemptionForm.name }"
          />
          <small class="p-error" v-if="submitted && !exemptionForm.name">Name is required.</small>
        </div>

        <div class="field">
          <label for="description">Description</label>
          <Textarea 
            id="description" 
            v-model="exemptionForm.description" 
            rows="3" 
            class="w-full" 
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="field">
            <label for="rate">Rate (%) <span class="text-red-500">*</span></label>
            <InputNumber 
              id="rate" 
              v-model="exemptionForm.rate" 
              mode="decimal" 
              :min="0" 
              :max="100" 
              :minFractionDigits="2"
              :maxFractionDigits="2"
              class="w-full"
              :class="{ 'p-invalid': submitted && exemptionForm.rate === null }"
            />
            <small class="p-error" v-if="submitted && exemptionForm.rate === null">Rate is required.</small>
          </div>

          <div class="field">
            <label for="effectiveDate">Effective Date <span class="text-red-500">*</span></label>
            <Calendar 
              id="effectiveDate" 
              v-model="exemptionForm.effectiveDate" 
              dateFormat="yy-mm-dd" 
              showIcon 
              class="w-full"
              :class="{ 'p-invalid': submitted && !exemptionForm.effectiveDate }"
            />
            <small class="p-error" v-if="submitted && !exemptionForm.effectiveDate">Effective date is required.</small>
          </div>
        </div>

        <div class="field">
          <label for="expiryDate">Expiry Date</label>
          <Calendar 
            id="expiryDate" 
            v-model="exemptionForm.expiryDate" 
            dateFormat="yy-mm-dd" 
            showIcon 
            class="w-full"
            :minDate="exemptionForm.effectiveDate"
          />
        </div>
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          @click="hideDialog" 
          class="p-button-text" 
        />
        <Button 
          :label="editingExemption ? 'Update' : 'Save'" 
          icon="pi pi-check" 
          @click="saveExemption" 
          :loading="saving"
          class="p-button-primary"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import { useAuthStore } from '@/stores/auth';
import { formatDate, formatPercentage } from '@/utils/formatters';
import { useTaxStore } from '@/stores/tax';

// UI Components
import Button from 'primevue/button';
import Card from 'primevue/card';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import InputNumber from 'primevue/inputnumber';
import Calendar from 'primevue/calendar';
import ConfirmDialog from 'primevue/confirmdialog';
import { PlusIcon } from '@heroicons/vue/24/outline';

// Types
interface TaxExemption {
  id?: string;
  code: string;
  name: string;
  description?: string;
  rate: number;
  effectiveDate: string | Date;
  expiryDate?: string | Date | null;
}

// State
const authStore = useAuthStore();
const taxStore = useTaxStore();
const confirm = useConfirm();
const toast = useToast();

const exemptions = ref<TaxExemption[]>([]);
const loading = ref(false);
const saving = ref(false);
const showExemptionDialog = ref(false);
const editingExemption = ref(false);
const submitted = ref(false);

const emptyExemption: TaxExemption = {
  code: '',
  name: '',
  description: '',
  rate: 0,
  effectiveDate: new Date(),
  expiryDate: null
};

const exemptionForm = ref<TaxExemption>({ ...emptyExemption });

// Methods
const hasPermission = (permission: string) => {
  return authStore.hasPermission(permission);
};

const fetchExemptions = async () => {
  try {
    loading.value = true;
    // TODO: Replace with actual API call
    // const response = await taxStore.fetchTaxExemptions();
    // exemptions.value = response.data;
    
    // Mock data for now
    exemptions.value = [
      {
        id: '1',
        code: 'ZERO',
        name: 'Zero Rated',
        description: 'Goods and services taxed at 0%',
        rate: 0,
        effectiveDate: '2025-01-01',
        expiryDate: null
      },
      {
        id: '2',
        code: 'EXEMPT',
        name: 'Exempt',
        description: 'Goods and services exempt from tax',
        rate: 0,
        effectiveDate: '2025-01-01',
        expiryDate: '2025-12-31'
      }
    ];
  } catch (error) {
    console.error('Error fetching tax exemptions:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load tax exemptions',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};

const openNew = () => {
  exemptionForm.value = { ...emptyExemption };
  submitted.value = false;
  editingExemption.value = false;
  showExemptionDialog.value = true;
};

const editExemption = (exemption: TaxExemption) => {
  exemptionForm.value = { ...exemption };
  editingExemption.value = true;
  showExemptionDialog.value = true;
};

const saveExemption = async () => {
  submitted.value = true;
  
  if (!exemptionForm.value.code || !exemptionForm.value.name || 
      exemptionForm.value.rate === null || !exemptionForm.value.effectiveDate) {
    return;
  }

  try {
    saving.value = true;
    
    // TODO: Replace with actual API call
    if (editingExemption.value) {
      // await taxStore.updateTaxExemption(exemptionForm.value);
      const index = exemptions.value.findIndex(e => e.id === exemptionForm.value.id);
      if (index !== -1) {
        exemptions.value[index] = { ...exemptionForm.value };
      }
    } else {
      // const response = await taxStore.createTaxExemption(exemptionForm.value);
      const newExemption = {
        ...exemptionForm.value,
        id: Math.random().toString(36).substr(2, 9) // Generate a random ID for demo
      };
      exemptions.value.push(newExemption);
    }
    
    showExemptionDialog.value = false;
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `Tax exemption ${editingExemption.value ? 'updated' : 'created'} successfully`,
      life: 3000
    });
  } catch (error) {
    console.error('Error saving tax exemption:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: `Failed to ${editingExemption.value ? 'update' : 'create'} tax exemption`,
      life: 3000
    });
  } finally {
    saving.value = false;
  }
};

const confirmDelete = (exemption: TaxExemption) => {
  confirm.require({
    message: `Are you sure you want to delete ${exemption.name}?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    accept: () => deleteExemption(exemption),
    reject: () => {}
  });
};

const deleteExemption = async (exemption: TaxExemption) => {
  try {
    // TODO: Replace with actual API call
    // await taxStore.deleteTaxExemption(exemption.id);
    exemptions.value = exemptions.value.filter(e => e.id !== exemption.id);
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Tax exemption deleted successfully',
      life: 3000
    });
  } catch (error) {
    console.error('Error deleting tax exemption:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete tax exemption',
      life: 3000
    });
  }
};

const hideDialog = () => {
  showExemptionDialog.value = false;
  submitted.value = false;
};

// Lifecycle hooks
onMounted(() => {
  fetchExemptions();
});
</script>

<style scoped>
.p-datatable .p-datatable-thead > tr > th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

:deep(.p-calendar) {
  width: 100%;
}
</style>
