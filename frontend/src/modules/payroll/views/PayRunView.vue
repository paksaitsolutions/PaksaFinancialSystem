<template>
  <v-container fluid class="pa-6">
    <!-- Loading State -->
    <v-row v-if="isLoading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circ>
        <div class="mt-4 text-subtitle-1">Loading pay run details...</div>
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
              @click="fetchPayRun"
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

    <!-- Pay Run Details -->
    <template v-else>
      <!-- Tax Summary Card -->
      <v-card class="mb-6">
        <v-card-title class="text-subtitle-1 font-weight-bold">
          Tax Summary
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="4">
              <div class="text-subtitle-2">Total Tax Amount</div>
              <div class="text-h6 font-weight-bold">
                {{ formatCurrency(payRun.taxAmount) }}
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="text-subtitle-2">Tax Breakdown</div>
              <div v-for="(amount, bracket) in payRun.taxBreakdown" :key="bracket" class="text-caption">
                {{ bracket }}: {{ formatCurrency(amount) }}
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="text-subtitle-2">Exemptions</div>
              <div v-for="(amount, exemption) in payRun.exemptions" :key="exemption" class="text-caption">
                {{ exemption }}: {{ formatCurrency(amount) }}
              </div>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <!-- Pay Run Details -->
      <!-- Header -->
      <v-row class="mb-4" align="center">
        <v-col cols="12" sm="6" md="8">
          <div class="d-flex align-center">
            <v-btn
              icon
              variant="text"
              class="mr-2"
              @click="$router.push({ name: 'payroll-runs' })"
            >
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
            <div>
              <h1 class="text-h4 font-weight-bold">Pay Run #{{ payRun?.payRunNumber || '...' }}</h1>
              <div class="d-flex align-center mt-1">
                <v-chip
                  :color="getStatusColor(payRun?.status)"
                  size="small"
                  class="mr-2"
                  label
                >
                  {{ formatStatus(payRun?.status) }}
                </v-chip>
                <span class="text-caption text-medium-emphasis">
                  Created on {{ formatDate(payRun?.createdAt) }} by {{ payRun?.createdBy?.name || 'System' }}
                </span>
              </div>
            </div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="4" class="text-right">
          <v-btn
            v-if="canProcessPayRun"
            color="primary"
            prepend-icon="mdi-cash-multiple"
            :to="{ name: 'payroll-run-process', params: { id: $route.params.id } }"
            class="mr-2"
          >
            Process Pay Run
          </v-btn>
          <v-btn
            v-else-if="canApprovePayRun"
            color="success"
            prepend-icon="mdi-check-circle"
            :to="{ name: 'payroll-run-approve', params: { id: $route.params.id } }"
            class="mr-2"
          >
            Approve Pay Run
          </v-btn>
          
          <v-menu>
            <template v-slot:activator="{ props: menuProps }">
              <v-btn
                v-bind="menuProps"
                variant="outlined"
                color="primary"
                class="text-none"
              >
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>
            <v-list density="compact">
              <v-list-item
                v-for="(action, i) in actionItems"
                :key="i"
                :value="action.title"
                @click="action.action"
                :disabled="action.disabled"
              >
                <template v-slot:prepend>
                  <v-icon :icon="action.icon" :color="action.color"></v-icon>
                </template>
                <v-list-item-title>{{ action.title }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-col>
      </v-row>

      <!-- Summary Cards -->
      <v-row class="mb-6">
        <v-col cols="12" md="4">
          <v-card variant="flat" border class="h-100">
            <v-card-text>
              <div class="d-flex justify-space-between align-center">
                <div>
                  <div class="text-subtitle-2 text-medium-emphasis">Pay Period</div>
                  <div class="text-h6">
                    {{ formatDate(payRun?.payPeriodStart) }} - {{ formatDate(payRun?.payPeriodEnd) }}
                  </div>
                </div>
                <v-icon color="primary" size="40">mdi-calendar-range</v-icon>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="4">
          <v-card variant="flat" border class="h-100">
            <v-card-text>
              <div class="d-flex justify-space-between align-center">
                <div>
                  <div class="text-subtitle-2 text-medium-emphasis">Payment Date</div>
                  <div class="text-h6">
                    {{ formatDate(payRun?.paymentDate) }}
                  </div>
                </div>
                <v-icon color="success" size="40">mdi-calendar-check</v-icon>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="4">
          <v-card variant="flat" border class="h-100">
            <v-card-text>
              <div class="d-flex justify-space-between align-center">
                <div>
                  <div class="text-subtitle-2 text-medium-emphasis">Employees</div>
                  <div class="text-h6">
                    {{ payRun?.employeeCount || 0 }} employees
                  </div>
                </div>
                <v-icon color="info" size="40">mdi-account-group</v-icon>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Tabs -->
      <v-tabs v-model="activeTab" color="primary" class="mb-6">
        <v-tab value="summary">
          <v-icon start>mdi-chart-box</v-icon>
          Summary
        </v-tab>
        <v-tab value="payslips" :disabled="!payRun?.payslips?.length">
          <v-icon start>mdi-file-document-multiple</v-icon>
          Payslips ({{ payRun?.payslips?.length || 0 }})
        </v-tab>
        <v-tab value="transactions" :disabled="!payRun?.transactions?.length">
          <v-icon start>mdi-bank-transfer</v-icon>
          Transactions ({{ payRun?.transactions?.length || 0 }})
        </v-tab>
        <v-tab value="audit">
          <v-icon start>mdi-history</v-icon>
          Audit Log
        </v-tab>
      </v-tabs>

      <!-- Tab Content -->
      <v-window v-model="activeTab" class="elevation-1 rounded">
        <!-- Summary Tab -->
        <v-window-item value="summary">
          <v-card variant="flat" class="rounded-0">
            <v-card-text class="pa-6">
              <v-row>
                <!-- Earnings Summary -->
                <v-col cols="12" md="6">
                  <v-card variant="outlined" class="mb-6">
                    <v-card-title class="text-subtitle-1 font-weight-bold">
                      <v-icon start>mdi-cash-plus</v-icon>
                      Earnings Summary
                    </v-card-title>
                    <v-divider></v-divider>
                    <v-card-text>
                      <v-table density="comfortable">
                        <thead>
                          <tr>
                            <th>Earnings Type</th>
                            <th class="text-right">Amount</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="(amount, type) in payRun?.summary?.earnings || {}" :key="`earn-${type}`">
                            <td>{{ formatEarningsType(type) }}</td>
                            <td class="text-right">{{ formatCurrency(amount) }}</td>
                          </tr>
                          <tr class="font-weight-bold">
                            <td>Total Earnings</td>
                            <td class="text-right">{{ formatCurrency(payRun?.totalGross) }}</td>
                          </tr>
                        </tbody>
                      </v-table>
                    </v-card-text>
                  </v-card>
                </v-col>

                <!-- Deductions Summary -->
                <v-col cols="12" md="6">
                  <v-card variant="outlined" class="mb-6">
                    <v-card-title class="text-subtitle-1 font-weight-bold">
                      <v-icon start>mdi-cash-minus</v-icon>
                      Deductions Summary
                    </v-card-title>
                    <v-divider></v-divider>
                    <v-card-text>
                      <v-table density="comfortable">
                        <thead>
                          <tr>
                            <th>Deduction Type</th>
                            <th class="text-right">Amount</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="(amount, type) in payRun?.summary?.deductions || {}" :key="`deduct-${type}`">
                            <td>{{ formatDeductionType(type) }}</td>
                            <td class="text-right">{{ formatCurrency(amount) }}</td>
                          </tr>
                          <tr class="font-weight-bold">
                            <td>Total Deductions</td>
                            <td class="text-right">{{ formatCurrency(payRun?.totalDeductions) }}</td>
                          </tr>
                        </tbody>
                      </v-table>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Totals Card -->
              <v-row>
                <v-col cols="12" md="8" offset-md="2">
                  <v-card variant="outlined" class="border-primary">
                    <v-card-text class="pa-6">
                      <v-row>
                        <v-col cols="12" md="6" class="text-center text-md-right">
                          <div class="text-h5 font-weight-bold">
                            {{ formatCurrency(payRun?.totalNet) }}
                          </div>
                          <div class="text-subtitle-2 text-medium-emphasis">Net Pay</div>
                        </v-col>
                        <v-col cols="12" md="6" class="text-center text-md-left">
                          <div class="text-h5 font-weight-bold">
                            {{ payRun?.employeeCount || 0 }}
                          </div>
                          <div class="text-subtitle-2 text-medium-emphasis">Employees</div>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Notes -->
              <v-row class="mt-6">
                <v-col cols="12">
                  <v-card variant="outlined">
                    <v-card-title class="text-subtitle-1 font-weight-bold">
                      <v-icon start>mdi-note-text</v-icon>
                      Notes
                    </v-card-title>
                    <v-divider></v-divider>
                    <v-card-text>
                      <div v-if="payRun?.notes">
                        {{ payRun.notes }}
                      </div>
                      <div v-else class="text-medium-emphasis font-italic">
                        No notes available for this pay run.
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-window-item>

        <!-- Payslips Tab -->
        <v-window-item value="payslips">
          <v-card variant="flat" class="rounded-0">
            <v-card-text class="pa-0">
              <v-data-table
                :headers="payslipHeaders"
                :items="payRun?.payslips || []"
                :loading="isLoading"
                :items-per-page="10"
                class="elevation-0"
              >
                <template v-slot:item.employee="{ item }">
                  <div class="d-flex align-center">
                    <v-avatar size="36" class="me-3" color="primary" variant="tonal">
                      <v-img v-if="item.employee?.avatar" :src="item.employee.avatar"></v-img>
                      <span v-else class="text-h6">{{ getInitials(item.employee?.name) }}</span>
                    </v-avatar>
                    <div>
                      <div class="font-weight-medium">{{ item.employee?.name || 'N/A' }}</div>
                      <div class="text-caption text-medium-emphasis">{{ item.employee?.employeeId || 'N/A' }}</div>
                    </div>
                  </div>
                </template>

                <template v-slot:item.grossPay="{ item }">
                  {{ formatCurrency(item.grossPay) }}
                </template>

                <template v-slot:item.totalDeductions="{ item }">
                  <span :class="{ 'text-error': item.totalDeductions > 0 }">
                    {{ formatCurrency(item.totalDeductions) }}
                  </span>
                </template>

                <template v-slot:item.netPay="{ item }">
                  <span class="font-weight-bold">{{ formatCurrency(item.netPay) }}</span>
                </template>

                <template v-slot:item.status="{ item }">
                  <v-chip
                    :color="getPayslipStatusColor(item.status)"
                    size="small"
                    label
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
                    :to="{ name: 'payslip-detail', params: { id: item.id } }"
                  >
                    <v-icon size="small">mdi-eye</v-icon>
                    <v-tooltip activator="parent" location="top">View Details</v-tooltip>
                  </v-btn>
                  <v-btn
                    icon
                    variant="text"
                    size="small"
                    @click="downloadPayslip(item)"
                  >
                    <v-icon size="small">mdi-download</v-icon>
                    <v-tooltip activator="parent" location="top">Download PDF</v-tooltip>
                  </v-btn>
                </template>

                <template v-slot:no-data>
                  <div class="py-6 text-center">
                    <v-icon size="48" class="mb-2">mdi-file-document-outline</v-icon>
                    <div class="text-subtitle-1">No payslips found</div>
                    <div class="text-caption text-medium-emphasis">
                      There are no payslips available for this pay run.
                    </div>
                  </div>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-window-item>

        <!-- Transactions Tab -->
        <v-window-item value="transactions">
          <v-card variant="flat" class="rounded-0">
            <v-card-text class="pa-0">
              <v-data-table
                :headers="transactionHeaders"
                :items="payRun?.transactions || []"
                :loading="isLoading"
                :items-per-page="10"
                class="elevation-0"
              >
                <template v-slot:item.date="{ item }">
                  {{ formatDate(item.date) }}
                </template>

                <template v-slot:item.amount="{ item }">
                  <span :class="{ 'text-success': item.type === 'credit', 'text-error': item.type === 'debit' }">
                    {{ formatCurrency(item.amount) }}
                  </span>
                </template>

                <template v-slot:item.status="{ item }">
                  <v-chip
                    :color="getTransactionStatusColor(item.status)"
                    size="small"
                    label
                    class="text-capitalize"
                  >
                    {{ item.status }}
                  </v-chip>
                </template>

                <template v-slot:no-data>
                  <div class="py-6 text-center">
                    <v-icon size="48" class="mb-2">mdi-bank-transfer</v-icon>
                    <div class="text-subtitle-1">No transactions found</div>
                    <div class="text-caption text-medium-emphasis">
                      There are no transactions available for this pay run.
                    </div>
                  </div>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-window-item>

        <!-- Audit Log Tab -->
        <v-window-item value="audit">
          <v-card variant="flat" class="rounded-0">
            <v-card-text class="pa-0">
              <v-timeline density="compact" align="start" side="end">
                <v-timeline-item
                  v-for="(event, index) in auditLogs"
                  :key="index"
                  :dot-color="getAuditEventColor(event.action)"
                  size="small"
                >
                  <div class="d-flex justify-space-between">
                    <strong>{{ event.action }}</strong>
                    <span class="text-caption text-medium-emphasis ms-4">
                      {{ formatDateTime(event.timestamp) }}
                    </span>
                  </div>
                  <div class="text-caption">
                    {{ event.description }}
                  </div>
                  <div v-if="event.user" class="text-caption text-medium-emphasis">
                    By {{ event.user.name }} ({{ event.user.email }})
                  </div>
                </v-timeline-item>
              </v-timeline>
              <div v-if="!auditLogs.length" class="py-6 text-center">
                <v-icon size="48" class="mb-2">mdi-history</v-icon>
                <div class="text-subtitle-1">No audit logs found</div>
                <div class="text-caption text-medium-emphasis">
                  There are no audit logs available for this pay run.
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-window-item>
      </v-window>
    </template>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useTaxPolicyStore } from '@/modules/tax/store/policy';
