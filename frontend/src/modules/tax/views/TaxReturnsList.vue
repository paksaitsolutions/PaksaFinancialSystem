<template>
  <div class="tax-returns-list">
    <div class="flex justify-content-between align-items-center mb-4">
      <div class="text-2xl font-bold">Tax Returns</div>
      <Button 
        label="New Return" 
        icon="pi pi-plus" 
        @click="navigateToNewReturn"
      />
    </div>
    
    <Card>
      <template #content>
        <DataTable 
          :value="taxReturns" 
          :loading="isLoading"
          :paginator="true" 
          :rows="10"
          :rowsPerPageOptions="[10, 25, 50]"
          :globalFilterFields="['return_reference', 'tax_type', 'status']"
          stripedRows
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <template #header>
            <div class="flex justify-content-between">
              <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText 
                  v-model="filters.global.value" 
                  placeholder="Search returns..." 
                  class="w-20rem"
                />
              </span>
              <div class="flex gap-2">
                <Button 
                  icon="pi pi-filter" 
                  class="p-button-text"
                  @click="showFilters = !showFilters"
                  :label="showFilters ? 'Hide Filters' : 'Show Filters'"
                />
                <Button 
                  icon="pi pi-download" 
                  label="Export" 
                  class="p-button-outlined"
                  @click="exportToExcel"
                />
              </div>
            </div>
            
            <div v-if="showFilters" class="grid p-fluid mt-3">
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="status">Status</label>
                  <MultiSelect
                    id="status"
                    v-model="filters.status.value"
                    :options="statusOptions"
                    optionLabel="label"
                    optionValue="value"
                    display="chip"
                    placeholder="Select Status"
                  />
                </div>
              </div>
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="taxType">Tax Type</label>
                  <MultiSelect
                    id="taxType"
                    v-model="filters.tax_type.value"
                    :options="taxTypeOptions"
                    optionLabel="label"
                    optionValue="value"
                    display="chip"
                    placeholder="Select Tax Type"
                  />
                </div>
              </div>
              <div class="col-12 md:col-4">
                <div class="field">
                  <label for="dateRange">Date Range</label>
                  <Calendar
                    id="dateRange"
                    v-model="dateRange"
                    selectionMode="range"
                    :manualInput="false"
                    dateFormat="yy-mm-dd"
                    showIcon
                    showButtonBar
                    :showOnFocus="false"
                    placeholder="Select Date Range"
                  />
                </div>
              </div>
            </div>
          </template>
          
          <Column field="return_reference" header="Reference" sortable>
            <template #body="{ data }">
              <router-link 
                :to="{ name: 'TaxReturnDetail', params: { id: data.id } }"
                class="text-primary font-medium"
              >
                {{ data.return_reference }}
              </router-link>
            </template>
          </Column>
          
          <Column field="tax_type" header="Tax Type" sortable>
            <template #body="{ data }">
              {{ formatTaxType(data.tax_type) }}
            </template>
          </Column>
          
          <Column field="period_start" header="Period" sortable>
            <template #body="{ data }">
              {{ formatDateRange(data.period_start, data.period_end) }}
            </template>
          </Column>
          
          <Column field="filing_date" header="Filing Date" sortable>
            <template #body="{ data }">
              {{ data.filing_date ? formatDate(data.filing_date) : 'Not filed' }}
            </template>
          </Column>
          
          <Column field="due_date" header="Due Date" sortable>
            <template #body="{ data }">
              <div class="flex align-items-center">
                {{ formatDate(data.due_date) }}
                <i 
                  v-if="isDueSoon(data.due_date)" 
                  class="pi pi-exclamation-triangle text-yellow-500 ml-2"
                  v-tooltip.top="'Due soon'"
                ></i>
                <i 
                  v-else-if="isOverdue(data.due_date) && data.status !== 'paid'" 
                  class="pi pi-exclamation-circle text-red-500 ml-2"
                  v-tooltip.top="'Overdue'"
                ></i>
              </div>
            </template>
          </Column>
          
          <Column field="total_tax_due" header="Amount Due" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.total_tax_due) }}
            </template>
          </Column>
          
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          
          <Column headerStyle="width: 10rem; text-align: center" bodyStyle="text-align: center; overflow: visible">
            <template #body="{ data }">
              <div class="flex gap-2 justify-content-center">
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-rounded p-button-text p-button-sm"
                  @click="viewReturn(data.id)"
                  v-tooltip.top="'View Details'"
                />
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-rounded p-button-text p-button-sm"
                  @click="editReturn(data.id)"
                  v-tooltip.top="'Edit'"
                />
                <Button 
                  icon="pi pi-file-pdf" 
                  class="p-button-rounded p-button-text p-button-sm"
                  @click="exportToPdf(data.id)"
                  v-tooltip.top="'Export PDF'"
                />
                <Button 
                  v-if="data.status === 'draft'"
                  icon="pi pi-trash" 
                  class="p-button-rounded p-button-text p-button-sm p-button-danger"
                  @click="confirmDelete(data)"
                  v-tooltip.top="'Delete'"
                />
              </div>
            </template>
          </Column>
          
          <template #empty>
            <div class="text-center p-4">
              <i class="pi pi-search text-4xl text-400 mb-3"></i>
              <p class="text-600">No tax returns found</p>
              <Button 
                label="Create Your First Return" 
                icon="pi pi-plus" 
                class="mt-3"
                @click="navigateToNewReturn"
              />
            </div>
          </template>
        </DataTable>
      </template>
    </Card>
    
    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';
