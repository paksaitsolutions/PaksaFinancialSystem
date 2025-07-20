<template>
  <v-container fluid class="pa-6">
    <!-- Loading State -->
    <v-row v-if="isLoading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <div class="mt-4 text-subtitle-1">Loading payslip details...</div>
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
              @click="fetchPayslip"
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

    <!-- Payslip Details -->
    <template v-else>
      <!-- Header -->
      <v-row class="mb-4" align="center">
        <v-col cols="12" sm="6" md="8">
          <div class="d-flex align-center">
            <v-btn
              icon
              variant="text"
              class="mr-2"
              @click="$router.go(-1)"
            >
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
            <div>
              <h1 class="text-h4 font-weight-bold">Payslip #{{ payslip?.payslipNumber || '...' }}</h1>
              <div class="d-flex align-center mt-1">
                <v-chip
                  :color="getStatusColor(payslip?.status)"
                  size="small"
                  class="mr-2"
                  label
                >
                  {{ formatStatus(payslip?.status) }}
                </v-chip>
                <span class="text-caption text-medium-emphasis">
                  Generated on {{ formatDate(payslip?.createdAt) }}
                </span>
              </div>
            </div>
          </div>
        </v-col>
        <v-col cols="12" sm="6" md="4" class="text-right">
          <v-btn
            color="primary"
            variant="outlined"
            class="mr-2"
            @click="downloadPayslip"
            :loading="isDownloading"
          >
            <v-icon start>mdi-download</v-icon>
            Download PDF
          </v-btn>
          <v-btn
            color="primary"
            @click="printPayslip"
            :loading="isPrinting"
          >
            <v-icon start>mdi-printer</v-icon>
            Print
          </v-btn>
        </v-col>
      </v-row>

      <!-- Summary Cards -->
      <v-row class="mb-6">
        <v-col cols="12" md="4">
          <v-card variant="flat" border class="h-100">
            <v-card-text>
              <div class="d-flex justify-space-between align-center">
                <div>
                  <div class="text-subtitle-2 text-medium-emphasis">Employee</div>
                  <div class="text-h6">
                    {{ payslip?.employee?.name || 'N/A' }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ payslip?.employee?.employeeId || '' }}
                  </div>
                </div>
                <v-avatar color="primary" size="48">
                  <v-icon>mdi-account</v-icon>
                </v-avatar>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="4">
          <v-card variant="flat" border class="h-100">
            <v-card-text>
              <div class="d-flex justify-space-between align-center">
                <div>
                  <div class="text-subtitle-2 text-medium-emphasis">Pay Period</div>
                  <div class="text-h6">
                    {{ formatDate(payslip?.payPeriodStart) }} - {{ formatDate(payslip?.payPeriodEnd) }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    Payment Date: {{ formatDate(payslip?.paymentDate) }}
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
                  <div class="text-subtitle-2 text-medium-emphasis">Net Pay</div>
                  <div class="text-h4 font-weight-bold">
                    {{ formatCurrency(payslip?.netPay) }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    Gross: {{ formatCurrency(payslip?.grossPay) }} | 
                    Deductions: {{ formatCurrency(payslip?.totalDeductions) }}
                  </div>
                </div>
                <v-icon color="success" size="40">mdi-cash-multiple</v-icon>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Tabs -->
      <v-tabs v-model="activeTab" color="primary" class="mb-6">
        <v-tab value="earnings">
          <v-icon start>mdi-cash-plus</v-icon>
          Earnings
        </v-tab>
        <v-tab value="deductions">
          <v-icon start>mdi-cash-minus</v-icon>
          Deductions
        </v-tab>
        <v-tab value="taxes">
          <v-icon start>mdi-bank</v-icon>
          Taxes
        </v-tab>
        <v-tab value="leave">
          <v-icon start>mdi-calendar</v-icon>
          Leave & Attendance
        </v-tab>
      </v-tabs>

      <v-window v-model="activeTab" class="elevation-1 rounded">
        <!-- Earnings Tab -->
        <v-window-item value="earnings">
          <v-card variant="flat" class="rounded-0">
            <v-card-text class="pa-0">
              <v-table density="comfortable">
                <thead>
                  <tr>
                    <th>Earnings Type</th>
                    <th class="text-right">Hours/Qty</th>
                    <th class="text-right">Rate</th>
                    <th class="text-right">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in payslip?.earnings" :key="`earn-${index}`">
                    <td>{{ item.type }}</td>
                    <td class="text-right">{{ item.hours || item.quantity || '-' }}</td>
                    <td class="text-right">{{ item.rate ? formatCurrency(item.rate) : '-' }}</td>
                    <td class="text-right font-weight-bold">{{ formatCurrency(item.amount) }}</td>
                  </tr>
                  <tr>
                    <td colspan="3" class="text-right font-weight-bold">Total Earnings:</td>
                    <td class="text-right font-weight-bold">{{ formatCurrency(payslip?.grossPay) }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>
        </v-window-item>

        <!-- Deductions Tab -->
        <v-window-item value="deductions">
          <v-card variant="flat" class="rounded-0">
            <v-card-text class="pa-0">
              <v-table density="comfortable">
                <thead>
                  <tr>
                    <th>Deduction Type</th>
                    <th class="text-right">Amount</th>
                    <th class="text-right">YTD Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in payslip?.deductions" :key="`deduct-${index}`">
                    <td>{{ item.type }}</td>
                    <td class="text-right">{{ formatCurrency(item.amount) }}</td>
                    <td class="text-right">{{ formatCurrency(item.ytdTotal) }}</td>
                  </tr>
                  <tr>
                    <td class="font-weight-bold">Total Deductions:</td>
                    <td class="text-right font-weight-bold">{{ formatCurrency(payslip?.totalDeductions) }}</td>
                    <td></td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>
        </v-window-item>

        <!-- Taxes Tab -->
        <v-window-item value="taxes">
          <v-card variant="flat" class="rounded-0">
            <v-card-text class="pa-0">
              <v-table density="comfortable">
                <thead>
                  <tr>
                    <th>Tax Type</th>
                    <th class="text-right">Amount</th>
                    <th class="text-right">YTD Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in payslip?.taxes" :key="`tax-${index}`">
                    <td>{{ item.type }}</td>
                    <td class="text-right">{{ formatCurrency(item.amount) }}</td>
                    <td class="text-right">{{ formatCurrency(item.ytdTotal) }}</td>
                  </tr>
                  <tr>
                    <td class="font-weight-bold">Total Taxes:</td>
                    <td class="text-right font-weight-bold">{{ formatCurrency(payslip?.totalTaxes) }}</td>
                    <td></td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>
        </v-window-item>

        <!-- Leave & Attendance Tab -->
        <v-window-item value="leave">
          <v-card variant="flat" class="rounded-0">
            <v-card-text class="pa-0">
              <v-table density="comfortable">
                <thead>
                  <tr>
                    <th>Leave Type</th>
                    <th class="text-right">Taken</th>
                    <th class="text-right">Balance</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in payslip?.leaveBalances" :key="`leave-${index}`">
                    <td>{{ item.type }}</td>
                    <td class="text-right">{{ item.taken }} days</td>
                    <td class="text-right">{{ item.balance }} days</td>
                  </tr>
                </tbody>
              </v-table>
              
              <v-divider class="my-4"></v-divider>
              
              <v-table density="comfortable" class="mt-4">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th class="text-right">Hours</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in payslip?.attendance" :key="`attend-${index}`">
                    <td>{{ formatDate(item.date) }}</td>
                    <td>{{ item.type }}</td>
                    <td>
                      <v-chip
                        :color="getAttendanceStatusColor(item.status)"
                        size="small"
                        label
                      >
                        {{ item.status }}
                      </v-chip>
                    </td>
                    <td class="text-right">{{ item.hours || '-' }}</td>
                  </tr>
                </tbody>
              </v-table>
            </v-card-text>
          </v-card>
        </v-window-item>
      </v-window>

      <!-- Additional Information -->
      <v-row class="mt-6">
        <v-col cols="12" md="6">
          <v-card variant="outlined">
            <v-card-title class="text-subtitle-1 font-weight-bold">
              Payment Information
            </v-card-title>
            <v-card-text>
              <v-list density="compact">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon icon="mdi-bank" class="me-4"></v-icon>
                  </template>
                  <v-list-item-title>Bank Account</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ payslip?.bankAccount?.bankName || 'N/A' }} 
                    (***{{ payslip?.bankAccount?.lastFourDigits || '****' }})
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon icon="mdi-cash-multiple" class="me-4"></v-icon>
                  </template>
                  <v-list-item-title>Payment Method</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ payslip?.paymentMethod || 'N/A' }}
                  </v-list-item-subtitle>
                </v-list-item>
                <v-list-item v-if="payslip?.paymentReference">
                  <template v-slot:prepend>
                    <v-icon icon="mdi-note-text" class="me-4"></v-icon>
                  </template>
                  <v-list-item-title>Payment Reference</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ payslip.paymentReference }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="6">
          <v-card variant="outlined">
            <v-card-title class="text-subtitle-1 font-weight-bold">
              YTD Summary
            </v-card-title>
            <v-card-text>
              <v-list density="compact" class="py-0">
                <v-list-item class="px-0">
                  <v-list-item-title class="text-subtitle-2">Gross Pay</v-list-item-title>
                  <template v-slot:append>
                    <span class="font-weight-medium">{{ formatCurrency(payslip?.ytdGrossPay) }}</span>
                  </template>
                </v-list-item>
                <v-list-item class="px-0">
                  <v-list-item-title class="text-subtitle-2">Total Deductions</v-list-item-title>
                  <template v-slot:append>
                    <span class="font-weight-medium">{{ formatCurrency(payslip?.ytdDeductions) }}</span>
                  </template>
                </v-list-item>
                <v-list-item class="px-0">
                  <v-list-item-title class="text-subtitle-2">Total Taxes</v-list-item-title>
                  <template v-slot:append>
                    <span class="font-weight-medium">{{ formatCurrency(payslip?.ytdTaxes) }}</span>
                  </template>
                </v-list-item>
                <v-divider class="my-2"></v-divider>
                <v-list-item class="px-0">
                  <v-list-item-title class="text-subtitle-1 font-weight-bold">Net Pay YTD</v-list-item-title>
                  <template v-slot:append>
                    <span class="text-h6 font-weight-bold">{{ formatCurrency(payslip?.ytdNetPay) }}</span>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Footer Actions -->
      <v-row class="mt-6">
        <v-col cols="12" class="text-right">
          <v-btn
            color="primary"
            variant="outlined"
            class="mr-2"
            @click="$router.go(-1)"
          >
            Back to List
          </v-btn>
          <v-btn
            color="primary"
            @click="printPayslip"
            :loading="isPrinting"
          >
            <v-icon start>mdi-printer</v-icon>
            Print Payslip
          </v-btn>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { usePayslipStore } from '../store/payslips';
