<template>
  <v-container fluid class="pa-6">
    <!-- Page Header -->
    <v-row class="mb-6" align="center">
      <v-col cols="12" sm="6" md="8">
        <h1 class="text-h4 font-weight-bold">Pay Runs</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          View and manage all payroll runs
        </p>
      </v-col>
      <v-col cols="12" sm="6" md="4" class="text-right">
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          :to="{ name: 'payroll-run-create' }"
          :loading="isLoading"
        >
          New Pay Run
        </v-btn>
      </v-col>
    </v-row>

    <!-- Tax Summary Card -->
    <v-card class="mb-6">
      <v-card-title class="text-subtitle-1 font-weight-bold">
        Total Tax Summary
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <div class="text-subtitle-2">Total Tax Amount</div>
            <div class="text-h6 font-weight-bold">
              {{ formatCurrency(totalTaxAmount) }}
            </div>
          </v-col>
          <v-col cols="12" md="4">
            <div class="text-subtitle-2">Average Tax per Employee</div>
            <div class="text-h6 font-weight-bold">
              {{ formatCurrency(averageTaxPerEmployee) }}
            </div>
          </v-col>
          <v-col cols="12" md="4">
            <div class="text-subtitle-2">Total Exemptions</div>
            <div class="text-h6 font-weight-bold">
              {{ formatCurrency(totalExemptions) }}
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Filters Card -->
    <v-card class="mb-6">
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-filter</v-icon>
        <span>Filters</span>
        <v-spacer></v-spacer>
        <v-btn
          variant="text"
          size="small"
          @click="resetFilters"
          :disabled="!hasActiveFilters"
        >
          Reset Filters
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.status"
              :items="statusOptions"
              label="Status"
              clearable
              hide-details
              density="compact"
              variant="outlined"
            ></v-select>
          </v-col>
          <v-col cols="12" md="4">
            <v-menu
              v-model="dateMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              min-width="auto"
              offset-y
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-bind="props"
                  v-model="dateRangeText"
                  label="Date Range"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                  clearable
                  hide-details
                  variant="outlined"
                  density="compact"
                  @click:clear="clearDateRange"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="dateRange"
                range
                @update:modelValue="dateMenu = false"
              ></v-date-picker>
            </v-menu>
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="searchQuery"
              label="Search"
              prepend-inner-icon="mdi-magnify"
              clearable
              hide-details
              variant="outlined"
              density="compact"
              @keyup.enter="fetchPayRuns"
            ></v-text-field>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Pay Runs Table -->
    <v-card>
      <v-card-title class="d-flex align-center">
        <span>Pay Runs</span>
        <v-spacer></v-spacer>
        <v-btn
          icon
          @click="fetchPayRuns"
          :loading="isLoading"
          variant="text"
        >
          <v-icon>mdi-refresh</v-icon>
          <v-tooltip activator="parent" location="top">Refresh</v-tooltip>
        </v-btn>
        <v-menu>
          <template v-slot:activator="{ props: menuProps }">
            <v-btn
              variant="text"
              icon
              v-bind="menuProps"
              class="ml-2"
            >
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list density="compact">
            <v-list-item
              v-for="(action, i) in tableActions"
              :key="i"
              :value="action.title"
              @click="action.action"
            >
              <template v-slot:prepend>
                <v-icon :icon="action.icon"></v-icon>
              </template>
              <v-list-item-title>{{ action.title }}</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="payRuns"
          :loading="isLoading"
          :items-per-page="pagination.itemsPerPage"
          :page="pagination.page"
          :items-length="pagination.totalItems"
          :sort-by="pagination.sortBy"
          :sort-desc="pagination.sortDesc"
          :search="searchQuery"
          @update:options="onTableOptionsChange"
          class="elevation-1"
        >
          <template v-slot:item.status="{ item }">
            <v-chip
              :color="getStatusColor(item.raw.status)"
              size="small"
              label
            >
              {{ formatStatus(item.raw.status) }}
            </v-chip>
          </template>

          <template v-slot:item.payPeriod="{ item }">
            {{ formatDate(item.raw.payPeriodStart) }} - {{ formatDate(item.raw.payPeriodEnd) }}
          </template>

          <template v-slot:item.paymentDate="{ item }">
            {{ formatDate(item.raw.paymentDate) }}
          </template>

          <template v-slot:item.totalGross="{ item }">
            {{ formatCurrency(item.raw.totalGross) }}
          </template>

          <template v-slot:item.totalNet="{ item }">
            {{ formatCurrency(item.raw.totalNet) }}
          </template>

          <template v-slot:item.actions="{ item }">
            <div class="d-flex">
              <v-tooltip location="top">
                <template v-slot:activator="{ props: tooltipProps }">
                  <v-btn
                    v-bind="tooltipProps"
                    icon
                    size="small"
                    variant="text"
                    :to="{ name: 'payroll-run-detail', params: { id: item.raw.id } }"
                    class="mr-1"
                  >
                    <v-icon size="small">mdi-eye</v-icon>
                  </v-btn>
                </template>
                <span>View Details</span>
              </v-tooltip>

              <v-tooltip location="top" v-if="canProcessPayRun(item.raw)">
                <template v-slot:activator="{ props: tooltipProps }">
                  <v-btn
                    v-bind="tooltipProps"
                    icon
                    size="small"
                    variant="text"
                    :to="{ name: 'payroll-run-process', params: { id: item.raw.id } }"
                    class="mr-1"
                  >
                    <v-icon size="small" color="primary">mdi-cash-multiple</v-icon>
                  </v-btn>
                </template>
                <span>Process Pay Run</span>
              </v-tooltip>

              <v-tooltip location="top" v-if="canApprovePayRun(item.raw)">
                <template v-slot:activator="{ props: tooltipProps }">
                  <v-btn
                    v-bind="tooltipProps"
                    icon
                    size="small"
                    variant="text"
                    :to="{ name: 'payroll-run-approve', params: { id: item.raw.id } }"
                    class="mr-1"
                  >
                    <v-icon size="small" color="success">mdi-check-circle</v-icon>
                  </v-btn>
                </template>
                <span>Approve Pay Run</span>
              </v-tooltip>

              <v-menu>
                <template v-slot:activator="{ props: menuProps }">
                  <v-btn
                    variant="text"
                    icon
                    size="small"
                    v-bind="menuProps"
                  >
                    <v-icon size="small">mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
                <v-list density="compact">
                  <v-list-item
                    v-for="(action, i) in getRowActions(item.raw)"
                    :key="i"
                    :value="action.title"
                    @click="action.action(item.raw)"
                  >
                    <template v-slot:prepend>
                      <v-icon :icon="action.icon" :color="action.color"></v-icon>
                    </template>
                    <v-list-item-title>{{ action.title }}</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </div>
          </template>

          <template v-slot:no-data>
            <div class="py-6 text-center">
              <div v-if="isLoading">
                <v-progress-circular indeterminate color="primary"></v-progress-circular>
                <div class="mt-2">Loading pay runs...</div>
              </div>
              <div v-else>
                <v-icon size="48" class="mb-2">mdi-file-document-outline</v-icon>
                <div class="text-subtitle-1">No pay runs found</div>
                <div class="text-caption text-medium-emphasis">
                  Try adjusting your search or filter criteria
                </div>
                <v-btn
                  color="primary"
                  variant="text"
                  class="mt-2"
                  @click="resetFilters"
                >
                  Reset Filters
                </v-btn>
              </div>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6">Confirm Delete</v-card-title>
        <v-card-text>
          Are you sure you want to delete this pay run? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="secondary"
            variant="text"
            @click="deleteDialog = false"
            :disabled="isDeleting"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            @click="confirmDelete"
            :loading="isDeleting"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useTaxPolicyStore } from '@/modules/tax/store/policy';
