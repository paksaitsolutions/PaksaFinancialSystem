<template>
  <div class="ap-payments">
    <!-- Header Section -->
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div class="header-text">
            <h1>
              <i class="pi pi-credit-card mr-2"></i>
              AP Payments
            </h1>
            <p class="text-600">Process and manage vendor payments efficiently</p>
          </div>
          <div class="header-actions">
            <Button 
              label="New Payment" 
              icon="pi pi-plus" 
              @click="handleNewPayment"
              class="mr-2"
            />
            <Button 
              label="Export" 
              icon="pi pi-download" 
              @click="exportPayments"
              :loading="isExporting"
              severity="secondary"
              outlined
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container">
      <!-- Summary Cards -->
      <div class="grid mb-4">
        <div 
          v-for="(summary, index) in summaryCards" 
          :key="index" 
          class="col-12 md:col-6 lg:col-3"
        >
          <Card class="h-full shadow-2">
            <template #title>{{ summary.title }}</template>
            <template #content>
              <div class="flex align-items-center justify-content-between">
                <div>
                  <div class="text-3xl font-bold mb-1">{{ summary.value }}</div>
                  <div 
                    class="text-sm flex align-items-center" 
                    :class="getTrendClass(summary.trend)"
                  >
                    <i :class="getTrendIcon(summary.trend)" class="mr-1"></i>
                    {{ Math.abs(summary.trend) }}% {{ summary.trendLabel || '' }}
                  </div>
                </div>
                <div 
                  class="flex align-items-center justify-content-center border-circle w-3rem h-3rem"
                  :class="summary.color"
                >
                  <i :class="summary.icon" class="text-white text-xl"></i>
                </div>
              </div>
            </template>
          </Card>
        </div>
      </div>

      <!-- Filters -->
      <Card class="mb-4">
        <template #title>
          <div class="flex align-items-center justify-content-between">
            <span>Filters</span>
            <Button 
              v-if="hasFilters"
              label="Clear Filters" 
              icon="pi pi-filter-slash" 
              @click="clearFilters"
              text
            />
          </div>
        </template>
        <template #content>
          <div class="grid">
            <div class="col-12 md:col-3">
              <span class="p-float-label">
                <Calendar 
                  v-model="filters.dateRange" 
                  selectionMode="range" 
                  :manualInput="false"
                  class="w-full"
                  inputId="date-range"
                />
                <label for="date-range">Date Range</label>
              </span>
            </div>
            <div class="col-12 md:col-3">
              <span class="p-float-label">
                <Dropdown 
                  v-model="filters.status" 
                  :options="statusOptions" 
                  optionLabel="label"
                  optionValue="value"
                  class="w-full"
                  inputId="status-filter"
                  :showClear="true"
                />
                <label for="status-filter">Status</label>
              </span>
            </div>
            <div class="col-12 md:col-3">
              <span class="p-float-label">
                <InputText 
                  v-model="filters.searchQuery" 
                  class="w-full" 
                  placeholder="Search by vendor, reference..."
                  id="search-query"
                />
                <label for="search-query">Search</label>
              </span>
            </div>
            <div class="col-12 md:col-3 flex align-items-end">
              <Button 
                label="Apply Filters" 
                icon="pi pi-filter" 
                class="w-full"
                @click="applyFilters"
                :disabled="!hasFilters"
              />
            </div>
          </div>
        </template>
      </Card>

      <!-- DataTable -->
      <Card>
        <template #title>Payment Transactions</template>
        <template #content>
          <DataTable 
            :value="filteredPayments" 
            :loading="loading"
            :paginator="true"
            :rows="10"
            :rowsPerPageOptions="[10, 25, 50]"
            paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
            currentPageReportTemplate="Showing {first} to {last} of {totalRecords} payments"
            responsiveLayout="scroll"
            :globalFilterFields="['vendor.name', 'reference', 'paymentMethod']"
            v-model:filters="filters"
          >
            <template #empty>No payments found.</template>
            <template #loading>Loading payments data. Please wait.</template>
            
            <Column field="id" header="ID" :sortable="true" style="width: 7rem" />
            
            <Column field="date" header="Date" :sortable="true" style="width: 10rem">
              <template #body="{ data }">
                {{ formatDate(data.date) }}
              </template>
            </Column>
            
            <Column field="vendor.name" header="Vendor" :sortable="true" style="width: 15rem" />
            
            <Column field="reference" header="Reference" :sortable="true" style="width: 12rem" />
            
            <Column field="amount" header="Amount" :sortable="true" style="width: 10rem">
              <template #body="{ data }">
                {{ formatCurrency(data.amount) }}
              </template>
            </Column>
            
            <Column field="status" header="Status" :sortable="true" style="width: 10rem">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            
            <Column field="paymentMethod" header="Method" :sortable="true" style="width: 10rem" />
            
            <Column header="Actions" style="width: 8rem">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button 
                    icon="pi pi-eye" 
                    class="p-button-rounded p-button-text" 
                    @click="viewPayment(data.id)"
                    v-tooltip.top="'View Details'"
                  />
                  <Button 
                    icon="pi pi-pencil" 
                    class="p-button-rounded p-button-text p-button-success" 
                    @click="editPayment(data.id)"
                    v-tooltip.top="'Edit'"
                  />
                  <Button 
                    icon="pi pi-trash" 
                    class="p-button-rounded p-button-text p-button-danger" 
                    @click="confirmDelete(data.id)"
                    v-tooltip.top="'Delete'"
                  />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>

    <!-- Export Dialog -->
    <ExportDialog 
      ref="exportDialog"
      :visible.sync="showExportDialog"
      :data="payments"
      :columns="exportColumns"
      title="Export Payments"
      @export="handleExport"
    />

    <!-- Delete Confirmation -->
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useAuthStore } from '@/stores/auth';

