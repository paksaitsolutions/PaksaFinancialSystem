<template>
  <div class="payrun-list-view">
    <div class="d-flex justify-space-between align-center mb-4">
      <h1>Pay Runs</h1>
      <v-btn
        color="primary"
        :to="{ name: 'payroll-payruns-create' }"
        prepend-icon="mdi-plus"
      >
        New Pay Run
      </v-btn>
    </div>

    <v-card class="mb-4">
      <v-card-text>
        <v-row>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="search"
              label="Search"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="comfortable"
              hide-details
              clearable
              @update:model-value="fetchPayRuns"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.status"
              :items="statusOptions"
              label="Status"
              variant="outlined"
              density="comfortable"
              hide-details
              clearable
              @update:model-value="fetchPayRuns"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-menu
              v-model="dateMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              min-width="auto"
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="dateRangeText"
                  label="Date Range"
                  prepend-inner-icon="mdi-calendar"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  readonly
                  v-bind="props"
                />
              </template>
              <v-date-picker
                v-model="dateRange"
                range
                @update:model-value="onDateRangeChange"
              />
            </v-menu>
          </v-col>
          <v-col cols="12" md="3" class="d-flex align-center">
            <v-btn
              color="secondary"
              variant="tonal"
              class="mr-2"
              @click="resetFilters"
            >
              Reset
            </v-btn>
            <v-btn
              color="primary"
              variant="elevated"
              @click="fetchPayRuns"
              :loading="loading"
            >
              Apply
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-card>
      <v-card-title class="d-flex align-center">
        <span class="text-h6">Pay Run History</span>
        <v-spacer />
        <v-btn
          icon
          variant="text"
          :loading="loading"
          @click="fetchPayRuns"
        >
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="payruns"
        :loading="loading"
        :items-per-page="pagination.itemsPerPage"
        :page="pagination.page"
        :items-length="pagination.totalItems"
        :server-items-length="pagination.totalItems"
        :items-per-page-options="[10, 25, 50, 100]"
        @update:options="onTableOptionsChange"
        class="elevation-1"
      >
        <template v-slot:item.payPeriod="{ item }">
          {{ formatDateRange(item.payPeriodStartDate, item.payPeriodEndDate) }}
        </template>
        
        <template v-slot:item.paymentDate="{ item }">
          {{ formatDate(item.paymentDate) }}
        </template>
        
        <template v-slot:item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            size="small"
            :text="formatStatus(item.status)"
            class="text-uppercase"
          />
        </template>
        
        <template v-slot:item.actions="{ item }">
          <div class="d-flex">
            <v-tooltip text="View Details" location="top">
              <template v-slot:activator="{ props }">
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  color="primary"
                  v-bind="props"
                  :to="{ name: 'payroll-payruns-view', params: { id: item.id } }"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </template>
            </v-tooltip>
            
            <v-tooltip text="Export" location="top">
              <template v-slot:activator="{ props }">
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  color="secondary"
                  v-bind="props"
                  @click="exportPayRun(item.id)"
                >
                  <v-icon>mdi-file-export</v-icon>
                </v-btn>
              </template>
            </v-tooltip>
          </div>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { format, parseISO } from 'date-fns';
import { payrollService } from '@/services/payroll/payrollService';
import type { PayRun, PayRunStatus } from '@/services/payroll/types';