import { taxCalculationService } from '@/services/tax/taxCalculationService';
import { usePayrollStore } from '@/stores/payroll';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatDate, formatCurrency } from '@/utils/formatters';

const router = useRouter();
const payrollStore = usePayrollStore();
const { showSuccess, showError } = useSnackbar();
const taxPolicyStore = useTaxPolicyStore();

// State
const isLoading = ref(false);
const payRuns = ref<PayRun[]>([]);
const error = ref<string | null>(null);
const filters = ref({
  status: null as string | null,
  period: null as string | null,
  dateRange: {
    start: null as string | null,
    end: null as string | null
  }
});

// Computed tax summaries
const totalTaxAmount = computed(() => {
  return payRuns.value.reduce((total, run) => total + (run.taxAmount || 0), 0);
});

const totalExemptions = computed(() => {
  return payRuns.value.reduce((total, run) => {
    return total + Object.values(run.exemptions || {}).reduce((sum, amount) => sum + amount, 0);
  }, 0);
});

const averageTaxPerEmployee = computed(() => {
  const totalEmployees = payRuns.value.reduce((total, run) => total + run.payslips.length, 0);
  return totalEmployees > 0 ? totalTaxAmount.value / totalEmployees : 0;
});

// Table headers
const headers = [
  { title: 'Pay Run ID', key: 'id', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Pay Period', key: 'payPeriod', sortable: true },
  { title: 'Payment Date', key: 'paymentDate', sortable: true },
  { title: 'Employees', key: 'employeeCount', align: 'end', sortable: true },
  { title: 'Total Gross', key: 'totalGross', align: 'end', sortable: true },
  { title: 'Total Net', key: 'totalNet', align: 'end', sortable: true },
  { title: 'Tax Amount', key: 'taxAmount', align: 'end', sortable: true },
  { title: 'Tax Breakdown', key: 'taxBreakdown', sortable: true },
  { title: 'Exemptions', key: 'exemptions', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

// Fetch pay runs
const fetchPayRuns = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    
    // Fetch tax policy first
    await taxPolicyStore.fetchPolicy();
    
    const params = {
      status: filters.value.status,
      period: filters.value.period,
      start_date: filters.value.dateRange.start,
      end_date: filters.value.dateRange.end
    };

    const response = await payrollService.getPayRuns(params);
    
    // Calculate tax details for each pay run if not present
    payRuns.value = response.map(run => {
      if (!run.taxAmount || !run.taxBreakdown) {
        const taxResult = taxCalculationService.calculatePayRunTax(run);
        return {
          ...run,
          taxAmount: taxResult.taxAmount,
          taxBreakdown: taxResult.taxBreakdown,
          exemptions: taxResult.exemptions
        };
      }
      return run;
    });
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to fetch pay runs';
    console.error('Error fetching pay runs:', err);
  } finally {
    isLoading.value = false;
  }
};

// Lifecycle hooks
onMounted(() => {
  fetchPayRuns();
});

// Watch for changes in filters
watch(
  [filters],
  () => {
    fetchPayRuns();
  },
  { deep: true }
);
    pagination.value.sortBy = options.sortBy;
    pagination.value.sortDesc = options.sortDesc;
  }
  
  fetchPayRuns();
}