// Types
type PaymentStatus = 'pending' | 'approved' | 'paid' | 'cancelled' | 'failed';

type Payment = {
  id: string;
  date: string;
  vendor: { name: string };
  reference: string;
  amount: number;
  status: PaymentStatus;
  paymentMethod: string;
};

type SummaryCard = {
  title: string;
  value: string | number;
  icon: string;
  color: string;
  trend: number;
  trendLabel?: string;
};

type PaymentFilters = {
  vendor: string | null;
  dateRange: Date[] | null;
  status: PaymentStatus | null;
  amountRange: number[] | null;
  searchQuery: string;
};

// Composables
const router = useRouter();
const toast = useToast();
const confirm = useConfirm();
const authStore = useAuthStore();
const currentCompany = computed(() => authStore.currentCompany);

// State
const loading = ref<boolean>(true);
const isExporting = ref<boolean>(false);
const showExportDialog = ref<boolean>(false);
const filters = ref<PaymentFilters>({
  vendor: null,
  dateRange: null,
  status: null,
  amountRange: null,
  searchQuery: ''
});

// Status options for filter dropdown
const statusOptions = [
  { label: 'Pending', value: 'pending' },
  { label: 'Approved', value: 'approved' },
  { label: 'Paid', value: 'paid' },
  { label: 'Cancelled', value: 'cancelled' },
  { label: 'Failed', value: 'failed' }
];

// Computed
const hasFilters = computed<boolean>(() => {
  return (
    !!filters.value.vendor ||
    !!filters.value.status ||
    !!filters.value.searchQuery ||
    (filters.value.dateRange && filters.value.dateRange.length === 2) ||
    (filters.value.amountRange && filters.value.amountRange.length === 2)
  );
});

const payments = ref<Payment[]>([]);

const loadPayments = async () => {
  if (!currentCompany.value?.id) return;
  
  loading.value = true;
  try {
    // Replace with actual payment service call
    // const response = await paymentService.getPayments(currentCompany.value.id)
    // payments.value = response.data
    payments.value = []; // Placeholder until payment service is implemented
  } catch (error) {
    console.error('Error loading payments:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load payments',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

const filteredPayments = computed<Payment[]>(() => {
  if (!payments.value) return [];
  
  return payments.value.filter(payment => {
    // Filter by status
    if (filters.value.status && payment.status !== filters.value.status) {
      return false;
    }
    
    // Filter by date range
    if (filters.value.dateRange && filters.value.dateRange.length === 2) {
      const paymentDate = new Date(payment.date);
      const [start, end] = filters.value.dateRange;
      
      if (paymentDate < start || paymentDate > end) {
        return false;
      }
    }
    
    // Filter by search query
    if (filters.value.searchQuery) {
      const query = filters.value.searchQuery.toLowerCase();
      const vendorMatch = payment.vendor?.name?.toLowerCase().includes(query) || false;
      const refMatch = payment.reference?.toLowerCase().includes(query) || false;
      
      if (!vendorMatch && !refMatch) {
        return false;
      }
    }
    
    return true;
  });
});

// Summary cards data
const summaryCards = ref<SummaryCard[]>([
  { 
    title: 'Total Payments', 
    value: '$0.00', 
    icon: 'pi pi-credit-card', 
    color: 'bg-blue-500', 
    trend: 0,
    trendLabel: 'vs last period' 
  },
  { 
    title: 'This Month', 
    value: '$0.00', 
    icon: 'pi pi-calendar', 
    color: 'bg-green-500', 
    trend: 0,
    trendLabel: 'vs last month' 
  },
  { 
    title: 'Pending Approval', 
    value: '0', 
    icon: 'pi pi-clock', 
    color: 'bg-amber-500', 
    trend: 0,
    trendLabel: 'awaiting review' 
  },
  { 
    title: 'Overdue', 
    value: '0', 
    icon: 'pi pi-exclamation-triangle', 
    color: 'bg-red-500', 
    trend: 0,
    trendLabel: 'past due date' 
  }
]);

// Export columns configuration
const exportColumns = [
  { field: 'id', header: 'ID' },
  { field: 'vendor.name', header: 'Vendor' },
  { field: 'date', header: 'Date' },
  { field: 'amount', header: 'Amount', type: 'currency' },
  { field: 'status', header: 'Status' },
  { field: 'paymentMethod', header: 'Payment Method' },
  { field: 'reference', header: 'Reference' }
];

// Methods
const handleNewPayment = (): void => {
  router.push({ name: 'ap-payments-new' });
};

const viewPayment = (id: string): void => {
  router.push({ name: 'ap-payments-view', params: { id } });
};

const editPayment = (id: string): void => {
  router.push({ name: 'ap-payments-edit', params: { id } });
};

const confirmDelete = (id: string): void => {
  confirm.require({
    message: 'Are you sure you want to delete this payment?',
    header: 'Confirm Deletion',
    icon: 'pi pi-exclamation-triangle',
    accept: () => deletePayment(id),
    reject: () => {}
  });
};

const deletePayment = async (id: string): Promise<void> => {
  try {
    // await paymentService.deletePayment(id);
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Payment deleted successfully',
      life: 3000
    });
    await loadPayments();
  } catch (error) {
    console.error('Error deleting payment:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete payment',
      life: 5000
    });
  }
};

