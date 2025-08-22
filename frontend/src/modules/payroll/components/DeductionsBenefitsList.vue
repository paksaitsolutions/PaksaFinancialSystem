<template>
  <div class="card">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2>Deductions & Benefits</h2>
      <Button
        label="Add New"
        icon="pi pi-plus"
        @click="showFormDialog = true"
      />
    </div>

    <DataTable
      :value="items"
      :loading="loading"
      :paginator="true"
      :rows="10"
      :rows-per-page-options="[5, 10, 25, 50]"
      paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
      current-page-report-template="Showing {first} to {last} of {totalRecords} entries"
      :global-filter-fields="['name', 'type', 'description']"
      responsive-layout="scroll"
      striped-rows
    >
      <template #header>
        <div class="flex justify-content-between">
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText
              v-model="filters['global'].value"
              placeholder="Search..."
            />
          </span>
          <div>
            <Button
              label="Export"
              icon="pi pi-download"
              class="p-button-text"
              @click="showExportDialog = true"
            />
          </div>
        </div>
      </template>

      <Column field="name" header="Name" :sortable="true">
        <template #body="{ data }">
          <span :class="{ 'font-bold': data.active, 'text-400': !data.active }">
            {{ data.name }}
          </span>
        </template>
      </Column>

      <Column field="type" header="Type" :sortable="true">
        <template #body="{ data }">
          <Tag
            :value="formatType(data.type)"
            :severity="getTypeSeverity(data.type)"
          />
        </template>
      </Column>

      <Column field="amount" header="Amount" :sortable="true">
        <template #body="{ data }">
          {{ formatAmount(data) }}
        </template>
      </Column>

      <Column field="taxable" header="Taxable" :sortable="true">
        <template #body="{ data }">
          <i
            class="pi"
            :class="data.taxable ? 'pi-check-circle text-green-500' : 'pi-times-circle text-red-500'"
          />
        </template>
      </Column>

      <Column field="active" header="Status" :sortable="true">
        <template #body="{ data }">
          <Tag
            :value="data.active ? 'Active' : 'Inactive'"
            :severity="data.active ? 'success' : 'danger'"
          />
        </template>
      </Column>

      <Column header="Actions" :exportable="false" style="min-width: 12rem">
        <template #body="{ data }">
          <div class="flex gap-2">
            <Button
              icon="pi pi-pencil"
              class="p-button-rounded p-button-text p-button-sm"
              @click="editItem(data)"
            />
            <Button
              icon="pi pi-trash"
              class="p-button-rounded p-button-text p-button-sm p-button-danger"
              @click="confirmDelete(data)"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <!-- Form Dialog -->
    <Dialog
      v-model:visible="showFormDialog"
      :header="editingItem ? 'Edit Item' : 'Add New Item'"
      :modal="true"
      :style="{ width: '600px' }"
    >
      <DeductionBenefitForm
        v-if="showFormDialog"
        :deduction="editingItem"
        :loading="formLoading"
        @submit="handleFormSubmit"
        @cancel="showFormDialog = false"
      />
    </Dialog>

    <!-- Delete Confirmation -->
    <ConfirmDeleteDialog
      v-model:show="showDeleteDialog"
      :item="itemToDelete"
      item-name="this item"
      @confirm="handleDelete"
    />

    <!-- Export Dialog -->
    <ReportExportDialog
      v-model:visible="showExportDialog"
      title="Export Deductions & Benefits"
      :formats="['pdf', 'excel', 'csv']"
      :include-filters="true"
      @export="handleExport"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, reactive } from 'vue';
import { FilterMatchMode } from 'primevue/api';
import { usePayrollStore } from '../store/payrollStore';
import { useToast } from 'primevue/usetoast';

// Components
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import DeductionBenefitForm from './DeductionBenefitForm.vue';
import ConfirmDeleteDialog from './dialogs/ConfirmDeleteDialog.vue';
import ReportExportDialog from '@/components/common/ReportExportDialog.vue';

