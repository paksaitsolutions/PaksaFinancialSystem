<template>
  <div class="payroll-deductions-benefits">
    <!-- Page Header -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-3xl font-bold text-900 mb-1">{{ $t('payroll.deductionBenefit.title') }}</h1>
        <p class="text-600 m-0">{{ $t('payroll.deductionBenefit.subtitle') }}</p>
      </div>
      <div class="flex gap-2
      ">
        <Button 
          :label="$t('common.export')" 
          icon="pi pi-download" 
          class="p-button-outlined"
          @click="showExportDialog = true"
          :disabled="!deductionBenefits.length"
        />
        <Button 
          :label="$t('common.new')" 
          icon="pi pi-plus" 
          @click="openNew"
        />
      </div>
    </div>

    <!-- DataTable -->
    <Card>
      <template #content>
        <div class="flex justify-content-between align-items-center mb-4">
          <div class="flex gap-2">
            <Dropdown 
              v-model="filters.type" 
              :options="filterTypes" 
              option-label="label" 
              option-value="value"
              :placeholder="$t('common.allTypes')"
              class="w-10rem"
              @change="fetchDeductionBenefits"
            />
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText 
                v-model="filters.search" 
                :placeholder="$t('common.search') + '...'"
                @input="onSearchInput"
              />
            </span>
          </div>
          <div class="flex gap-2">
            <Button 
              icon="pi pi-filter-slash" 
              :label="$t('common.clear')"
              class="p-button-text"
              @click="clearFilters"
              :disabled="!hasActiveFilters"
            />
          </div>
        </div>

        <DataTable 
          :value="deductionBenefits" 
          :loading="loading"
          :paginator="true" 
          :rows="pagination.rows"
          :total-records="totalRecords"
          :first="pagination.first"
          :rows-per-page-options="[10, 20, 50]"
          paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          current-page-report-template="{first} - {last} of {totalRecords}"
          @page="onPageChange($event)"
          striped-rows
          responsive-layout="scroll"
          data-key="id"
          class="p-datatable-sm"
        >
          <Column field="type" :header="$t('payroll.deductionBenefit.type')" :sortable="true">
            <template #body="{ data }">
              <Tag 
                :value="getTypeLabel(data.type)" 
                :severity="data.type === 'deduction' ? 'danger' : 'success'" 
              />
            </template>
          </Column>
          <Column field="code" :header="$t('common.code')" :sortable="true" />
          <Column field="name" :header="$t('common.name')" :sortable="true" />
          <Column field="amountType" :header="$t('payroll.deductionBenefit.amountType')" :sortable="true">
            <template #body="{ data }">
              {{ getAmountTypeLabel(data.amountType) }}
            </template>
          </Column>
          <Column field="amount" :header="$t('payroll.deductionBenefit.amount')" :sortable="true">
            <template #body="{ data }">
              {{ formatAmount(data) }}
            </template>
          </Column>
          <Column field="isTaxable" :header="$t('payroll.deductionBenefit.taxable')" :sortable="true">
            <template #body="{ data }">
              <i 
                class="pi" 
                :class="data.isTaxable ? 'pi-check-circle text-green-500' : 'pi-times-circle text-red-500'"
              />
            </template>
          </Column>
          <Column field="status" :header="$t('common.status')" :sortable="true">
            <template #body="{ data }">
              <Tag 
                :value="data.isActive ? $t('common.active') : $t('common.inactive')" 
                :severity="data.isActive ? 'success' : 'danger'" 
              />
            </template>
          </Column>
          <Column field="effectiveDate" :header="$t('payroll.deductionBenefit.effectiveDate')" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.effectiveDate) }}
            </template>
          </Column>
          <Column :header="$t('common.actions')" style="width: 10rem">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-sm p-button-rounded"
                  @click="editDeductionBenefit(data)"
                  v-tooltip.top="$t('common.edit')"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-rounded p-button-danger"
                  @click="confirmDeleteDeductionBenefit(data)"
                  v-tooltip.top="$t('common.delete')"
                />
              </div>
            </template>
          </Column>
          <template #empty>
            <div class="text-center p-4">
              <i class="pi pi-search text-400 text-4xl mb-2" />
              <p class="text-600">{{ $t('common.noRecordsFound') }}</p>
              <Button 
                v-if="hasActiveFilters"
                :label="$t('common.clearFilters')" 
                class="p-button-text"
                @click="clearFilters"
              />
            </div>
          </template>
          <template #loading>
            <div class="text-center p-4">
              <i class="pi pi-spin pi-spinner text-4xl text-400" />
              <p class="text-600 mt-2">{{ $t('common.loading') }}...</p>
            </div>
          </template>
        </DataTable>
      </template>
    </Card>

    <!-- Deduction/Benefit Form Dialog -->
    <Dialog 
      v-model:visible="showFormDialog" 
      :header="formTitle"
      :modal="true" 
      :style="{ width: '50vw' }" 
      :closable="!submitting" 
      :close-on-escape="!submitting"
    >
      <DeductionBenefitForm
        v-if="showFormDialog"
        ref="deductionBenefitForm"
        :initial-data="currentDeductionBenefit"
        :is-edit="isEdit"
        :loading="submitting"
        :gl-accounts="glAccounts"
        @submit="saveDeductionBenefit"
        @cancel="showFormDialog = false"
      />
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog 
      v-model:visible="showDeleteDialog"
      :header="$t('common.confirmDelete')"
      :message="$t('payroll.deductionBenefit.confirmDelete', { name: currentDeductionBenefit?.name || '' })"
      :loading="deleting"
      @confirm="deleteDeductionBenefit"
      @update:visible="val => !val && (showDeleteDialog = false)"
    />

    <!-- Export Dialog -->
    <ExportDialog 
      v-model:visible="showExportDialog"
      :formats="exportFormats"
      :has-pagination="true"
      :total-pages="Math.ceil(totalRecords / pagination.rows)"
      @export="handleExport"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { useDeductionBenefitStore } from '../store/deductionBenefit';