const exportPayments = (): void => {
  showExportDialog.value = true;
};

const handleExport = async (format: string): Promise<void> => {
  isExporting.value = true;
  try {
    // Implement export logic here
    console.log(`Exporting ${filteredPayments.value.length} payments as ${format}`);
    
    toast.add({
      severity: 'success',
      summary: 'Export Successful',
      detail: `Payments exported to ${format.toUpperCase()} successfully`,
      life: 3000
    });
  } catch (error) {
    console.error('Export error:', error);
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'An error occurred while exporting payments.',
      life: 5000
    });
  } finally {
    isExporting.value = false;
    showExportDialog.value = false;
  }
};

const applyFilters = (): void => {
  // The filteredPayments computed property will automatically update
  // when the filters change
  console.log('Filters applied:', filters.value);
};

const clearFilters = (): void => {
  filters.value = {
    vendor: null,
    dateRange: null,
    status: null,
    amountRange: null,
    searchQuery: ''
  };
};

// Utility methods
const formatDate = (dateString: string): string => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount || 0);
};

const getStatusSeverity = (status: PaymentStatus): string => {
  switch (status) {
    case 'pending':
      return 'warning';
    case 'approved':
      return 'info';
    case 'paid':
      return 'success';
    case 'cancelled':
      return 'danger';
    case 'failed':
      return 'danger';
    default:
      return 'info';
  }
};

const getTrendClass = (trend: number): string => {
  if (trend > 0) return 'text-green-500';
  if (trend < 0) return 'text-red-500';
  return 'text-500';
};

const getTrendIcon = (trend: number): string => {
  if (trend > 0) return 'pi pi-arrow-up';
  if (trend < 0) return 'pi pi-arrow-down';
  return 'pi pi-minus';
};

// Lifecycle hooks
onMounted(async (): Promise<void> => {
  await loadPayments();
});
</script>

<style scoped>
.ap-payments {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.page-header {
  background-color: var(--surface-card);
  border-bottom: 1px solid var(--surface-border);
  padding: 1.5rem 0;
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-text h1 {
  margin: 0;
  display: flex;
  align-items: center;
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-color);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Card styles */
:deep(.p-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.p-card-body) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.p-card-content) {
  flex: 1;
  padding: 0;
}

/* Responsive adjustments */
@media screen and (max-width: 960px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .header-actions .p-button {
    flex: 1;
    justify-content: center;
  }
}

/* Status badges */
:deep(.p-tag) {
  min-width: 100px;
  text-align: center;
  text-transform: capitalize;
}

/* Loading overlay */n:deep(.p-datatable-loading-overlay) {
  background-color: rgba(255, 255, 255, 0.7);
}

/* Filter form */
.p-float-label {
  margin-bottom: 1.5rem;
}

/* Action buttons */
.action-buttons {
  display: flex;
  gap: 0.5rem;
}

/* Responsive table */
@media screen and (max-width: 768px) {
  :deep(.p-datatable) {
    overflow-x: auto;
    display: block;
  }
}
</style>
