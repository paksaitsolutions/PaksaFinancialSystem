<template>
  <div class="transactions-tab">
    <v-alert
      v-if="status !== 'paid'"
      type="info"
      variant="tonal"
      class="mb-6 rounded-lg"
      border="start"
      density="comfortable"
    >
      <template v-slot:prepend>
        <v-icon icon="mdi-information" class="me-2" />
      </template>
      <div class="d-flex align-center">
        <span>Bank transactions will be available after the pay run is marked as paid.</span>
      </div>
    </v-alert>
    
    <!-- Summary Cards -->
    <v-row class="mb-6" v-if="status === 'paid'">
      <v-col cols="12" sm="6" md="3">
        <v-card variant="flat" class="h-100 rounded-lg" border>
          <v-card-text class="pa-4">
            <div class="d-flex align-center">
              <v-avatar color="primary" variant="tonal" size="48" class="me-3">
                <v-icon icon="mdi-bank-transfer" size="24" />
              </v-avatar>
              <div>
                <div class="text-subtitle-2 text-medium-emphasis">Total Transactions</div>
                <div class="text-h5 font-weight-bold">{{ formattedTotalTransactions }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card variant="flat" class="h-100 rounded-lg" border>
          <v-card-text class="pa-4">
            <div class="d-flex align-center">
              <v-avatar color="success" variant="tonal" size="48" class="me-3">
                <v-icon icon="mdi-cash-multiple" size="24" />
              </v-avatar>
              <div>
                <div class="text-subtitle-2 text-medium-emphasis">Total Amount</div>
                <div class="text-h5 font-weight-bold">{{ formatCurrency(totalAmount) }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card variant="flat" class="h-100 rounded-lg" border>
          <v-card-text class="pa-4">
            <div class="d-flex align-center">
              <v-avatar color="info" variant="tonal" size="48" class="me-3">
                <v-icon icon="mdi-account-group" size="24" />
              </v-avatar>
              <div>
                <div class="text-subtitle-2 text-medium-emphasis">Employees Paid</div>
                <div class="text-h5 font-weight-bold">{{ employeesPaid }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" sm="6" md="3">
        <v-card variant="flat" class="h-100 rounded-lg" border>
          <v-card-text class="pa-4">
            <div class="d-flex align-center">
              <v-avatar color="warning" variant="tonal" size="48" class="me-3">
                <v-icon icon="mdi-alert-circle" size="24" />
              </v-avatar>
              <div>
                <div class="text-subtitle-2 text-medium-emphasis">Pending Actions</div>
                <div class="text-h5 font-weight-bold">{{ pendingActions }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Filters -->
    <v-card variant="flat" class="mb-6 rounded-lg" border v-if="status === 'paid'">
      <v-card-text class="pa-4">
        <v-row dense align="center">
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              label="Search transactions"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="comfortable"
              hide-details
              clearable
              class="rounded-pill"
              :disabled="status !== 'paid'"
            />
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="statusFilter"
              :items="statusOptions"
              label="Status"
              density="comfortable"
              variant="outlined"
              hide-details
              clearable
              class="rounded-pill"
            />
          </v-col>
          <v-col cols="12" md="4" class="d-flex justify-end">
            <v-btn-toggle
              v-model="dateRange"
              density="comfortable"
              variant="outlined"
              divided
              class="rounded-pill"
            >
              <v-btn value="today" size="small">Today</v-btn>
              <v-btn value="week" size="small">Week</v-btn>
              <v-btn value="month" size="small">Month</v-btn>
              <v-btn value="year" size="small">Year</v-btn>
            </v-btn-toggle>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
        <v-spacer />
        <v-btn
          color="primary"
          variant="tonal"
          prepend-icon="mdi-bank-transfer"
          @click="initiateBankTransfer"
          :loading="processing"
          :disabled="status !== 'processed'"
        >
          Initiate Bank Transfer
        </v-btn>
        <v-btn
          color="secondary"
          variant="tonal"
          prepend-icon="mdi-file-export"
          @click="exportTransactions"
          :loading="exporting"
          :disabled="!transactions.length"
          class="ml-2"
        >
          Export
        </v-btn>
      </v-card-actions>
      
    <!-- Transactions Table -->
    <v-card variant="flat" class="rounded-lg overflow-hidden" border v-if="status === 'paid'">
      <v-data-table
        :headers="headers"
        :items="filteredTransactions"
        :loading="loading"
        :items-per-page="pagination.itemsPerPage"
        :page="pagination.page"
        :items-length="pagination.totalItems"
        :server-items-length="pagination.totalItems"
        :items-per-page-options="[10, 25, 50]"
        @update:options="onTableOptionsChange"
        class="elevation-0"
        :loading-text="'Loading transactions...'"
        :no-data-text="'No transactions found'"
        :footer-props="{
          'items-per-page-options': [10, 25, 50],
          'items-per-page-text': 'Rows per page:',
          'show-current-page': true,
          'show-first-last-page': true,
          'page-text': '{0}-{1} of {2}'
        }"
      >
        <template v-slot:item.date="{ item }">
          {{ formatDate(item.date) }}
        </template>
        
        <template v-slot:item.amount="{ item }">
          <v-chip
            variant="tonal"
            :color="item.amount < 0 ? 'error' : 'success'"
            size="small"
            class="font-weight-medium"
          >
            {{ item.amount < 0 ? '-' : '' }}{{ formatCurrency(Math.abs(item.amount)) }}
          </v-chip>
        </template>
        
        <template v-slot:item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            variant="flat"
            size="small"
            class="text-uppercase font-weight-medium"
            :prepend-icon="getStatusIcon(item.status)"
            :text="formatStatus(item.status)"
          />
        </template>
        
        <template v-slot:item.actions="{ item }">
          <v-tooltip text="View Details" location="top">
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                icon
                variant="text"
                size="small"
                color="primary"
                @click="viewTransactionDetails(item.id)"
                class="mx-1"
              >
                <v-icon>mdi-eye-outline</v-icon>
              </v-btn>
            </template>
          </v-tooltip>
          
          <v-tooltip text="Download Receipt" location="top">
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                icon
                variant="text"
                size="small"
                color="secondary"
                @click="downloadReceipt(item.id)"
                :loading="downloadingReceipts[item.id]"
                :disabled="item.status !== 'completed'"
                class="mx-1"
              >
                <v-icon>mdi-file-download-outline</v-icon>
              </v-btn>
            </template>
          </v-tooltip>
          
          <v-menu>
            <template v-slot:activator="{ props: menu }">
              <v-tooltip text="More Actions" location="top">
                <template v-slot:activator="{ props: tooltip }">
                  <v-btn
                    v-bind="{ ...menu, ...tooltip }"
                    icon
                    variant="text"
                    size="small"
                    color="grey"
                    class="mx-1"
                  >
                    <v-icon>mdi-dots-vertical</v-icon>
                  </v-btn>
                </template>
              </v-tooltip>
            </template>
            <v-list density="compact">
              <v-list-item @click="copyTransactionLink(item.id)">
                <template v-slot:prepend>
                  <v-icon icon="mdi-link" size="small" class="me-2" />
                </template>
                <v-list-item-title>Copy Link</v-list-item-title>
              </v-list-item>
              <v-list-item @click="exportTransaction(item)" :disabled="item.status !== 'completed'">
                <template v-slot:prepend>
                  <v-icon icon="mdi-file-export" size="small" class="me-2" />
                </template>
                <v-list-item-title>Export</v-list-item-title>
              </v-list-item>
              <v-divider class="my-1" />
              <v-list-item 
                @click="cancelTransaction(item.id)" 
                :disabled="!['pending', 'processing'].includes(item.status)"
                class="text-error"
              >
                <template v-slot:prepend>
                  <v-icon icon="mdi-cancel" size="small" class="me-2" />
                </template>
                <v-list-item-title>Cancel Transaction</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </template>
        
        <template v-slot:no-data>
          <v-container class="fill-height" fluid>
            <v-row align="center" justify="center">
              <v-col cols="12" sm="8" md="6" lg="4" class="text-center">
                <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-bank-transfer</v-icon>
                <h3 class="text-h6 mb-2">
                  <template v-if="status !== 'paid'">
                    Transactions Unavailable
                  </template>
                  <template v-else>
                    No Transactions Found
                  </template>
                </h3>
                <p class="text-medium-emphasis mb-4">
                  <template v-if="status !== 'paid'">
                    Transactions will appear here after the pay run is marked as paid.
                  </template>
                  <template v-else>
                    No transactions match your current filters. Try adjusting your search criteria.
                  </template>
                </p>
                <v-btn
                  v-if="status === 'paid'"
                  color="primary"
                  variant="tonal"
                  prepend-icon="mdi-refresh"
                  @click="fetchTransactions"
                  class="mt-2"
                >
                  Refresh
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
        </template>
        
        <template v-slot:loading>
          <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
        </template>
      </v-data-table>
    </v-card>
    
    <!-- Transaction Details Dialog -->
    <v-dialog v-model="showTransactionDialog" max-width="800">
      <v-card v-if="selectedTransaction">
        <v-card-title class="d-flex align-center">
          <span class="text-h6">Transaction Details</span>
          <v-spacer />
          <v-btn icon @click="showTransactionDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-divider />
        
        <v-card-text class="pt-4">
          <v-row>
            <v-col cols="12" md="6">
              <v-list density="compact" class="transparent">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-identifier</v-icon>
                  </template>
                  <v-list-item-title>Transaction ID</v-list-item-title>
                  <v-list-item-subtitle class="text-right">
                    {{ selectedTransaction.id }}
                  </v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-calendar</v-icon>
                  </template>
                  <v-list-item-title>Date</v-list-item-title>
                  <v-list-item-subtitle class="text-right">
                    {{ formatDateTime(selectedTransaction.date) }}
                  </v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-cash-multiple</v-icon>
                  </template>
                  <v-list-item-title>Amount</v-list-item-title>
                  <v-list-item-subtitle 
                    class="text-right font-weight-bold"
                    :class="{ 'text-error': selectedTransaction.amount < 0, 'text-success': selectedTransaction.amount >= 0 }"
                  >
                    {{ formatCurrency(selectedTransaction.amount) }}
                  </v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-bank</v-icon>
                  </template>
                  <v-list-item-title>Bank Account</v-list-item-title>
                  <v-list-item-subtitle class="text-right">
                    {{ selectedTransaction.bankAccount?.name || 'N/A' }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-list density="compact" class="transparent">
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-account</v-icon>
                  </template>
                  <v-list-item-title>Employee</v-list-item-title>
                  <v-list-item-subtitle class="text-right">
                    {{ selectedTransaction.employee?.name || 'N/A' }}
                  </v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-account-bank</v-icon>
                  </template>
                  <v-list-item-title>Account Number</v-list-item-title>
                  <v-list-item-subtitle class="text-right">
                    {{ selectedTransaction.destinationAccount?.maskedNumber || 'N/A' }}
                  </v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-bank-transfer</v-icon>
                  </template>
                  <v-list-item-title>Reference</v-list-item-title>
                  <v-list-item-subtitle class="text-right">
                    {{ selectedTransaction.reference || 'N/A' }}
                  </v-list-item-subtitle>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon>mdi-information</v-icon>
                  </template>
                  <v-list-item-title>Status</v-list-item-title>
                  <v-list-item-subtitle class="text-right">
                    <v-chip
                      :color="getStatusColor(selectedTransaction.status)"
                      size="small"
                      :text="formatStatus(selectedTransaction.status)"
                      class="text-uppercase"
                    />
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
              
              <v-divider class="my-2" />
              
              <div class="text-subtitle-2 font-weight-medium mt-4 mb-2">Notes</div>
              <v-textarea
                v-model="selectedTransaction.notes"
                variant="outlined"
                rows="3"
                hide-details
                readonly
                placeholder="No notes available"
              />
            </v-col>
          </v-row>
          
          <v-divider class="my-4" />
          
          <div class="d-flex justify-end">
            <v-btn
              color="primary"
              variant="tonal"
              prepend-icon="mdi-download"
              @click="downloadReceipt(selectedTransaction.id)"
              :loading="downloadingReceipts[selectedTransaction.id]"
              class="mr-2"
            >
              Download Receipt
            </v-btn>
            <v-btn
              color="secondary"
              variant="text"
              @click="showTransactionDialog = false"
            >
              Close
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
    
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false">Close</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch } from 'vue';
import { format, parseISO } from 'date-fns';
import { useClipboard } from '@vueuse/core';
import { payrollService } from '@/services/payroll/payrollService';

type TransactionStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

interface Transaction {
  id: string;
  date: string | Date;
  reference: string;
  description: string;
  amount: number;
  status: TransactionStatus;
  bankAccount?: {
    id: string;
    name: string;
  };
  employee?: {
    id: string;
    name: string;
  };
  destinationAccount?: {
    id: string;
    maskedNumber: string;
    bankName?: string;
    accountType?: string;
  };
  notes?: string;
}

export default defineComponent({
  name: 'PayRunTransactionsTab',
  
  props: {
    payrunId: {
      type: String,
      required: true,
    },
    status: {
      type: String,
      required: true,
      validator: (value: string) => 
        ['draft', 'processing', 'processed', 'paid', 'cancelled'].includes(value),
    },
  },
  
  setup(props) {
    const loading = ref(false);
    const processing = ref(false);
    const exporting = ref(false);
    const search = ref('');
    const statusFilter = ref<string | null>(null);
    const dateRange = ref('month');
    const showTransactionDialog = ref(false);
    const selectedTransaction = ref<Transaction | null>(null);
    const downloadingReceipts = ref<Record<string, boolean>>({});
    const { copy } = useClipboard();
    
    // Status options for filter dropdown
    const statusOptions = [
      { title: 'All Statuses', value: null },
      { title: 'Completed', value: 'completed' },
      { title: 'Pending', value: 'pending' },
      { title: 'Processing', value: 'processing' },
      { title: 'Failed', value: 'failed' },
      { title: 'Cancelled', value: 'cancelled' },
    ];
    
    // Mock data for demonstration
    const mockTransactions: Transaction[] = [
      {
        id: 'txn_123456',
        date: new Date().toISOString(),
        reference: 'PAY-2023-001',
        description: 'Salary Payment - John Doe',
        amount: 3500.00,
        status: 'completed',
        bankAccount: { id: 'bank_123', name: 'Main Business Account' },
        employee: { id: 'emp_123', name: 'John Doe' },
        destinationAccount: { 
          id: 'dest_123', 
          maskedNumber: '****1234',
          bankName: 'Chase',
          accountType: 'checking'
        },
        notes: 'Regular monthly salary payment',
      },
      {
        id: 'txn_123457',
        date: new Date().toISOString(),
        reference: 'PAY-2023-002',
        description: 'Salary Payment - Jane Smith',
        amount: 4200.00,
        status: 'completed',
        bankAccount: { id: 'bank_123', name: 'Main Business Account' },
        employee: { id: 'emp_124', name: 'Jane Smith' },
        destinationAccount: { 
          id: 'dest_124', 
          maskedNumber: '****5678',
          bankName: 'Bank of America',
          accountType: 'savings'
        },
        notes: 'Regular monthly salary payment',
      },
    ];
    
    const transactions = ref<any[]>([]);
    
    const snackbar = ref({
      show: false,
      message: '',
      color: 'success',
    });
    
    const pagination = ref({
      page: 1,
      itemsPerPage: 10,
      totalItems: 0,
      sortBy: ['date'],
      sortDesc: [true],
    });
    
    const headers = [
      { 
        title: 'Date', 
        key: 'date', 
        sortable: true,
        width: '140px',
      },
      { 
        title: 'Reference', 
        key: 'reference', 
        sortable: true,
        width: '160px',
      },
      { 
        title: 'Description', 
        key: 'description', 
        sortable: true,
        minWidth: '200px',
      },
      { 
        title: 'Amount', 
        key: 'amount', 
        sortable: true, 
        align: 'end',
        width: '150px',
      },
      { 
        title: 'Status', 
        key: 'status', 
        sortable: true, 
        width: '160px',
        filterable: true,
      },
      { 
        title: '', 
        key: 'actions', 
        sortable: false, 
        align: 'end', 
        width: '140px',
      },
    ];
    
    // Computed properties for summary cards
    const formattedTotalTransactions = computed(() => {
      return transactions.value.length.toLocaleString();
    });
    
    const totalAmount = computed(() => {
      return transactions.value.reduce((sum, txn) => sum + txn.amount, 0);
    });
    
    const employeesPaid = computed(() => {
      const uniqueEmployees = new Set(transactions.value.map(txn => txn.employee?.id).filter(Boolean));
      return uniqueEmployees.size;
    });
    
    const pendingActions = computed(() => {
      return transactions.value.filter(txn => 
        ['pending', 'processing'].includes(txn.status)
      ).length;
    });
    
    // Filter transactions based on search, status filter, and date range
    const filteredTransactions = computed(() => {
      let result = [...transactions.value];
      
      // Apply search filter
      if (search.value) {
        const searchTerm = search.value.toLowerCase();
        result = result.filter(transaction => 
          transaction.reference?.toLowerCase().includes(searchTerm) ||
          transaction.description?.toLowerCase().includes(searchTerm) ||
          transaction.employee?.name?.toLowerCase().includes(searchTerm) ||
          transaction.status?.toLowerCase().includes(searchTerm)
        );
      }
      
      // Apply status filter
      if (statusFilter.value) {
        result = result.filter(transaction => 
          transaction.status === statusFilter.value
        );
      }
      
      // Apply date range filter (simplified example)
      if (dateRange.value) {
        const now = new Date();
        let fromDate = new Date();
        
        switch (dateRange.value) {
          case 'today':
            fromDate.setHours(0, 0, 0, 0);
            break;
          case 'week':
            fromDate.setDate(now.getDate() - 7);
            break;
          case 'month':
            fromDate.setMonth(now.getMonth() - 1);
            break;
          case 'year':
            fromDate.setFullYear(now.getFullYear() - 1);
            break;
        }
        
        result = result.filter(transaction => {
          const txnDate = new Date(transaction.date);
          return txnDate >= fromDate;
        });
      }
      
      return result;
    });
    
    const formatDate = (date: string | Date) => {
      if (!date) return 'N/A';
      return format(typeof date === 'string' ? parseISO(date) : date, 'MMM d, yyyy');
    };
    
    const formatDateTime = (date: string | Date) => {
      if (!date) return 'N/A';
      return format(
        typeof date === 'string' ? parseISO(date) : date, 
        'MMM d, yyyy h:mm a'
      );
    };
    
    const formatCurrency = (amount: number) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
      }).format(Math.abs(amount));
    };
    
    const formatStatus = (status: string) => {
      return status.charAt(0).toUpperCase() + status.slice(1);
    };
    
    const getStatusColor = (status: TransactionStatus) => {
      const colors: Record<TransactionStatus, string> = {
        pending: 'warning',
        processing: 'info',
        completed: 'success',
        failed: 'error',
        cancelled: 'grey',
      };
      return colors[status] || 'grey';
    };
    
    const getStatusIcon = (status: TransactionStatus) => {
      const icons: Record<TransactionStatus, string> = {
        pending: 'mdi-clock-time-eight-outline',
        processing: 'mdi-progress-clock',
        completed: 'mdi-check-circle-outline',
        failed: 'mdi-alert-circle-outline',
        cancelled: 'mdi-cancel',
      };
      return icons[status] || 'mdi-help-circle-outline';
    };
    
    const fetchTransactions = async () => {
      if (props.status !== 'paid') {
        transactions.value = [];
        return;
      }
      
      try {
        loading.value = true;
        // TODO: Replace with actual API call
        // const response = await payrollService.getPayRunTransactions(props.payrunId, {
        //   page: pagination.value.page,
        //   limit: pagination.value.itemsPerPage,
        //   sortBy: pagination.value.sortBy[0],
        //   sortOrder: pagination.value.sortDesc[0] ? 'desc' : 'asc',
        // });
        // 
        // transactions.value = response.data;
        // pagination.value.totalItems = response.total;
        
        // Use mock data for now
        transactions.value = [...mockTransactions];
        pagination.value.totalItems = transactions.value.length;
      } catch (error) {
        console.error('Error fetching transactions:', error);
        showSnackbar('Failed to load transactions', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const initiateBankTransfer = async () => {
      if (!confirm('Are you sure you want to initiate bank transfers for this pay run?')) {
        return;
      }
      
      try {
        processing.value = true;
        // TODO: Replace with actual API call
        // await payrollService.initiateBankTransfer(props.payrunId);
        showSnackbar('Bank transfers initiated successfully', 'success');
        fetchTransactions();
      } catch (error) {
        console.error('Error initiating bank transfer:', error);
        showSnackbar('Failed to initiate bank transfers', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const exportTransactions = async () => {
      try {
        exporting.value = true;
        // TODO: Replace with actual API call
        // const blob = await payrollService.exportPayRunTransactions(props.payrunId, 'csv');
        // 
        // // Create a download link
        // const url = window.URL.createObjectURL(blob);
        // const link = document.createElement('a');
        // link.href = url;
        // link.setAttribute('download', `transactions-${props.payrunId}.csv`);
        // document.body.appendChild(link);
        // link.click();
        // link.remove();
        
        showSnackbar('Export functionality will be implemented soon', 'info');
      } catch (error) {
        console.error('Error exporting transactions:', error);
        showSnackbar('Failed to export transactions', 'error');
      } finally {
        exporting.value = false;
      }
    };
    
    const viewTransactionDetails = (transactionId: string) => {
      const transaction = transactions.value.find(t => t.id === transactionId);
      if (transaction) {
        selectedTransaction.value = { ...transaction };
        showTransactionDialog.value = true;
      }
    };
    
    const downloadReceipt = async (transactionId: string) => {
      try {
        // Set loading state for this specific receipt
        downloadingReceipts.value = { 
          ...downloadingReceipts.value, 
          [transactionId]: true 
        };
        
        // TODO: Replace with actual API call
        // const blob = await payrollService.downloadTransactionReceipt(transactionId);
        // 
        // // Create a download link
        // const url = window.URL.createObjectURL(blob);
        // const link = document.createElement('a');
        // link.href = url;
        // link.setAttribute('download', `receipt-${transactionId}.pdf`);
        // document.body.appendChild(link);
        // link.click();
        // link.remove();
        
        // Mock success for now
        showSnackbar('Receipt downloaded successfully', 'success');
      } catch (error) {
        console.error('Error downloading receipt:', error);
        showSnackbar('Failed to download receipt', 'error');
      } finally {
        // Clear loading state
        downloadingReceipts.value = { 
          ...downloadingReceipts.value, 
          [transactionId]: false 
        };
      }
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
      
      fetchTransactions();
    };
    
    const showSnackbar = (message: string, color: 'success' | 'error' | 'info' | 'warning') => {
      snackbar.value = {
        show: true,
        message,
        color,
      };
    };
    
    // Watch for changes in the payrunId or status props
    watch(
      [() => props.payrunId, () => props.status],
      () => {
        fetchTransactions();
      },
      { immediate: true }
    );
    
    // Additional methods for new UI elements
    const copyTransactionLink = (transactionId: string) => {
      const url = `${window.location.origin}/payroll/transactions/${transactionId}`;
      copy(url);
      showSnackbar('Transaction link copied to clipboard', 'success');
    };
    
    const exportTransaction = async (transaction: Transaction) => {
      try {
        exporting.value = true;
        // TODO: Implement export functionality
        showSnackbar('Export functionality will be implemented soon', 'info');
      } catch (error) {
        console.error('Error exporting transaction:', error);
        showSnackbar('Failed to export transaction', 'error');
      } finally {
        exporting.value = false;
      }
    };
    
    const cancelTransaction = async (transactionId: string) => {
      if (!confirm('Are you sure you want to cancel this transaction?')) {
        return;
      }
      
      try {
        // TODO: Implement cancel transaction
        // await payrollService.cancelTransaction(transactionId);
        showSnackbar('Transaction cancelled successfully', 'success');
        fetchTransactions();
      } catch (error) {
        console.error('Error cancelling transaction:', error);
        showSnackbar('Failed to cancel transaction', 'error');
      }
    };

    return {
      // Refs
      loading,
      processing,
      exporting,
      search,
      statusFilter,
      statusOptions,
      dateRange,
      showTransactionDialog,
      selectedTransaction,
      downloadingReceipts,
      transactions,
      snackbar,
      pagination,
      
      // Computed
      headers,
      filteredTransactions,
      formattedTotalTransactions,
      totalAmount,
      employeesPaid,
      pendingActions,
      
      // Methods
      formatDate,
      formatDateTime,
      formatCurrency,
      formatStatus,
      getStatusColor,
      getStatusIcon,
      initiateBankTransfer,
      exportTransactions,
      viewTransactionDetails,
      downloadReceipt,
      onTableOptionsChange,
      copyTransactionLink,
      exportTransaction,
      cancelTransaction,
    };
  },
});
</script>

<style scoped>
.transactions-tab {
  width: 100%;
}

.v-list-item {
  min-height: 40px;
}

/* Status colors */
.text-error {
  color: #f44336;
}

.text-success {
  color: #4caf50;
}

.text-warning {
  color: #ff9800;
}

.text-info {
  color: #2196f3;
}

/* Table styles */
.v-data-table {
  --v-theme-surface: transparent;
}

.v-data-table :deep(.v-data-table__td) {
  height: 60px;
  vertical-align: middle;
}

.v-data-table :deep(.v-data-table__th) {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  color: rgba(var(--v-theme-on-surface), var(--v-medium-emphasis-opacity));
}

.v-data-table :deep(.v-data-table__tr--hover) {
  background: rgba(var(--v-theme-primary), 0.04) !important;
}

/* Card styles */
.v-card {
  transition: box-shadow 0.2s ease-in-out;
}

.v-card:hover {
  box-shadow: 0 8px 30px -12px rgba(0, 0, 0, 0.12) !important;
}

/* Summary cards */
.summary-card {
  border-left: 4px solid;
  transition: transform 0.2s ease-in-out;
}

.summary-card:hover {
  transform: translateY(-2px);
}

/* Status chips */
.v-chip--size-small {
  font-weight: 500;
  letter-spacing: 0.3px;
}

/* Action buttons */
.v-btn--icon.v-btn--density-default {
  width: 32px;
  height: 32px;
}

/* Empty state */
.empty-state {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  text-align: center;
  padding: 2rem;
  color: rgba(var(--v-theme-on-surface), var(--v-disabled-opacity));
}

/* Responsive adjustments */
@media (max-width: 959px) {
  .v-data-table :deep(.v-data-table__td),
  .v-data-table :deep(.v-data-table__th) {
    padding: 0 8px;
  }
  
  .v-data-table :deep(.v-data-table__td:first-child),
  .v-data-table :deep(.v-data-table__th:first-child) {
    padding-left: 16px;
  }
  
  .v-data-table :deep(.v-data-table__td:last-child),
  .v-data-table :deep(.v-data-table__th:last-child) {
    padding-right: 16px;
  }
}

/* Animation for status changes */
@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.status-pending,
.status-processing {
  animation: pulse 2s infinite;
}

/* Print styles */
@media print {
  .no-print {
    display: none !important;
  }
  
  .v-data-table {
    width: 100% !important;
  }
  
  .v-data-table :deep(table) {
    width: 100% !important;
  }
}
</style>
