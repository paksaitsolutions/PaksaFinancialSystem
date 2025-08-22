<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Employee Payslips</span>
            <v-btn
              color="primary"
              prepend-icon="mdi-download"
              @click="exportPayslips"
              :loading="exporting"
            >
              Export
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-row class="mb-4">
              <v-col cols="12" sm="6" md="3">
                <v-select
                  v-model="filters.status"
                  :items="statusOptions"
                  label="Status"
                  variant="outlined"
                  density="compact"
                  clearable
                  hide-details
                ></v-select>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-select
                  v-model="filters.department"
                  :items="departments"
                  label="Department"
                  variant="outlined"
                  density="compact"
                  clearable
                  hide-details
                ></v-select>
              </v-col>
              
              <v-col cols="12" sm="6" md="3">
                <v-menu
                  v-model="dateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="dateRangeText"
                      label="Pay Period"
                      prepend-inner-icon="mdi-calendar"
                      variant="outlined"
                      density="compact"
                      readonly
                      v-bind="props"
                      hide-details
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="dateRange"
                    range
                    @update:model-value="updateDateRange"
                  ></v-date-picker>
                </v-menu>
              </v-col>
              
              <v-col cols="12" sm="6" md="3" class="d-flex align-center">
                <v-btn
                  color="secondary"
                  variant="tonal"
                  class="me-2"
                  @click="resetFilters"
                >
                  Reset
                </v-btn>
                <v-btn
                  color="primary"
                  @click="applyFilters"
                  :loading="loading"
                >
                  Apply
                </v-btn>
              </v-col>
            </v-row>
            
            <v-data-table
              :headers="headers"
              :items="payslips"
              :loading="loading"
              :items-per-page="10"
              :page.sync="currentPage"
              :items-per-page-options="[10, 25, 50]"
              class="elevation-1"
              density="comfortable"
              show-current-page
            >
              <template v-slot:item.employee="{ item }">
                <div class="d-flex align-center">
                  <v-avatar size="36" color="primary" class="me-3">
                    <span class="text-white">{{ getInitials(item.employee_name) }}</span>
                  </v-avatar>
                  <div>
                    <div class="font-weight-medium">{{ item.employee_name }}</div>
                    <div class="text-caption text-medium-emphasis">{{ item.employee_id }}</div>
                  </div>
                </div>
              </template>
              
              <template v-slot:item.pay_period="{ item }">
                {{ formatDateRange(item.start_date, item.end_date) }}
              </template>
              
              <template v-slot:item.payment_date="{ item }">
                {{ formatDate(item.payment_date) }}
              </template>
              
              <template v-slot:item.net_pay="{ item }">
                <span class="font-weight-medium">{{ formatCurrency(item.net_pay) }}</span>
              </template>
              
              <template v-slot:item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  size="small"
                  class="text-capitalize"
                >
                  {{ item.status }}
                </v-chip>
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  @click="viewPayslip(item)"
                >
                  <v-icon>mdi-eye-outline</v-icon>
                  <v-tooltip activator="parent" location="top">View Payslip</v-tooltip>
                </v-btn>
                
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  @click="downloadPayslip(item)"
                  :loading="downloadingId === item.id"
                >
                  <v-icon>mdi-download</v-icon>
                  <v-tooltip activator="parent" location="top">Download PDF</v-tooltip>
                </v-btn>
              </template>
              
              <template v-slot:no-data>
                <div class="py-4 text-center">
                  No payslips found matching your criteria
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Export Dialog -->
    <v-dialog v-model="exportDialog" max-width="500">
      <v-card>
        <v-card-title>Export Payslips</v-card-title>
        <v-card-text>
          <v-radio-group v-model="exportFormat" column>
            <v-radio
              v-for="format in exportFormats"
              :key="format.value"
              :label="format.label"
              :value="format.value"
            ></v-radio>
          </v-radio-group>
          
          <v-checkbox
            v-model="includeAllColumns"
            label="Include all columns"
            hide-details
            class="mt-2"
          ></v-checkbox>
          
          <v-text-field
            v-if="exportFormat === 'csv'"
            v-model="delimiter"
            label="Delimiter"
            class="mt-4"
            hide-details
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="secondary"
            variant="text"
            @click="exportDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            @click="confirmExport"
            :loading="exporting"
          >
            Export
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'PayslipsView',
  
  setup() {
    const router = useRouter();
    
    const loading = ref(false);
    const exporting = ref(false);
    const downloadingId = ref<string | null>(null);
    const exportDialog = ref(false);
    const dateMenu = ref(false);
    const currentPage = ref(1);
    
    // Filters
    const filters = ref({
      status: null as string | null,
      department: null as string | null,
      start_date: null as string | null,
      end_date: null as string | null,
    });
    
    // Date range picker
    const dateRange = ref([
      new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().substr(0, 10),
      new Date().toISOString().substr(0, 10)
    ]);
    
    const dateRangeText = computed(() => {
      const start = dateRange.value[0] ? formatDate(dateRange.value[0]) : '';
      const end = dateRange.value[1] ? formatDate(dateRange.value[1]) : '';
      return start && end ? `${start} - ${end}` : 'Select date range';
    });
    
    // Export options
    const exportFormat = ref('pdf');
    const includeAllColumns = ref(true);
    const delimiter = ref(',');
    
    const exportFormats = [
      { label: 'PDF (Portable Document Format)', value: 'pdf' },
      { label: 'Excel (XLSX)', value: 'xlsx' },
      { label: 'CSV (Comma Separated Values)', value: 'csv' },
    ];
    
    // Mock data - replace with API calls
    const statusOptions = ['paid', 'pending', 'cancelled', 'processing'];
    const departments = ['Sales', 'Marketing', 'Engineering', 'HR', 'Finance', 'Operations'];
    
    const payslips = ref<any[]>([]);
    
    const headers = [
      { title: 'Employee', key: 'employee', sortable: true },
      { title: 'Employee ID', key: 'employee_id', sortable: true },
      { title: 'Pay Period', key: 'pay_period', sortable: true },
      { title: 'Payment Date', key: 'payment_date', sortable: true },
      { title: 'Gross Pay', key: 'gross_pay', align: 'end', sortable: true },
      { title: 'Deductions', key: 'deductions', align: 'end', sortable: true },
      { title: 'Net Pay', key: 'net_pay', align: 'end', sortable: true },
      { title: 'Status', key: 'status', sortable: true, align: 'center' },
      { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
    ];
    
    // Format currency
    const formatCurrency = (value: number) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
    };
    
    // Format date
    const formatDate = (date: string | Date) => {
      if (!date) return 'N/A';
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    };
    
    // Format date range
    const formatDateRange = (start: string, end: string) => {
      const startDate = new Date(start);
      const endDate = new Date(end);
      
      if (startDate.getMonth() === endDate.getMonth()) {
        return `${startDate.getDate()} - ${endDate.getDate()} ${startDate.toLocaleString('default', { month: 'short' })} ${startDate.getFullYear()}`;
      } else {
        return `${startDate.getDate()} ${startDate.toLocaleString('default', { month: 'short' })} - ${endDate.getDate()} ${endDate.toLocaleString('default', { month: 'short' })} ${startDate.getFullYear()}`;
      }
    };
    
    // Get status color
    const getStatusColor = (status: string) => {
      const statusMap: Record<string, string> = {
        paid: 'success',
        pending: 'warning',
        processing: 'info',
        cancelled: 'error',
        draft: 'grey',
      };
      return statusMap[status.toLowerCase()] || 'grey';
    };
    
    // Get initials from name
    const getInitials = (name: string) => {
      if (!name) return '??';
      return name
        .split(' ')
        .map(part => part[0])
        .join('')
        .toUpperCase()
        .substring(0, 2);
    };
    
    // Update date range filter
    const updateDateRange = (dates: string[]) => {
      if (dates.length === 2) {
        dateRange.value = dates;
        dateMenu.value = false;
      }
    };
    
    // Apply filters
    const applyFilters = () => {
      loading.value = true;
      
      // In a real app, this would be an API call with the filters
      setTimeout(() => {
        // Mock data - replace with actual API call
        payslips.value = Array.from({ length: 25 }, (_, i) => ({
          id: `PS-${1000 + i}`,
          employee_id: `EMP-${1000 + i}`,
          employee_name: `Employee ${i + 1}`,
          department: departments[i % departments.length],
          start_date: new Date(Date.now() - Math.floor(Math.random() * 90) * 24 * 60 * 60 * 1000).toISOString(),
          end_date: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
          payment_date: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
          gross_pay: 3000 + Math.floor(Math.random() * 5000),
          deductions: 500 + Math.floor(Math.random() * 1000),
          net_pay: 2500 + Math.floor(Math.random() * 4000),
          status: statusOptions[Math.floor(Math.random() * statusOptions.length)],
        }));
        
        loading.value = false;
      }, 800);
    };
    
    // Reset filters
    const resetFilters = () => {
      filters.value = {
        status: null,
        department: null,
        start_date: null,
        end_date: null,
      };
      
      dateRange.value = [
        new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().substr(0, 10),
        new Date().toISOString().substr(0, 10)
      ];
      
      applyFilters();
    };
    
    // View payslip
    const viewPayslip = (item: any) => {
      router.push({
        name: 'payslip-detail',
        params: { id: item.id }
      });
    };
    
    // Download payslip
    const downloadPayslip = (item: any) => {
      downloadingId.value = item.id;
      
      // Simulate API call
      setTimeout(() => {
        // In a real app, this would trigger a file download
        console.log(`Downloading payslip ${item.id}...`);
        downloadingId.value = null;
      }, 1000);
    };
    
    // Export payslips
    const exportPayslips = () => {
      exportDialog.value = true;
    };
    
    // Confirm export
    const confirmExport = () => {
      exporting.value = true;
      
      // Simulate API call
      setTimeout(() => {
        console.log(`Exporting payslips as ${exportFormat.value}...`);
        exporting.value = false;
        exportDialog.value = false;
      }, 1500);
    };
    
    // Initial load
    onMounted(() => {
      applyFilters();
    });
    
    return {
      loading,
      exporting,
      downloadingId,
      exportDialog,
      dateMenu,
      currentPage,
      filters,
      dateRange,
      dateRangeText,
      exportFormat,
      includeAllColumns,
      delimiter,
      exportFormats,
      statusOptions,
      departments,
      payslips,
      headers,
      formatCurrency,
      formatDate,
      formatDateRange,
      getStatusColor,
      getInitials,
      updateDateRange,
      applyFilters,
      resetFilters,
      viewPayslip,
      downloadPayslip,
      exportPayslips,
      confirmExport,
    };
  },
});
</script>
