<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <div>
              <v-icon class="me-2" size="large">mdi-history</v-icon>
              <span class="text-h5">Payroll History</span>
            </div>
            <div>
              <v-btn
                color="primary"
                class="me-2"
                prepend-icon="mdi-file-export"
                @click="exportPayroll"
              >
                Export
              </v-btn>
              <v-btn
                color="primary"
                variant="tonal"
                to="/payroll/run"
                prepend-icon="mdi-plus"
              >
                New Payroll Run
              </v-btn>
            </div>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text>
            <v-row class="mb-4">
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="search"
                  label="Search payroll"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  clearable
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="statusFilter"
                  :items="statusOptions"
                  label="Status"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  clearable
                ></v-select>
              </v-col>
              <v-col cols="12" md="3">
                <v-select
                  v-model="yearFilter"
                  :items="yearOptions"
                  label="Year"
                  variant="outlined"
                  density="comfortable"
                  hide-details
                  clearable
                ></v-select>
              </v-col>
              <v-col cols="12" md="2">
                <v-btn
                  color="secondary"
                  variant="tonal"
                  block
                  @click="resetFilters"
                >
                  Reset Filters
                </v-btn>
              </v-col>
            </v-row>

            <v-data-table
              :headers="headers"
              :items="filteredPayrolls"
              :search="search"
              :loading="isLoading"
              :items-per-page="10"
              class="elevation-1"
            >
              <template v-slot:item.payPeriod="{ item }">
                {{ formatDate(item.startDate) }} - {{ formatDate(item.endDate) }}
              </template>
              
              <template v-slot:item.payDate="{ item }">
                {{ formatDate(item.payDate) }}
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
              
              <template v-slot:item.totalNetPay="{ item }">
                {{ formatCurrency(item.totalNetPay) }}
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="primary"
                  @click="viewPayroll(item)"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
                <v-btn
                  icon
                  size="small"
                  variant="text"
                  color="secondary"
                  @click="exportPayrollItem(item)"
                  :loading="item.exporting"
                >
                  <v-icon>mdi-file-export</v-icon>
                </v-btn>
              </template>
              
              <template v-slot:no-data>
                <div class="text-center py-4">
                  <v-icon size="64" class="mb-2">mdi-file-document-outline</v-icon>
                  <div class="text-subtitle-1">No payroll records found</div>
                  <v-btn
                    color="primary"
                    variant="text"
                    class="mt-2"
                    to="/payroll/run"
                  >
                    Run Payroll
                  </v-btn>
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { format, parseISO } from 'date-fns';

const router = useRouter();

// Data
const search = ref('');
const statusFilter = ref('');
const yearFilter = ref('');
const isLoading = ref(false);

// Options
const statusOptions = [
  { title: 'Draft', value: 'draft' },
  { title: 'Processing', value: 'processing' },
  { title: 'Completed', value: 'completed' },
  { title: 'Paid', value: 'paid' },
  { title: 'Cancelled', value: 'cancelled' },
];

const yearOptions = [
  { title: '2023', value: 2023 },
  { title: '2024', value: 2024 },
  { title: '2025', value: 2025 },
];

// Table headers
const headers = [
  { title: 'Payroll ID', key: 'id', sortable: true },
  { title: 'Pay Period', key: 'payPeriod', sortable: true },
  { title: 'Pay Date', key: 'payDate', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Employees', key: 'employeeCount', align: 'center', sortable: true },
  { title: 'Total Net Pay', key: 'totalNetPay', align: 'end', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

// Sample data - replace with API call
const payrolls = ref([
  {
    id: 'PR-2023-001',
    startDate: '2023-11-01',
    endDate: '2023-11-15',
    payDate: '2023-11-20',
    status: 'completed',
    employeeCount: 24,
    totalNetPay: 87456.32,
    type: 'Regular',
    approvedBy: 'John Smith',
    approvedAt: '2023-11-18T14:30:00Z',
    exporting: false,
  },
  {
    id: 'PR-2023-002',
    startDate: '2023-11-16',
    endDate: '2023-11-30',
    payDate: '2023-12-05',
    status: 'paid',
    employeeCount: 25,
    totalNetPay: 89234.56,
    type: 'Regular',
    approvedBy: 'John Smith',
    approvedAt: '2023-12-03T10:15:00Z',
    exporting: false,
  },
  {
    id: 'BONUS-2023-001',
    startDate: '2023-12-01',
    endDate: '2023-12-01',
    payDate: '2023-12-15',
    status: 'completed',
    employeeCount: 25,
    totalNetPay: 25000.00,
    type: 'Bonus',
    approvedBy: 'Jane Doe',
    approvedAt: '2023-12-10T16:45:00Z',
    exporting: false,
  },
  {
    id: 'PR-2023-003',
    startDate: '2023-12-01',
    endDate: '2023-12-15',
    payDate: '2023-12-20',
    status: 'processing',
    employeeCount: 25,
    totalNetPay: 90234.78,
    type: 'Regular',
    approvedBy: 'John Smith',
    approvedAt: '2023-12-18T09:20:00Z',
    exporting: false,
  },
  {
    id: 'PR-2023-004',
    startDate: '2023-12-16',
    endDate: '2023-12-31',
    payDate: '2024-01-05',
    status: 'draft',
    employeeCount: 25,
    totalNetPay: 0,
    type: 'Regular',
    approvedBy: '',
    approvedAt: '',
    exporting: false,
  },
]);

// Computed
const filteredPayrolls = computed(() => {
  return payrolls.value.filter(payroll => {
    const matchesSearch = !search.value || 
      payroll.id.toLowerCase().includes(search.value.toLowerCase()) ||
      payroll.type.toLowerCase().includes(search.value.toLowerCase());
    
    const matchesStatus = !statusFilter.value || 
      payroll.status === statusFilter.value;
    
    const matchesYear = !yearFilter.value || 
      new Date(payroll.payDate).getFullYear() === yearFilter.value;
    
    return matchesSearch && matchesStatus && matchesYear;
  });
});

// Methods
const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A';
  return format(parseISO(dateString), 'MMM d, yyyy');
};

const formatDateTime = (dateTimeString: string) => {
  if (!dateTimeString) return 'N/A';
  return format(parseISO(dateTimeString), 'MMM d, yyyy h:mm a');
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(amount);
};

const getStatusColor = (status: string) => {
  const statusColors: Record<string, string> = {
    draft: 'grey',
    processing: 'blue',
    completed: 'green',
    paid: 'success',
    cancelled: 'red',
  };
  return statusColors[status] || 'grey';
};

const viewPayroll = (item: any) => {
  router.push(`/payroll/history/${item.id}`);
};

const exportPayroll = () => {
  // Implementation for exporting all filtered payrolls
  console.log('Exporting filtered payrolls');
};

const exportPayrollItem = (item: any) => {
  item.exporting = true;
  // Simulate API call
  setTimeout(() => {
    console.log(`Exporting payroll ${item.id}`);
    item.exporting = false;
  }, 1000);
};

const resetFilters = () => {
  search.value = '';
  statusFilter.value = '';
  yearFilter.value = '';
};

// Lifecycle hooks
onMounted(() => {
  // Load payroll history from API
  isLoading.value = true;
  // Simulate API call
  setTimeout(() => {
    isLoading.value = false;
  }, 1000);
});
</script>
