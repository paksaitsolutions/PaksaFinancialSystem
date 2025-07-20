<template>
  <div class="deduction-benefit-list">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1>{{ $t('deductionBenefit.manageDeductionsBenefits') }}</h1>
      <div class="flex gap-2">
        <Button 
          :label="$t('common.export')" 
          icon="pi pi-download" 
          class="p-button-outlined"
          @click="showExportDialog = true"
        />
        <Button 
          :label="$t('deductionBenefit.addNew')" 
          icon="pi pi-plus" 
          @click="showCreateDialog = true"
        />
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="p-fluid grid">
        <div class="field col-12 md:col-4">
          <span class="p-float-label">
            <InputText 
              id="search" 
              v-model="filters.search" 
              @keyup.enter="applyFilters"
            />
            <label for="search">{{ $t('common.search') }}</label>
          </span>
        </div>
        <div class="field col-12 md:col-3">
          <span class="p-float-label">
            <Dropdown 
              id="type" 
              v-model="filters.type" 
              :options="typeOptions" 
              option-label="label" 
              option-value="value"
              :show-clear="true"
            />
            <label for="type">{{ $t('deductionBenefit.type') }}</label>
          </span>
        </div>
        <div class="field col-12 md:col-3">
          <div class="flex align-items-center mt-4">
            <Checkbox 
              id="activeOnly" 
              v-model="filters.activeOnly" 
              :binary="true" 
              class="mr-2"
            />
            <label for="activeOnly" class="ml-2">{{ $t('common.showActiveOnly') }}</label>
          </div>
        </div>
        <div class="field col-12 md:col-2 flex align-items-end">
          <Button 
            :label="$t('common.apply')" 
            class="p-button-outlined"
            @click="applyFilters"
          />
        </div>
      </div>
    </div>

    <!-- Data Table -->
    <div class="card">
      <DataTable 
        :value="items" 
        :loading="loading"
        :paginator="true" 
        :rows="pagination.rows"
        :total-records="totalItems"
        :rows-per-page-options="[10, 20, 50]"
        :current-page-report-template="$t('common.paginationTemplate')"
        @page="onPageChange($event)"
        striped-rows
      >
        <Column field="name" :header="$t('deductionBenefit.name')" sortable>
          <template #body="{ data }">
            <span class="font-medium">{{ data.name }}</span>
          </template>
        </Column>
        <Column field="type" :header="$t('deductionBenefit.type')" sortable>
          <template #body="{ data }">
            <Tag :value="getTypeLabel(data.type)" :severity="getTypeSeverity(data.type)" />
          </template>
        </Column>
        <Column field="amount" :header="$t('deductionBenefit.amount')" sortable>
          <template #body="{ data }">
            {{ formatAmount(data) }}
          </template>
        </Column>
        <Column field="taxable" :header="$t('deductionBenefit.taxable')" sortable>
          <template #body="{ data }">
            <i v-if="data.taxable" class="pi pi-check-circle text-green-500"></i>
            <i v-else class="pi pi-times-circle text-red-500"></i>
          </template>
        </Column>
        <Column field="active" :header="$t('common.status')" sortable>
          <template #body="{ data }">
            <Tag 
              :value="data.active ? $t('common.active') : $t('common.inactive')" 
              :severity="data.active ? 'success' : 'danger'" 
            />
          </template>
        </Column>
        <Column :header="$t('common.actions')" style="width: 15%">
          <template #body="{ data }">
            <div class="flex gap-2">
              <Button 
                icon="pi pi-pencil" 
                class="p-button-rounded p-button-text p-button-sm"
                @click="editItem(data)"
                v-tooltip.top="$t('common.edit')"
              />
              <Button 
                icon="pi pi-trash" 
                class="p-button-rounded p-button-text p-button-sm p-button-danger"
                @click="confirmDelete(data)"
                v-tooltip.top="$t('common.delete')"
              />
            </div>
          </template>
        </Column>
        <template #empty>
          <div class="text-center p-4">
            <p>{{ $t('common.noRecordsFound') }}</p>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- Create/Edit Dialog -->
    <Dialog 
      v-model:visible="showFormDialog" 
      :header="formTitle"
      :modal="true"
      :style="{ width: '600px' }"
      @hide="resetForm"
    >
      <DeductionBenefitForm
        v-if="showFormDialog"
        :initial-values="formData"
        :loading="formLoading"
        @submit="handleSubmit"
        @cancel="showFormDialog = false"
      />
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog />
    <confirm-dialog
      v-model:visible="showDeleteDialog"
      :header="$t('common.confirmDelete')"
      :message="$t('deductionBenefit.confirmDelete', { name: selectedItem?.name })"
      :loading="deleteLoading"
      @confirm="deleteItem"
      @cancel="showDeleteDialog = false"
    />

    <!-- Export Dialog -->
    <export-dialog
      v-model:visible="showExportDialog"
      :formats="exportFormats"
      :loading="exportLoading"
      @export="handleExport"
      @cancel="showExportDialog = false"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { useDeductionBenefitStore } from '../store/deductionBenefitStore';