export default defineComponent({
  name: 'PayRunListView',
  
  setup() {
    const router = useRouter();
    const loading = ref(false);
    const payruns = ref<PayRun[]>([]);
    const search = ref('');
    const dateMenu = ref(false);
    const dateRange = ref<[string, string] | null>(null);
    
    const filters = ref({
      status: null as PayRunStatus | null,
      startDate: null as string | null,
      endDate: null as string | null,
    });

    const pagination = ref({
      page: 1,
      itemsPerPage: 10,
      totalItems: 0,
      sortBy: ['payPeriodStartDate'],
      sortDesc: [true],
    });

    const statusOptions = [
      { title: 'Draft', value: 'draft' },
      { title: 'Processing', value: 'processing' },
      { title: 'Processed', value: 'processed' },
      { title: 'Paid', value: 'paid' },
      { title: 'Cancelled', value: 'cancelled' },
    ];

    const headers = [
      { title: 'Pay Period', key: 'payPeriod', sortable: false },
      { title: 'Payment Date', key: 'paymentDate', sortable: true },
      { title: 'Status', key: 'status', sortable: true },
      { title: 'Total Employees', key: 'employeeCount', sortable: true },
      { title: 'Total Amount', key: 'totalAmount', sortable: true },
      { title: 'Created By', key: 'createdBy', sortable: true },
      { title: 'Created At', key: 'createdAt', sortable: true },
      { title: 'Actions', key: 'actions', sortable: false, align: 'end' },
    ];

    const dateRangeText = computed(() => {
      if (!dateRange.value) return '';
      const [start, end] = dateRange.value;
      return `${formatDate(start)} - ${end ? formatDate(end) : ''}`;
    });

    const formatDate = (date: string | Date) => {
      if (!date) return '';
      return format(typeof date === 'string' ? parseISO(date) : date, 'MMM d, yyyy');
    };

    const formatDateRange = (startDate: string, endDate: string) => {
      if (!startDate || !endDate) return '';
      const start = format(parseISO(startDate), 'MMM d');
      const end = format(parseISO(endDate), 'MMM d, yyyy');
      return `${start} - ${end}`;
    };

    const formatStatus = (status: string) => {
      return status.charAt(0).toUpperCase() + status.slice(1);
    };

    const getStatusColor = (status: string) => {
      const colors: Record<string, string> = {
        draft: 'grey',
        processing: 'blue',
        processed: 'teal',
        paid: 'success',
        cancelled: 'error',
      };
      return colors[status] || 'grey';
    };

    const onDateRangeChange = (dates: any) => {
      if (dates && dates.length === 2) {
        dateRange.value = [dates[0], dates[1]];
        filters.value.startDate = dates[0];
        filters.value.endDate = dates[1];
      } else {
        dateRange.value = null;
        filters.value.startDate = null;
        filters.value.endDate = null;
      }
    };

    const resetFilters = () => {
      search.value = '';
      filters.value = {
        status: null,
        startDate: null,
        endDate: null,
      };
      dateRange.value = null;
      fetchPayRuns();
    };

    const onTableOptionsChange = (options: any) => {
      const { page, itemsPerPage, sortBy, sortDesc } = options;
      pagination.value = {
        page,
        itemsPerPage,
        totalItems: pagination.value.totalItems,
        sortBy,
        sortDesc,
      };
      fetchPayRuns();
    };

    const fetchPayRuns = async () => {
      try {
        loading.value = true;
        
        const params: Record<string, any> = {
          page: pagination.value.page,
          limit: pagination.value.itemsPerPage,
          search: search.value,
          ...filters.value,
        };

        // Remove null/undefined values
        Object.keys(params).forEach(key => {
          if (params[key] === null || params[key] === undefined || params[key] === '') {
            delete params[key];
          }
        });

        const response = await payrollService.getPayRuns(params);
        payruns.value = response.data;
        pagination.value.totalItems = response.meta?.total || 0;
      } catch (error) {
        console.error('Error fetching pay runs:', error);
        // Handle error (show notification)
      } finally {
        loading.value = false;
      }
    };

    const exportPayRun = async (payRunId: string) => {
      try {
        // TODO: Implement export functionality
        console.log('Exporting pay run:', payRunId);
        // const url = await payrollService.exportPayRun(payRunId);
        // window.open(url, '_blank');
      } catch (error) {
        console.error('Error exporting pay run:', error);
        // Handle error (show notification)
      }
    };

    onMounted(() => {
      fetchPayRuns();
    });

    return {
      // Refs
      loading,
      payruns,
      search,
      filters,
      dateMenu,
      dateRange,
      pagination,
      statusOptions,
      headers,
      // Computed
      dateRangeText,
      // Methods
      formatDate,
      formatDateRange,
      formatStatus,
      getStatusColor,
      onDateRangeChange,
      resetFilters,
      onTableOptionsChange,
      fetchPayRuns,
      exportPayRun,
    };
  },
});
</script>

<style scoped>
.payrun-list-view {
  padding: 20px;
}
</style>