import { storeToRefs } from 'pinia';
import { format, parseISO } from 'date-fns';

// Props
const route = useRoute();
const router = useRouter();
const payslipStore = usePayslipStore();

// Refs
const activeTab = ref('earnings');
const isDownloading = ref(false);
const isPrinting = ref(false);

// Computed
const { currentPayslip: payslip, isLoading, error } = storeToRefs(payslipStore);

// Methods
const fetchPayslip = async () => {
  const payslipId = route.params.id as string;
  await payslipStore.fetchPayslip(payslipId);
};

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return 'N/A';
  try {
    return format(parseISO(dateString), 'MMM d, yyyy');
  } catch (error) {
    return dateString;
  }
};

const formatCurrency = (amount: number | undefined) => {
  if (amount === undefined || amount === null) return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

const getStatusColor = (status: string | undefined) => {
  switch (status?.toLowerCase()) {
    case 'paid':
      return 'success';
    case 'pending':
      return 'warning';
    case 'draft':
      return 'info';
    case 'cancelled':
      return 'error';
    default:
      return 'default';
  }
};

const formatStatus = (status: string | undefined) => {
  if (!status) return 'Unknown';
  return status
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
};

const getAttendanceStatusColor = (status: string | undefined) => {
  switch (status?.toLowerCase()) {
    case 'present':
      return 'success';
    case 'absent':
      return 'error';
    case 'late':
      return 'warning';
    case 'half-day':
      return 'info';
    default:
      return 'default';
  }
};

const downloadPayslip = async () => {
  if (!payslip.value) return;
  
  isDownloading.value = true;
  try {
    // TODO: Implement actual PDF generation and download
    console.log('Downloading payslip PDF for:', payslip.value.payslipNumber);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Create a dummy PDF download
    const link = document.createElement('a');
    link.href = '#'; // Replace with actual PDF URL
    link.download = `payslip-${payslip.value.payslipNumber}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } catch (error) {
    console.error('Error downloading payslip:', error);
  } finally {
    isDownloading.value = false;
  }
};

const printPayslip = () => {
  isPrinting.value = true;
  setTimeout(() => {
    window.print();
    isPrinting.value = false;
  }, 500);
};

// Lifecycle hooks
onMounted(() => {
  fetchPayslip();
  
  // Set up before print listener to handle print-specific styles
  window.matchMedia('print').addEventListener('change', (e) => {
    if (e.matches) {
      // Before print
      document.body.classList.add('print-mode');
    } else {
      // After print
      document.body.classList.remove('print-mode');
    }
  });
});
</script>

<style scoped>
/* Print-specific styles */
@media print {
  @page {
    size: A4;
    margin: 10mm;
  }
  
  body {
    font-size: 12px;
    line-height: 1.4;
    color: #000;
    background: #fff;
  }
  
  .v-container {
    padding: 0 !important;
    max-width: 100% !important;
  }
  
  .v-navigation-drawer,
  .v-app-bar,
  .v-footer,
  .v-toolbar,
  .no-print {
    display: none !important;
  }
  
  .v-card {
    box-shadow: none !important;
    border: 1px solid #e0e0e0 !important;
    page-break-inside: avoid;
  }
  
  .v-window {
    height: auto !important;
  }
  
  .v-window__container {
    position: relative !important;
    height: auto !important;
  }
  
  .v-window-item {
    position: relative !important;
  }
  
  .v-tabs {
    display: none;
  }
  
  /* Show all tab content when printing */
  .v-window-item {
    display: block !important;
    opacity: 1 !important;
    transform: none !important;
  }
  
  .v-window-item + .v-window-item {
    margin-top: 20mm;
    page-break-before: always;
  }
  
  /* Ensure tables don't break across pages */
  table {
    page-break-inside: auto;
  }
  
  tr {
    page-break-inside: avoid;
    page-break-after: auto;
  }
  
  thead {
    display: table-header-group;
  }
  
  tfoot {
    display: table-footer-group;
  }
  
  /* Hide print button when printing */
  .v-btn {
    display: none !important;
  }
}

/* Additional styles for better print layout */
.print-header {
  display: none;
}

@media print {
  .print-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10mm;
    padding-bottom: 2mm;
    border-bottom: 1px solid #e0e0e0;
  }
  
  .print-header h1 {
    margin: 0;
    font-size: 18px;
  }
  
  .print-header .print-meta {
    text-align: right;
    font-size: 12px;
    color: #666;
  }
  
  .print-footer {
    margin-top: 5mm;
    padding-top: 2mm;
    border-top: 1px solid #e0e0e0;
    font-size: 10px;
    color: #666;
    text-align: center;
  }
  
  /* Ensure proper spacing for printed pages */
  .v-card {
    margin-bottom: 5mm;
  }
  
  /* Hide tabs content when printing individual tabs */
  .v-window-item {
    display: none;
  }
  
  .v-window-item--active {
    display: block !important;
  }
}
</style>