export default defineComponent({
  name: 'DeductionsBenefitsList',
  components: {
    DataTable,
    Column,
    Button,
    InputText,
    Tag,
    Dialog,
    DeductionBenefitForm,
    ConfirmDeleteDialog,
    ReportExportDialog,
  },
  setup() {
    const payrollStore = usePayrollStore();
    const toast = useToast();

    // State
    const items = ref([]);
    const loading = ref(false);
    const formLoading = ref(false);
    const showFormDialog = ref(false);
    const showDeleteDialog = ref(false);
    const showExportDialog = ref(false);
    const editingItem = ref(null);
    const itemToDelete = ref(null);

    // Filters
    const filters = reactive({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    });

    // Fetch data
    const fetchData = async () => {
      try {
        loading.value = true;
        // TODO: Replace with actual API call
        // items.value = await payrollStore.fetchDeductionsAndBenefits();
        
        // Mock data for now
        items.value = [
          {
            id: 1,
            type: 'deduction',
            name: 'Health Insurance',
            description: 'Monthly health insurance premium',
            amount_type: 'fixed',
            amount: 200.0,
            taxable: false,
            active: true,
          },
          {
            id: 2,
            type: 'benefit',
            name: 'Retirement Match',
            description: 'Company 401k match',
            amount_type: 'percentage',
            amount: 5.0,
            taxable: false,
            active: true,
          },
          // Add more mock data as needed
        ];
      } catch (error) {
        console.error('Error fetching deductions/benefits:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load deductions and benefits',
          life: 3000,
        });
      } finally {
        loading.value = false;
      }
    };

    // Format type for display
    const formatType = (type: string): string => {
      const types = {
        deduction: 'Deduction',
        benefit: 'Benefit',
        garnishment: 'Garnishment',
        loan: 'Loan',
        other: 'Other',
      };
      return types[type] || type;
    };

    // Get severity for type tag
    const getTypeSeverity = (type: string): string => {
      const severities = {
        deduction: 'warning',
        benefit: 'success',
        garnishment: 'danger',
        loan: 'info',
        other: 'secondary',
      };
      return severities[type] || 'info';
    };

    // Format amount with currency or percentage
    const formatAmount = (item: any): string => {
      if (item.amount_type === 'percentage') {
        return `${item.amount}%`;
      }
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
      }).format(item.amount);
    };

    // Edit item
    const editItem = (item: any) => {
      editingItem.value = { ...item };
      showFormDialog.value = true;
    };

    // Confirm delete
    const confirmDelete = (item: any) => {
      itemToDelete.value = item;
      showDeleteDialog.value = true;
    };

    // Handle form submit
    const handleFormSubmit = async (formData: any) => {
      try {
        formLoading.value = true;
        
        if (editingItem.value) {
          // Update existing item
          // await payrollStore.updateDeductionOrBenefit(editingItem.value.id, formData);
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Item updated successfully',
            life: 3000,
          });
        } else {
          // Create new item
          // await payrollStore.createDeductionOrBenefit(formData);
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Item created successfully',
            life: 3000,
          });
        }
        
        showFormDialog.value = false;
        fetchData();
      } catch (error) {
        console.error('Error saving item:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to save item',
          life: 3000,
        });
      } finally {
        formLoading.value = false;
      }
    };

    // Handle delete
    const handleDelete = async () => {
      if (!itemToDelete.value) return;
      
      try {
        // await payrollStore.deleteDeductionOrBenefit(itemToDelete.value.id);
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Item deleted successfully',
          life: 3000,
        });
        fetchData();
      } catch (error) {
        console.error('Error deleting item:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete item',
          life: 3000,
        });
      } finally {
        showDeleteDialog.value = false;
        itemToDelete.value = null;
      }
    };

    // Handle export
    const handleExport = async (format: string, options: any = {}) => {
      try {
        // TODO: Implement export functionality
        console.log('Exporting to', format, 'with options', options);
        
        toast.add({
          severity: 'success',
          summary: 'Export Started',
          detail: `Your export to ${format.toUpperCase()} has started. You will be notified when it's ready.`,
          life: 3000,
        });
        
        showExportDialog.value = false;
      } catch (error) {
        console.error('Export error:', error);
        toast.add({
          severity: 'error',
          summary: 'Export Failed',
          detail: 'Failed to generate export. Please try again.',
          life: 3000,
        });
      }
    };

    // Initialize
    onMounted(() => {
      fetchData();
    });

    return {
      items,
      loading,
      formLoading,
      showFormDialog,
      showDeleteDialog,
      showExportDialog,
      editingItem,
      itemToDelete,
      filters,
      formatType,
      getTypeSeverity,
      formatAmount,
      editItem,
      confirmDelete,
      handleFormSubmit,
      handleDelete,
      handleExport,
    };
  },
});
</script>

<style scoped>
/* Add any custom styles here */
</style>