import { storeToRefs } from 'pinia';
import { formatDate, formatCurrency } from '@/utils/formatters';
import DeductionBenefitForm from '../components/DeductionBenefitForm.vue';
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue';
import ExportDialog from '@/components/shared/ExportDialog.vue';

export default defineComponent({
  name: 'PayrollDeductionsBenefitsView',
  components: {
    DeductionBenefitForm,
    ConfirmDialog,
    ExportDialog
  },
  setup() {
    const { t } = useI18n();
    const toast = useToast();
    const router = useRouter();
    const deductionBenefitStore = useDeductionBenefitStore();
    const { 
      deductionBenefits, 
      loading, 
      totalRecords,
      glAccounts
    } = storeToRefs(deductionBenefitStore);

    // Refs
    const showFormDialog = ref(false);
    const showDeleteDialog = ref(false);
    const showExportDialog = ref(false);
    const isEdit = ref(false);
    const submitting = ref(false);
    const deleting = ref(false);
    const currentDeductionBenefit = ref<any>(null);
    const deductionBenefitForm = ref<any>(null);
    
    // Filters and pagination
    const filters = ref({
      type: null,
      search: '',
      status: null
    });

    const pagination = ref({
      first: 0,
      rows: 10,
      sortField: 'name',
      sortOrder: 1
    });

    // Computed
    const formTitle = computed(() => {
      return isEdit.value 
        ? t('payroll.deductionBenefit.editTitle')
        : t('payroll.deductionBenefit.newTitle');
    });

    const hasActiveFilters = computed(() => {
      return Object.values(filters.value).some(val => val !== null && val !== '');
    });

    const filterTypes = computed(() => [
      { label: t('common.allTypes'), value: null },
      { label: t('payroll.deductionBenefit.types.deduction'), value: 'deduction' },
      { label: t('payroll.deductionBenefit.types.benefit'), value: 'benefit' }
    ]);

    const exportFormats = computed(() => [
      { label: 'PDF', value: 'pdf', icon: 'pi pi-file-pdf' },
      { label: 'Excel', value: 'xlsx', icon: 'pi pi-file-excel' },
      { label: 'CSV', value: 'csv', icon: 'pi pi-file' }
    ]);

    // Methods
    const fetchDeductionBenefits = async () => {
      try {
        await deductionBenefitStore.fetchDeductionBenefits({
          ...pagination.value,
          ...filters.value,
          page: Math.floor(pagination.value.first / pagination.value.rows) + 1,
          limit: pagination.value.rows
        });
      } catch (error) {
        console.error('Error fetching deduction/benefit records:', error);
        toast.add({
          severity: 'error',
          summary: t('common.error'),
          detail: t('common.fetchError'),
          life: 5000
        });
      }
    };

    const fetchGLAccounts = async () => {
      try {
        await deductionBenefitStore.fetchGLAccounts();
      } catch (error) {
        console.error('Error fetching GL accounts:', error);
      }
    };

    const openNew = () => {
      currentDeductionBenefit.value = {};
      isEdit.value = false;
      showFormDialog.value = true;
    };

    const editDeductionBenefit = (item: any) => {
      currentDeductionBenefit.value = { ...item };
      isEdit.value = true;
      showFormDialog.value = true;
    };

    const confirmDeleteDeductionBenefit = (item: any) => {
      currentDeductionBenefit.value = { ...item };
      showDeleteDialog.value = true;
    };

    const saveDeductionBenefit = async (formData: any) => {
      try {
        submitting.value = true;
        
        if (isEdit.value) {
          await deductionBenefitStore.updateDeductionBenefit({
            id: currentDeductionBenefit.value.id,
            ...formData
          });
          toast.add({
            severity: 'success',
            summary: t('common.success'),
            detail: t('payroll.deductionBenefit.updateSuccess'),
            life: 5000
          });
        } else {
          await deductionBenefitStore.createDeductionBenefit(formData);
          toast.add({
            severity: 'success',
            summary: t('common.success'),
            detail: t('payroll.deductionBenefit.createSuccess'),
            life: 5000
          });
        }
        
        showFormDialog.value = false;
        fetchDeductionBenefits();
      } catch (error) {
        console.error('Error saving deduction/benefit:', error);
        toast.add({
          severity: 'error',
          summary: t('common.error'),
          detail: t('common.saveError'),
          life: 5000
        });
      } finally {
        submitting.value = false;
      }
    };

    const deleteDeductionBenefit = async () => {
      if (!currentDeductionBenefit.value) return;
      
      try {
        deleting.value = true;
        await deductionBenefitStore.deleteDeductionBenefit(currentDeductionBenefit.value.id);
        
        toast.add({
          severity: 'success',
          summary: t('common.success'),
          detail: t('payroll.deductionBenefit.deleteSuccess'),
          life: 5000
        });
        
        showDeleteDialog.value = false;
        fetchDeductionBenefits();
      } catch (error) {
        console.error('Error deleting deduction/benefit:', error);
        toast.add({
          severity: 'error',
          summary: t('common.error'),
          detail: t('common.deleteError'),
          life: 5000
        });
      } finally {
        deleting.value = false;
      }
    };

    const handleExport = async (options: any) => {
      try {
        const exportParams = {
          format: options.format,
          ...(options.scope === 'range' && {
            startPage: options.pageRange.start,
            endPage: options.pageRange.end
          }),
          ...(options.scope === 'current' && {
            startPage: Math.floor(pagination.value.first / pagination.value.rows) + 1,
            endPage: Math.ceil((pagination.value.first + pagination.value.rows) / pagination.value.rows)
          }),
          ...filters.value
        };

        const blob = await deductionBenefitStore.exportDeductionBenefits(exportParams);
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `deductions-benefits-${new Date().toISOString().split('T')[0]}.${options.format}`);
        document.body.appendChild(link);
        link.click();
        link.parentNode?.removeChild(link);
        
        toast.add({
          severity: 'success',
          summary: t('common.success'),
          detail: t('common.exportSuccess'),
          life: 5000
        });
        
        showExportDialog.value = false;
      } catch (error) {
        console.error('Error exporting data:', error);
        toast.add({
          severity: 'error',
          summary: t('common.error'),
          detail: t('common.exportError'),
          life: 5000
        });
      }
    };

    const onPageChange = (event: any) => {
      pagination.value.first = event.first;
      pagination.value.rows = event.rows;
      fetchDeductionBenefits();
    };

    const onSearchInput = debounce(() => {
      fetchDeductionBenefits();
    }, 500);

    const clearFilters = () => {
      filters.value = {
        type: null,
        search: '',
        status: null
      };
      fetchDeductionBenefits();
    };

    const getTypeLabel = (type: string) => {
      return type === 'deduction' 
        ? t('payroll.deductionBenefit.types.deduction')
        : t('payroll.deductionBenefit.types.benefit');
    };

    const getAmountTypeLabel = (type: string) => {
      return type === 'fixed'
        ? t('payroll.deductionBenefit.amountTypes.fixed')
        : t('payroll.deductionBenefit.amountTypes.percentage');
    };

    const formatAmount = (item: any) => {
      if (item.amountType === 'percentage') {
        return `${item.amount}%`;
      }
      return formatCurrency(item.amount, 'PKR');
    };

    // Debounce helper function
    const debounce = (fn: Function, delay: number) => {
      let timeoutId: ReturnType<typeof setTimeout>;
      return function(this: any, ...args: any[]) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
      };
    };

    // Lifecycle hooks
    onMounted(() => {
      fetchDeductionBenefits();
      fetchGLAccounts();
    });

    return {
      // Refs
      showFormDialog,
      showDeleteDialog,
      showExportDialog,
      isEdit,
      loading,
      submitting,
      deleting,
      currentDeductionBenefit,
      deductionBenefitForm,
      filters,
      pagination,
      deductionBenefits,
      totalRecords,
      glAccounts,
      
      // Computed
      formTitle,
      hasActiveFilters,
      filterTypes,
      exportFormats,
      
      // Methods
      openNew,
      editDeductionBenefit,
      confirmDeleteDeductionBenefit,
      saveDeductionBenefit,
      deleteDeductionBenefit,
      handleExport,
      onPageChange,
      onSearchInput,
      clearFilters,
      getTypeLabel,
      getAmountTypeLabel,
      formatAmount,
      formatDate,
      fetchDeductionBenefits
    };
  }
});
</script>

<style scoped>
.payroll-deductions-benefits {
  padding: 1.5rem;
}

/* Responsive adjustments */
@media screen and (max-width: 960px) {
  .payroll-deductions-benefits {
    padding: 1rem;
  }
  
  :deep(.p-datatable) {
    overflow-x: auto;
    display: block;
  }
}

/* Card styling */
:deep(.p-card) {
  box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.1), 0 1px 1px 0 rgba(0, 0, 0, 0.1), 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  border-radius: 6px;
}

/* Table styling */
:deep(.p-datatable) {
  .p-datatable-thead > tr > th {
    background-color: #f8f9fa;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
  }
  
  .p-datatable-tbody > tr {
    transition: background-color 0.2s;
    
    &:hover {
      background-color: #f8f9fa !important;
    }
  }
}

/* Action buttons */
:deep(.p-button.p-button-sm.p-button-rounded) {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .pi {
    font-size: 1rem;
  }
}
</style>