import DeductionBenefitForm from '../components/DeductionBenefitForm.vue';
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue';
import ExportDialog from '@/components/shared/ExportDialog.vue';

export default defineComponent({
  name: 'DeductionBenefitListView',
  components: {
    DeductionBenefitForm,
    ConfirmDialog,
    ExportDialog
  },
  setup() {
    const { t } = useI18n();
    const confirm = useConfirm();
    const toast = useToast();
    const router = useRouter();
    const store = useDeductionBenefitStore();

    // State
    const showFormDialog = ref(false);
    const showDeleteDialog = ref(false);
    const showExportDialog = ref(false);
    const formLoading = ref(false);
    const deleteLoading = ref(false);
    const exportLoading = ref(false);
    const isEditing = ref(false);
    const selectedItem = ref<any>(null);

    // Filters
    const filters = ref({
      search: '',
      type: '',
      activeOnly: true
    });

    // Pagination
    const pagination = ref({
      page: 1,
      rows: 10,
      sortField: 'name',
      sortOrder: 1
    });

    // Computed
    const items = computed(() => store.state.items);
    const totalItems = computed(() => store.state.totalItems);
    const loading = computed(() => store.state.loading);
    
    const formTitle = computed(() => {
      return isEditing.value 
        ? t('deductionBenefit.editDeductionBenefit')
        : t('deductionBenefit.addDeductionBenefit');
    });

    const formData = computed(() => {
      return selectedItem.value || {
        type: '',
        name: '',
        description: '',
        amount_type: 'fixed',
        amount: 0,
        taxable: false,
        active: true
      };
    });

    const typeOptions = [
      { label: t('deductionBenefit.types.all'), value: '' },
      { label: t('deductionBenefit.types.deduction'), value: 'deduction' },
      { label: t('deductionBenefit.types.benefit'), value: 'benefit' },
      { label: t('deductionBenefit.types.garnishment'), value: 'garnishment' },
      { label: t('deductionBenefit.types.loan'), value: 'loan' },
      { label: t('deductionBenefit.types.other'), value: 'other' }
    ];

    const exportFormats = [
      { label: 'PDF', value: 'pdf', icon: 'pi pi-file-pdf' },
      { label: 'Excel', value: 'xlsx', icon: 'pi pi-file-excel' },
      { label: 'CSV', value: 'csv', icon: 'pi pi-file' }
    ];

    // Methods
    const fetchData = async () => {
      try {
        await store.fetchItems({
          page: pagination.value.page,
          limit: pagination.value.rows,
          search: filters.value.search,
          type: filters.value.type,
          active_only: filters.value.activeOnly
        });
      } catch (error) {
        console.error('Error fetching data:', error);
        toast.add({
          severity: 'error',
          summary: t('common.error'),
          detail: t('common.fetchError'),
          life: 5000
        });
      }
    };

    const applyFilters = () => {
      pagination.value.page = 1; // Reset to first page
      fetchData();
    };

    const onPageChange = (event: any) => {
      pagination.value.page = event.page + 1;
      pagination.value.rows = event.rows;
      fetchData();
    };

    const addNewItem = () => {
      isEditing.value = false;
      selectedItem.value = null;
      showFormDialog.value = true;
    };

    const editItem = (item: any) => {
      isEditing.value = true;
      selectedItem.value = { ...item };
      showFormDialog.value = true;
    };

    const handleSubmit = async (formData: any) => {
      formLoading.value = true;
      try {
        if (isEditing.value && selectedItem.value) {
          await store.updateItem(selectedItem.value.id, formData);
          toast.add({
            severity: 'success',
            summary: t('common.success'),
            detail: t('deductionBenefit.updateSuccess'),
            life: 5000
          });
        } else {
          await store.createItem(formData);
          toast.add({
            severity: 'success',
            summary: t('common.success'),
            detail: t('deductionBenefit.createSuccess'),
            life: 5000
          });
        }
        showFormDialog.value = false;
        fetchData();
      } catch (error) {
        console.error('Error saving item:', error);
        toast.add({
          severity: 'error',
          summary: t('common.error'),
          detail: t('common.saveError'),
          life: 5000
        });
      } finally {
        formLoading.value = false;
      }
    };

    const confirmDelete = (item: any) => {
      selectedItem.value = item;
      showDeleteDialog.value = true;
    };

    const deleteItem = async () => {
      if (!selectedItem.value) return;
      
      deleteLoading.value = true;
      try {
        await store.deleteItem(selectedItem.value.id);
        toast.add({
          severity: 'success',
          summary: t('common.success'),
          detail: t('deductionBenefit.deleteSuccess'),
          life: 5000
        });
        fetchData();
      } catch (error) {
        console.error('Error deleting item:', error);
        toast.add({
          severity: 'error',
          summary: t('common.error'),
          detail: t('common.deleteError'),
          life: 5000
        });
      } finally {
        deleteLoading.value = false;
        showDeleteDialog.value = false;
        selectedItem.value = null;
      }
    };

    const resetForm = () => {
      selectedItem.value = null;
    };

    const handleExport = async (format: string) => {
      exportLoading.value = true;
      try {
        const url = await store.exportItems({
          format,
          filters: {
            search: filters.value.search,
            type: filters.value.type,
            active_only: filters.value.activeOnly
          }
        });

        // Create a temporary link to trigger the download
        const link = document.createElement('a');
        link.href = url;
        link.download = `deductions-benefits-${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        toast.add({
          severity: 'success',
          summary: t('common.success'),
          detail: t('common.exportSuccess'),
          life: 5000
        });
      } catch (error) {
        console.error('Error exporting data:', error);
        toast.add({
          severity: 'error',
          summary: t('common.error'),
          detail: t('common.exportError'),
          life: 5000
        });
      } finally {
        exportLoading.value = false;
        showExportDialog.value = false;
      }
    };

    const getTypeLabel = (type: string) => {
      const option = typeOptions.find(opt => opt.value === type);
      return option ? option.label : type;
    };

    const getTypeSeverity = (type: string) => {
      switch (type) {
        case 'deduction': return 'warning';
        case 'benefit': return 'success';
        case 'garnishment': return 'danger';
        case 'loan': return 'info';
        default: return 'secondary';
      }
    };

    const formatAmount = (item: any) => {
      if (item.amount_type === 'percentage') {
        return `${item.amount}%`;
      }
      return new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency: 'USD' // TODO: Use user's currency preference
      }).format(item.amount);
    };

    // Lifecycle hooks
    onMounted(() => {
      fetchData();
    });

    return {
      // State
      showFormDialog,
      showDeleteDialog,
      showExportDialog,
      formLoading,
      deleteLoading,
      exportLoading,
      selectedItem,
      filters,
      pagination,
      items,
      totalItems,
      loading,
      formTitle,
      formData,
      typeOptions,
      exportFormats,
      
      // Methods
      applyFilters,
      onPageChange,
      addNewItem,
      editItem,
      handleSubmit,
      confirmDelete,
      deleteItem,
      resetForm,
      handleExport,
      getTypeLabel,
      getTypeSeverity,
      formatAmount
    };
  }
});
</script>

<style scoped>
.deduction-benefit-list {
  padding: 1.5rem;
}

:deep(.p-datatable) {
  .p-datatable-thead > tr > th {
    background-color: #f8f9fa;
    font-weight: 600;
  }
  
  .p-datatable-tbody > tr > td {
    vertical-align: middle;
  }
}
</style>