import { taxCalculationService } from '@/services/tax/taxCalculationService';
import { usePayrollStore } from '@/stores/payroll';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatDate, formatCurrency, formatDateTime } from '@/utils/formatters';

const route = useRoute();
const router = useRouter();
const isLoading = ref(true);
const error = ref<string | null>(null);
const payRun = ref<any>(null);
const taxPolicyStore = useTaxPolicyStore();

// State
const activeTab = ref('summary');
const auditLogs = ref<any[]>([]);

// Table headers
const payslipHeaders = [
  { title: 'Employee', key: 'employee', sortable: true },
  { title: 'Gross Pay', key: 'grossPay', align: 'end', sortable: true },
  { title: 'Deductions', key: 'totalDeductions', align: 'end', sortable: true },
  { title: 'Net Pay', key: 'netPay', align: 'end', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

const transactionHeaders = [
  { title: 'Date', key: 'date', sortable: true },
  { title: 'Description', key: 'description', sortable: true },
  { title: 'Type', key: 'type', sortable: true },
  { title: 'Amount', key: 'amount', align: 'end', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Reference', key: 'reference', sortable: true },
];

// Computed
const actionItems = computed(() => {
  const items = [
    {
      title: 'Edit Pay Run',
      icon: 'mdi-pencil',
      action: () => {},
      disabled: !['draft', 'pending_approval'].includes(payRun.value?.status),
    },
    {
      title: 'Export to Excel',
      icon: 'mdi-microsoft-excel',
      action: exportToExcel,
      disabled: false,
    },
    {
      title: 'Export to PDF',
      icon: 'mdi-file-pdf',
      action: exportToPdf,
      disabled: false,
    },
    {
      title: 'Print',
      icon: 'mdi-printer',
      action: printDocument,
      disabled: false,
    },
    { type: 'divider' },
    {
      title: 'Cancel Pay Run',
      icon: 'mdi-cancel',
      color: 'error',
      action: confirmCancelPayRun,
      disabled: !['draft', 'pending_approval'].includes(payRun.value?.status),
    },
  ];

  return items;
});

const canProcessPayRun = computed(() => {
  return ['draft', 'pending_approval'].includes(payRun.value?.status);
});

const canApprovePayRun = computed(() => {
  return payRun.value?.status === 'pending_approval';
});

// Lifecycle hooks
onMounted(() => {
  fetchPayRun();
  fetchAuditLogs();
});

// Watch for route changes
watch(
  () => route.params.id,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      fetchPayRun();
      fetchAuditLogs();
    }
  }
);

// Methods
async function fetchPayRun() {
  try {
    isLoading.value = true;
    error.value = null;
    
    // Fetch tax policy first
    await taxPolicyStore.fetchPolicy();
    
    const response = await payrollStore.getPayRunById(route.params.id as string);
    payRun.value = response;
    
    // Calculate tax details if not already present
    if (!response.taxAmount || !response.taxBreakdown) {
      const taxResult = taxCalculationService.calculatePayRunTax(response);
      payRun.value = {
        ...response,
        taxAmount: taxResult.taxAmount,
        taxBreakdown: taxResult.taxBreakdown,
        exemptions: taxResult.exemptions
      };
    }
  } catch (err: any) {
    console.error('Error fetching pay run:', err);
    error.value = err.message || 'Failed to load pay run details';
  } finally {
    isLoading.value = false;
  }
}

async function fetchAuditLogs() {
  try {
    // TODO: Replace with actual API call
    // const response = await payrollStore.getPayRunAuditLogs(route.params.id);
    // auditLogs.value = response;
    
    // Mock data for now
    auditLogs.value = [
      {
        id: '1',
        action: 'Created',
        description: 'Pay run was created',
        timestamp: new Date().toISOString(),
        user: {
          id: '1',
          name: 'Admin User',
          email: 'admin@example.com',
        },
      },
      {
        id: '2',
        action: 'Updated',
        description: 'Pay run was updated',
        timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
        user: {
          id: '1',
          name: 'Admin User',
          email: 'admin@example.com',
        },
      },
    ];
  } catch (err) {
    console.error('Error fetching audit logs:', err);
  }
}

function getStatusColor(status: string) {
  const colors = {
    draft: 'grey',
    processing: 'blue',
    pending_approval: 'orange',
    approved: 'green',
    paid: 'success',
    cancelled: 'error',
  };
  return colors[status as keyof typeof colors] || 'grey';
}

function formatStatus(status: string) {
  if (!status) return '';
  return status
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function getPayslipStatusColor(status: string) {
  const colors = {
    draft: 'grey',
    pending: 'orange',
    processed: 'blue',
    paid: 'success',
    cancelled: 'error',
  };
  return colors[status as keyof typeof colors] || 'grey';
}

function getTransactionStatusColor(status: string) {
  const colors = {
    pending: 'warning',
    processing: 'info',
    completed: 'success',
    failed: 'error',
    cancelled: 'error',
  };
  return colors[status as keyof typeof colors] || 'grey';
}

function getAuditEventColor(action: string) {
  const colors: Record<string, string> = {
    created: 'success',
    updated: 'info',
    deleted: 'error',
    approved: 'success',
    rejected: 'error',
    processed: 'primary',
  };
  return colors[action.toLowerCase()] || 'grey';
}

function getInitials(name: string) {
  if (!name) return '??';
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .substring(0, 2);
}

function formatEarningsType(type: string) {
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function formatDeductionType(type: string) {
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function downloadPayslip(payslip: any) {
  // TODO: Implement PDF generation and download
  console.log('Downloading payslip:', payslip.id);
  showSuccess('Payslip download will be implemented soon');
}

function exportToExcel() {
  // TODO: Implement Excel export
  showSuccess('Export to Excel will be implemented soon');
}

function exportToPdf() {
  // TODO: Implement PDF export
  showSuccess('Export to PDF will be implemented soon');
}

function printDocument() {
  window.print();
}

function confirmCancelPayRun() {
  // TODO: Implement cancel pay run confirmation
  if (confirm('Are you sure you want to cancel this pay run? This action cannot be undone.')) {
    cancelPayRun();
  }
}

async function cancelPayRun() {
  try {
    isLoading.value = true;
    // TODO: Implement cancel pay run API call
    // await payrollStore.cancelPayRun(route.params.id);
    showSuccess('Pay run has been cancelled');
    fetchPayRun();
  } catch (err: any) {
    console.error('Error cancelling pay run:', err);
    showError(err.message || 'Failed to cancel pay run');
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.v-timeline-item-body {
  font-size: 0.875rem;
}

.v-timeline-divider {
  min-width: 24px;
}

.v-timeline-divider__dot {
  margin: 0;
}

.v-timeline-divider__inner-dot {
  margin: 4px 0;
}

.v-card--variant-outlined {
  border: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
}

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

@media print {
  .no-print {
    display: none !important;
  }
  
  .v-toolbar,
  .v-tabs {
    display: none !important;
  }
  
  .v-window-item:not([value="summary"]) {
    display: none !important;
  }
  
  .v-card {
    box-shadow: none !important;
    border: none !important;
  }
  
  @page {
    size: A4;
    margin: 1cm;
  }
}
</style>