function resetFilters() {
  filters.value = {
    status: '',
    startDate: '',
    endDate: '',
  };
  dateRange.value = [];
  searchQuery.value = '';
  pagination.value.page = 1;
  
  fetchPayRuns();
}

function clearDateRange() {
  dateRange.value = [];
  fetchPayRuns();
}

async function confirmDelete() {
  if (!selectedPayRun.value) return;
  
  try {
    isDeleting.value = true;
    await payrollStore.deletePayRun(selectedPayRun.value.id);
    showSuccess('Pay run deleted successfully');
    fetchPayRuns();
  } catch (error) {
    console.error('Error deleting pay run:', error);
    showError('Failed to delete pay run');
  } finally {
    deleteDialog.value = false;
    isDeleting.value = false;
    selectedPayRun.value = null;
  }
}

function exportToExcel() {
  // TODO: Implement Excel export
  showSuccess('Export to Excel will be implemented soon');
}

function exportToPdf() {
  // TODO: Implement PDF export
  showSuccess('Export to PDF will be implemented soon');
}

function printTable() {
  // TODO: Implement print functionality
  window.print();
}
</script>

<style scoped>
.v-table {
  --v-table-header-color: rgba(var(--v-theme-on-surface), var(--v-high-emphasis-opacity));
  --v-table-header-font-weight: 600;
}

.v-data-table-footer {
  border-top: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.v-data-table-header__content {
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}

.status-chip {
  font-weight: 500;
  text-transform: capitalize;
}

@media print {
  .no-print {
    display: none !important;
  }
  
  .v-data-table {
    width: 100% !important;
  }
  
  .v-data-table-footer {
    display: none !important;
  }
}
</style>
