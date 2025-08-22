<template>
  <v-container fluid class="pa-6">
    <!-- Loading State -->
    <v-row v-if="isLoading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <div class="mt-4 text-subtitle-1">Loading employee payroll details...</div>
      </v-col>
    </v-row>

    <!-- Error State -->
    <v-row v-else-if="error">
      <v-col cols="12">
        <v-alert type="error" variant="tonal" class="mb-6">
          <div class="d-flex align-center">
            <v-icon class="me-2">mdi-alert-circle</v-icon>
            <span>{{ error }}</span>
          </div>
          <template v-slot:append>
            <v-btn
              variant="text"
              color="error"
              @click="fetchEmployeePayroll"
              :loading="isLoading"
              class="mt-2"
            >
              <v-icon start>mdi-refresh</v-icon>
              Retry
            </v-btn>
          </template>
        </v-alert>
      </v-col>
    </v-row>

    <!-- Employee Payroll Details -->
    <template v-else>
      <v-row class="mb-6">
        <v-col cols="12" md="8">
          <v-card>
            <v-card-title class="d-flex justify-space-between align-center">
              <div>
                <div class="text-h6">{{ employee.name }}</div>
                <div class="text-subtitle-2 text-medium-emphasis">
                  {{ employee.department }} • {{ employee.position }}
                </div>
              </div>
              <v-chip :color="getStatusColor(employee.status)" size="small">
                {{ formatStatus(employee.status) }}
              </v-chip>
            </v-card-title>
            
            <v-divider></v-divider>
            
            <v-card-text>
              <v-tabs v-model="activeTab" grow>
                <v-tab value="details">Payroll Details</v-tab>
                <v-tab value="history">Payment History</v-tab>
                <v-tab value="documents">Documents</v-tab>
              </v-tabs>

              <v-window v-model="activeTab" class="mt-4">
                <!-- Payroll Details Tab -->
                <v-window-item value="details">
                  <v-row>
                    <v-col cols="12" md="6">
                      <v-card variant="outlined" class="mb-4">
                        <v-card-title class="text-subtitle-1 font-weight-bold">
                          Earnings
                        </v-card-title>
                        <v-card-text>
                          <v-table density="compact">
                            <tbody>
                              <tr v-for="(earning, index) in employee.earnings" :key="`earning-${index}`">
                                <td>{{ earning.type }}</td>
                                <td class="text-right">{{ formatCurrency(earning.amount) }}</td>
                              </tr>
                              <tr class="font-weight-bold">
                                <td>Total Earnings</td>
                                <td class="text-right">{{ formatCurrency(totalEarnings) }}</td>
                              </tr>
                            </tbody>
                          </v-table>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    
                    <v-col cols="12" md="6">
                      <v-card variant="outlined" class="mb-4">
                        <v-card-title class="text-subtitle-1 font-weight-bold">
                          Deductions
                        </v-card-title>
                        <v-card-text>
                          <v-table density="compact">
                            <tbody>
                              <tr v-for="(deduction, index) in employee.deductions" :key="`deduction-${index}`">
                                <td>{{ deduction.type }}</td>
                                <td class="text-right">{{ formatCurrency(deduction.amount) }}</td>
                              </tr>
                              <tr class="font-weight-bold">
                                <td>Total Deductions</td>
                                <td class="text-right">{{ formatCurrency(totalDeductions) }}</td>
                              </tr>
                            </tbody>
                          </v-table>
                        </v-card-text>
                      </v-card>
                      
                      <v-card variant="outlined">
                        <v-card-text>
                          <v-row>
                            <v-col cols="6">
                              <div class="text-subtitle-2">Net Pay</div>
                              <div class="text-h5 font-weight-bold text-primary">
                                {{ formatCurrency(netPay) }}
                              </div>
                            </v-col>
                            <v-col cols="6" class="text-right">
                              <div class="text-subtitle-2">Pay Period</div>
                              <div class="text-subtitle-1">
                                {{ formatDate(employee.payPeriodStart) }} - {{ formatDate(employee.payPeriodEnd) }}
                              </div>
                            </v-col>
                          </v-row>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                </v-window-item>

                <!-- Payment History Tab -->
                <v-window-item value="history">
                  <v-card variant="outlined">
                    <v-card-text>
                      <v-data-table
                        :headers="paymentHistoryHeaders"
                        :items="paymentHistory"
                        :items-per-page="5"
                        class="elevation-1"
                      >
                        <template v-slot:item.amount="{ item }">
                          {{ formatCurrency(item.amount) }}
                        </template>
                        <template v-slot:item.status="{ item }">
                          <v-chip :color="getStatusColor(item.status)" size="small">
                            {{ formatStatus(item.status) }}
                          </v-chip>
                        </template>
                        <template v-slot:item.actions="{ item }">
                          <v-btn
                            icon
                            size="small"
                            variant="text"
                            @click="viewPayslip(item)"
                          >
                            <v-icon>mdi-file-document-outline</v-icon>
                          </v-btn>
                        </template>
                      </v-data-table>
                    </v-card-text>
                  </v-card>
                </v-window-item>

                <!-- Documents Tab -->
                <v-window-item value="documents">
                  <v-card variant="outlined">
                    <v-card-text>
                      <v-data-table
                        :headers="documentHeaders"
                        :items="documents"
                        :items-per-page="5"
                        class="elevation-1"
                      >
                        <template v-slot:item.actions="{ item }">
                          <v-btn
                            icon
                            size="small"
                            variant="text"
                            @click="downloadDocument(item)"
                          >
                            <v-icon>mdi-download</v-icon>
                          </v-btn>
                        </template>
                      </v-data-table>
                    </v-card-text>
                  </v-card>
                </v-window-item>
              </v-window>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <!-- Employee Information Card -->
          <v-card class="mb-4">
            <v-card-title class="text-subtitle-1 font-weight-bold">
              Employee Information
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <div class="d-flex align-center mb-4">
                <v-avatar color="primary" size="64" class="me-4">
                  <span class="text-h5">{{ getInitials(employee.name) }}</span>
                </v-avatar>
                <div>
                  <div class="text-subtitle-1 font-weight-bold">{{ employee.name }}</div>
                  <div class="text-caption text-medium-emphasis">Employee ID: {{ employee.employeeId }}</div>
                  <div class="text-caption text-medium-emphasis">{{ employee.email }}</div>
                </div>
              </div>

              <v-divider class="my-3"></v-divider>

              <v-list density="compact" class="bg-transparent">
                <v-list-item prepend-icon="mdi-account-tie">
                  <v-list-item-title>Position</v-list-item-title>
                  <v-list-item-subtitle>{{ employee.position }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item prepend-icon="mdi-office-building">
                  <v-list-item-title>Department</v-list-item-title>
                  <v-list-item-subtitle>{{ employee.department }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item prepend-icon="mdi-calendar">
                  <v-list-item-title>Hire Date</v-list-item-title>
                  <v-list-item-subtitle>{{ formatDate(employee.hireDate) }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item prepend-icon="mdi-account-cash">
                  <v-list-item-title>Pay Type</v-list-item-title>
                  <v-list-item-subtitle>{{ employee.payType }} ({{ formatCurrency(employee.payRate) }} per {{ employee.payFrequency }})</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <!-- Quick Actions -->
          <v-card>
            <v-card-title class="text-subtitle-1 font-weight-bold">
              Quick Actions
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <v-list density="compact" class="bg-transparent">
                <v-list-item
                  v-for="(action, index) in quickActions"
                  :key="`action-${index}`"
                  :prepend-icon="action.icon"
                  :title="action.title"
                  :value="action.title"
                  :disabled="action.disabled"
                  @click="action.action()"
                  link
                ></v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { format } from 'date-fns';

const route = useRoute();
const router = useRouter();

// State
const isLoading = ref(true);
const error = ref<string | null>(null);
const activeTab = ref('details');
const employee = ref({
  id: '',
  name: 'John Doe',
  email: 'john.doe@example.com',
  employeeId: 'EMP-001',
  department: 'Engineering',
  position: 'Senior Software Engineer',
  status: 'active',
  hireDate: '2020-01-15',
  payType: 'Salary',
  payRate: 100000,
  payFrequency: 'year',
  payPeriodStart: '2023-04-01',
  payPeriodEnd: '2023-04-15',
  earnings: [
    { type: 'Base Salary', amount: 3846.15 },
    { type: 'Overtime', amount: 500.00 },
    { type: 'Bonus', amount: 1000.00 }
  ],
  deductions: [
    { type: 'Federal Tax', amount: 1000.00 },
    { type: 'State Tax', amount: 300.00 },
    { type: 'Social Security', amount: 350.00 },
    { type: 'Medical', amount: 200.00 },
    { type: '401(k)', amount: 500.00 }
  ]
});

const paymentHistory = ref([
  { id: 'PAY-001', date: '2023-03-15', payPeriod: 'Mar 1 - Mar 15, 2023', amount: 4196.15, status: 'paid' },
  { id: 'PAY-002', date: '2023-03-31', payPeriod: 'Mar 16 - Mar 31, 2023', amount: 3846.15, status: 'paid' },
  { id: 'PAY-003', date: '2023-04-15', payPeriod: 'Apr 1 - Apr 15, 2023', amount: 5346.15, status: 'pending' }
]);

const documents = ref([
  { id: 'DOC-001', name: '2023 W-2 Form', type: 'Tax Document', date: '2023-01-31' },
  { id: 'DOC-002', name: 'Q1 2023 Paystub Summary', type: 'Paystub', date: '2023-04-01' },
  { id: 'DOC-003', name: 'Employment Contract', type: 'Contract', date: '2020-01-15' }
]);

// Computed
const totalEarnings = computed(() => {
  return employee.value.earnings.reduce((sum, earning) => sum + earning.amount, 0);
});

const totalDeductions = computed(() => {
  return employee.value.deductions.reduce((sum, deduction) => sum + deduction.amount, 0);
});

const netPay = computed(() => {
  return totalEarnings.value - totalDeductions.value;
});

const paymentHistoryHeaders = [
  { title: 'Payment ID', key: 'id' },
  { title: 'Date', key: 'date' },
  { title: 'Pay Period', key: 'payPeriod' },
  { title: 'Amount', key: 'amount', align: 'end' },
  { title: 'Status', key: 'status' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
];

const documentHeaders = [
  { title: 'Document Name', key: 'name' },
  { title: 'Type', key: 'type' },
  { title: 'Date', key: 'date' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
];

const quickActions = [
  {
    title: 'Process One-Time Payment',
    icon: 'mdi-cash-plus',
    action: () => console.log('Process one-time payment'),
    disabled: false
  },
  {
    title: 'Update Tax Withholding',
    icon: 'mdi-bank-transfer',
    action: () => console.log('Update tax withholding'),
    disabled: false
  },
  {
    title: 'View Year-to-Date Summary',
    icon: 'mdi-chart-box',
    action: () => console.log('View YTD summary'),
    disabled: false
  },
  {
    title: 'Request Time Off',
    icon: 'mdi-calendar-account',
    action: () => console.log('Request time off'),
    disabled: false
  }
];

// Methods
const fetchEmployeePayroll = async () => {
  try {
    isLoading.value = true;
    error.value = null;
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    // In a real app, you would fetch the data from your API
    // const response = await payrollService.getEmployeePayroll(route.params.id);
    // employee.value = response.data;
  } catch (err) {
    console.error('Error fetching employee payroll:', err);
    error.value = 'Failed to load employee payroll details. Please try again later.';
  } finally {
    isLoading.value = false;
  }
};

const viewPayslip = (payment: any) => {
  router.push({ name: 'payslip-detail', params: { id: payment.id } });
};

const downloadDocument = (document: any) => {
  console.log('Download document:', document);
  // Implement document download logic
};

const formatDate = (dateString: string) => {
  return format(new Date(dateString), 'MMM d, yyyy');
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value);
};

const getStatusColor = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'success',
    pending: 'warning',
    inactive: 'error',
    paid: 'success',
    processing: 'info',
    failed: 'error'
  };
  return statusMap[status] || 'default';
};

const formatStatus = (status: string) => {
  return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
};

const getInitials = (name: string) => {
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase();
};

// Lifecycle Hooks
onMounted(() => {
  fetchEmployeePayroll();
});
</script>

<style scoped>
.v-avatar {
  background-color: #1976d2;
  color: white;
}

.v-list-item {
  border-radius: 8px;
  margin-bottom: 4px;
}

.v-list-item--active {
  background-color: rgba(25, 118, 210, 0.08);
}

.v-card {
  border-radius: 8px;
  overflow: hidden;
}

.v-table {
  background: transparent;
}
</style>