import { FilterMatchMode, FilterOperator } from 'primevue/api';
import { format, parseISO } from 'date-fns';
import { useTaxReturnStore } from '../store/tax-return';

export default defineComponent({
  name: 'TaxReturnsList',
  setup() {
    const router = useRouter();
    const confirm = useConfirm();
    const toast = useToast();
    const taxReturnStore = useTaxReturnStore();
    
    // State
    const isLoading = ref(false);
    const showFilters = ref(false);
    const dateRange = ref();
    
    // Mock data - replace with actual API calls
    const taxReturns = ref([
      {
        id: '1',
        return_reference: 'TRX-2023-001',
        tax_type: 'sales',
        period_start: '2023-01-01',
        period_end: '2023-01-31',
        filing_date: '2023-02-20',
        due_date: '2023-02-28',
        total_tax_due: 12500.75,
        status: 'filed',
        payment_status: 'paid'
      },
      {
        id: '2',
        return_reference: 'TRX-2023-002',
        tax_type: 'vat',
        period_start: '2023-02-01',
        period_end: '2023-02-28',
        filing_date: null,
        due_date: '2023-03-25',
        total_tax_due: 18750.00,
        status: 'draft',
        payment_status: 'unpaid'
      },
      {
        id: '3',
        return_reference: 'TRX-2022-012',
        tax_type: 'corporate',
        period_start: '2022-01-01',
        period_end: '2022-12-31',
        filing_date: '2023-03-15',
        due_date: '2023-04-15',
        total_tax_due: 125000.00,
        status: 'filed',
        payment_status: 'pending'
      },
      {
        id: '4',
        return_reference: 'TRX-2023-003',
        tax_type: 'withholding',
        period_start: '2023-03-01',
        period_end: '2023-03-31',
        filing_date: '2023-04-10',
        due_date: '2023-04-15',
        total_tax_due: 32500.25,
        status: 'filed',
        payment_status: 'paid'
      },
      {
        id: '5',
        return_reference: 'TRX-2023-004',
        tax_type: 'excise',
        period_start: '2023-03-01',
        period_end: '2023-03-31',
        due_date: '2023-04-20',
        total_tax_due: 8750.50,
        status: 'draft',
        payment_status: 'unpaid'
      }
    ]);
    
    // Filter options
    const statusOptions = [
      { label: 'Draft', value: 'draft' },
      { label: 'Filed', value: 'filed' },
      { label: 'Paid', value: 'paid' },
      { label: 'Overdue', value: 'overdue' },
      { label: 'Under Review', value: 'under_review' },
      { label: 'Amended', value: 'amended' }
    ];
    
    const taxTypeOptions = [
      { label: 'Sales Tax', value: 'sales' },
      { label: 'VAT', value: 'vat' },
      { label: 'Corporate Tax', value: 'corporate' },
      { label: 'Withholding Tax', value: 'withholding' },
      { label: 'Excise Tax', value: 'excise' },
      { label: 'Customs Duty', value: 'customs' },
      { label: 'Property Tax', value: 'property' },
      { label: 'Payroll Tax', value: 'payroll' }
    ];
    
    // Filters
    const filters = reactive({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS },
      status: { value: null, matchMode: FilterMatchMode.IN },
      tax_type: { value: null, matchMode: FilterMatchMode.IN },
      period_start: { value: null, matchMode: FilterMatchMode.DATE_AFTER_OR_EQUAL },
      period_end: { value: null, matchMode: FilterMatchMode.DATE_BEFORE_OR_EQUAL }
    });
    
    // Lifecycle hooks
    onMounted(async () => {
      await loadTaxReturns();
    });
    
    // Methods
    const loadTaxReturns = async () => {
      try {
        isLoading.value = true;
        // TODO: Replace with actual API call
        // taxReturns.value = await taxReturnStore.fetchTaxReturns();
      } catch (error) {
        console.error('Failed to load tax returns:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load tax returns',
          life: 5000
        });
      } finally {
        isLoading.value = false;
      }
    };
    
    const viewReturn = (id: string) => {
      router.push({ name: 'TaxReturnDetail', params: { id } });
    };
    
    const editReturn = (id: string) => {
      router.push({ name: 'EditTaxReturn', params: { id } });
    };
    
    const navigateToNewReturn = () => {
      router.push({ name: 'NewTaxReturn' });
    };
    
    const exportToPdf = (id: string) => {
      // TODO: Implement PDF export
      console.log('Exporting to PDF:', id);
      toast.add({
        severity: 'info',
        summary: 'Export',
        detail: 'Export to PDF will be implemented soon',
        life: 3000
      });
    };
    
    const exportToExcel = () => {
      // TODO: Implement Excel export
      console.log('Exporting to Excel');
      toast.add({
        severity: 'info',
        summary: 'Export',
        detail: 'Export to Excel will be implemented soon',
        life: 3000
      });
    };
    
    const confirmDelete = (taxReturn: any) => {
      confirm.require({
        message: `Are you sure you want to delete tax return ${taxReturn.return_reference}?`,
        header: 'Confirm Deletion',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: 'Delete',
        acceptClass: 'p-button-danger',
        accept: () => deleteReturn(taxReturn.id),
        reject: () => {}
      });
    };
    
    const deleteReturn = async (id: string) => {
      try {
        // TODO: Implement delete functionality
        // await taxReturnStore.deleteTaxReturn(id);
        
        // Remove from local state for now
        const index = taxReturns.value.findIndex(tr => tr.id === id);
        if (index !== -1) {
          taxReturns.value.splice(index, 1);
        }
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Tax return deleted successfully',
          life: 5000
        });
      } catch (error) {
        console.error('Failed to delete tax return:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete tax return',
          life: 5000
        });
      }
    };
    
    // Formatting helpers
    const formatDate = (dateString: string | null) => {
      if (!dateString) return 'N/A';
      return format(parseISO(dateString), 'MMM d, yyyy');
    };
    
    const formatDateRange = (startDate: string, endDate: string) => {
      return `${format(parseISO(startDate), 'MMM d')} - ${format(parseISO(endDate), 'MMM d, yyyy')}`;
    };
    
    const formatCurrency = (amount: number) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount);
    };
    
    const formatTaxType = (type: string) => {
      const typeMap: Record<string, string> = {
        'sales': 'Sales Tax',
        'vat': 'VAT',
        'corporate': 'Corporate Tax',
        'withholding': 'Withholding Tax',
        'excise': 'Excise Tax',
        'customs': 'Customs Duty',
        'property': 'Property Tax',
        'payroll': 'Payroll Tax'
      };
      return typeMap[type] || type;
    };
    
    const getStatusSeverity = (status: string) => {
      switch (status?.toLowerCase()) {
        case 'draft':
          return 'warning';
        case 'filed':
          return 'info';
        case 'paid':
          return 'success';
        case 'overdue':
          return 'danger';
        case 'under_review':
          return 'info';
        case 'amended':
          return 'help';
        default:
          return 'secondary';
      }
    };
    
    const isDueSoon = (dueDate: string) => {
      if (!dueDate) return false;
      const due = new Date(dueDate);
      const today = new Date();
      const diffTime = due.getTime() - today.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays > 0 && diffDays <= 7; // Due within 7 days
    };
    
    const isOverdue = (dueDate: string) => {
      if (!dueDate) return false;
      const due = new Date(dueDate);
      const today = new Date();
      return due < today;
    };
    
    return {
      // State
      taxReturns,
      isLoading,
      showFilters,
      dateRange,
      filters,
      
      // Options
      statusOptions,
      taxTypeOptions,
      
      // Methods
      viewReturn,
      editReturn,
      navigateToNewReturn,
      exportToPdf,
      exportToExcel,
      confirmDelete,
      formatDate,
      formatDateRange,
      formatCurrency,
      formatTaxType,
      getStatusSeverity,
      isDueSoon,
      isOverdue
    };
  }
});
</script>

<style scoped>
.tax-returns-list {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.p-datatable) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.p-datatable-wrapper) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.p-paginator) {
  margin-top: auto;
}
</style>
