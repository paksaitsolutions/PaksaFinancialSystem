<template>
  <div class="payrun-view">
    <v-breadcrumbs :items="breadcrumbs" class="px-0 py-4" />
    
    <v-card v-if="payrun" class="mb-6">
      <v-card-title class="d-flex align-center">
        <span class="text-h5">Pay Run #{{ payrun.referenceNumber || payrun.id }}</span>
        <v-chip class="ml-4" :color="getStatusColor(payrun.status)" size="small" :text="formatStatus(payrun.status)" />
        <v-spacer />
        <v-btn
          v-if="canEdit"
          color="primary"
          variant="tonal"
          class="mr-2"
          :to="{ name: 'payroll-payruns-edit', params: { id: payrun.id } }"
          prepend-icon="mdi-pencil"
        >
          Edit
        </v-btn>
        <v-menu>
          <template v-slot:activator="{ props }">
            <v-btn
              color="secondary"
              variant="tonal"
              v-bind="props"
              prepend-icon="mdi-dots-vertical"
            >
              Actions
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="processPayRun" v-if="payrun.status === 'draft'" :disabled="processing">
              <template v-slot:prepend>
                <v-icon>mdi-cog</v-icon>
              </template>
              <v-list-item-title>Process Pay Run</v-list-item-title>
            </v-list-item>
            <v-list-item @click="exportPayRun" :disabled="exporting">
              <template v-slot:prepend>
                <v-icon>mdi-file-export</v-icon>
              </template>
              <v-list-item-title>Export</v-list-item-title>
            </v-list-item>
            <v-divider v-if="payrun.status === 'draft'" />
            <v-list-item
              v-if="payrun.status === 'draft'"
              @click="confirmDelete"
              color="error"
            >
              <template v-slot:prepend>
                <v-icon>mdi-delete</v-icon>
              </template>
              <v-list-item-title>Delete</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12" md="4">
            <v-list density="compact" class="transparent">
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-calendar-range</v-icon>
                </template>
                <v-list-item-title>Pay Period</v-list-item-title>
                <v-list-item-subtitle class="text-right">
                  {{ formatDateRange(payrun.payPeriodStartDate, payrun.payPeriodEndDate) }}
                </v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-calendar-check</v-icon>
                </template>
                <v-list-item-title>Payment Date</v-list-item-title>
                <v-list-item-subtitle class="text-right">
                  {{ formatDate(payrun.paymentDate) }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-col>
          <v-col cols="12" md="4">
            <v-list density="compact" class="transparent">
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-account-group</v-icon>
                </template>
                <v-list-item-title>Employees</v-list-item-title>
                <v-list-item-subtitle class="text-right">
                  {{ payrun.employeeCount || 0 }}
                </v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-cash-multiple</v-icon>
                </template>
                <v-list-item-title>Total Amount</v-list-item-title>
                <v-list-item-subtitle class="text-right font-weight-bold">
                  {{ formatCurrency(payrun.totalAmount || 0) }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-col>
          <v-col cols="12" md="4">
            <v-list density="compact" class="transparent">
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-account</v-icon>
                </template>
                <v-list-item-title>Created By</v-list-item-title>
                <v-list-item-subtitle class="text-right">
                  {{ payrun.createdBy?.name || 'System' }}
                </v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <template v-slot:prepend>
                  <v-icon>mdi-clock-outline</v-icon>
                </template>
                <v-list-item-title>Created At</v-list-item-title>
                <v-list-item-subtitle class="text-right">
                  {{ formatDateTime(payrun.createdAt) }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>

        <v-divider class="my-4" />

        <v-tabs v-model="activeTab" grow>
          <v-tab value="payslips">
            <v-icon start>mdi-file-document-multiple</v-icon>
            Payslips ({{ payrun.employeeCount || 0 }})
          </v-tab>
          <v-tab value="summary">
            <v-icon start>mdi-chart-box</v-icon>
            Summary
          </v-tab>
          <v-tab value="transactions">
            <v-icon start>mdi-bank-transfer</v-icon>
            Bank Transactions
          </v-tab>
          <v-tab value="journal" v-if="payrun.journalEntryId">
            <v-icon start>mdi-book-open-variant</v-icon>
            Journal Entry
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="payslips">
            <PayRunPayslipsTab 
              :payrun-id="payrun.id" 
              :employee-count="payrun.employeeCount || 0"
              :reference-number="payrun.referenceNumber || payrun.id"
            />
          </v-window-item>
          
          <v-window-item value="summary">
            <PayRunSummaryTab 
              :earnings-summary="payrun.earningsSummary || {}}" 
              :deductions-summary="payrun.deductionsSummary || {}}"
              :total-earnings="payrun.totalEarnings || 0"
              :total-deductions="payrun.totalDeductions || 0"
              :total-net-pay="payrun.totalNetPay || 0"
            />
          </v-window-item>
          
          <v-window-item value="transactions">
            <PayRunTransactionsTab 
              :payrun-id="payrun.id" 
              :status="payrun.status"
            />
          </v-window-item>
          
          <v-window-item value="journal" v-if="payrun.journalEntryId">
            <PayRunJournalTab 
              :journal-entry-id="payrun.journalEntryId"
            />
          </v-window-item>
        </v-window>
      </v-card-text>
    </v-card>
    
    <v-dialog v-model="confirmDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6">Confirm Delete</v-card-title>
        <v-card-text>
          Are you sure you want to delete this pay run? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn
            color="secondary"
            variant="text"
            @click="confirmDialog = false"
            :disabled="deleting"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="elevated"
            @click="deletePayRun"
            :loading="deleting"
          >
            Delete
          </v-btn>
        </v-card-actions>
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
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { format, parseISO } from 'date-fns';
import { payrollService } from '@/services/payroll/payrollService';
import type { PayRun, PayRunStatus } from '@/services/payroll/types';
import PayRunPayslipsTab from './tabs/PayRunPayslipsTab.vue';
import PayRunSummaryTab from './tabs/PayRunSummaryTab.vue';
import PayRunTransactionsTab from './tabs/PayRunTransactionsTab.vue';
import PayRunJournalTab from './tabs/PayRunJournalTab.vue';

export default defineComponent({
  name: 'PayRunView',
  
  components: {
    PayRunPayslipsTab,
    PayRunSummaryTab,
    PayRunTransactionsTab,
    PayRunJournalTab,
  },
  
  props: {
    id: {
      type: String,
      required: true,
    },
  },
  
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    
    const loading = ref(true);
    const processing = ref(false);
    const exporting = ref(false);
    const deleting = ref(false);
    const confirmDialog = ref(false);
    
    const payrun = ref<PayRun | null>(null);
    const activeTab = ref('payslips');
    
    const snackbar = ref({
      show: false,
      message: '',
      color: 'success',
    });
    
    const breadcrumbs = computed(() => [
      { title: 'Dashboard', to: { name: 'dashboard' } },
      { title: 'Payroll', to: { name: 'payroll' } },
      { title: 'Pay Runs', to: { name: 'payroll-payruns' } },
      { 
        title: payrun.value?.referenceNumber 
          ? `Pay Run #${payrun.value.referenceNumber}` 
          : 'Pay Run Details' 
      },
    ]);
    
    const canEdit = computed(() => {
      return payrun.value?.status === 'draft' || payrun.value?.status === 'processing';
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
    
    const formatDateRange = (startDate: string, endDate: string) => {
      if (!startDate || !endDate) return 'N/A';
      const start = format(parseISO(startDate), 'MMM d, yyyy');
      const end = format(parseISO(endDate), 'MMM d, yyyy');
      return `${start} - ${end}`;
    };
    
    const formatCurrency = (amount: number) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
      }).format(amount);
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
    
    const fetchPayRun = async () => {
      try {
        loading.value = true;
        const response = await payrollService.getPayRun(props.id);
        payrun.value = response;
        
        // If pay run is not found, redirect to list
        if (!payrun.value) {
          router.push({ name: 'payroll-payruns' });
          return;
        }
      } catch (error) {
        console.error('Error fetching pay run:', error);
        showSnackbar('Failed to load pay run details', 'error');
        router.push({ name: 'payroll-payruns' });
      } finally {
        loading.value = false;
      }
    };
    
    const processPayRun = async () => {
      if (!payrun.value) return;
      
      try {
        processing.value = true;
        const response = await payrollService.processPayRun(payrun.value.id);
        payrun.value = response;
        showSnackbar('Pay run processed successfully', 'success');
      } catch (error) {
        console.error('Error processing pay run:', error);
        showSnackbar('Failed to process pay run', 'error');
      } finally {
        processing.value = false;
      }
    };
    
    const exportPayRun = async () => {
      if (!payrun.value) return;
      
      try {
        exporting.value = true;
        const blob = await payrollService.generatePayRunReport(payrun.value.id, 'pdf');
        
        // Create a download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `payrun-${payrun.value.referenceNumber || payrun.value.id}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        
        showSnackbar('Pay run exported successfully', 'success');
      } catch (error) {
        console.error('Error exporting pay run:', error);
        showSnackbar('Failed to export pay run', 'error');
      } finally {
        exporting.value = false;
      }
    };
    
    const confirmDelete = () => {
      confirmDialog.value = true;
    };
    
    const deletePayRun = async () => {
      if (!payrun.value) return;
      
      try {
        deleting.value = true;
        await payrollService.deletePayRun(payrun.value.id);
        showSnackbar('Pay run deleted successfully', 'success');
        router.push({ name: 'payroll-payruns' });
      } catch (error) {
        console.error('Error deleting pay run:', error);
        showSnackbar('Failed to delete pay run', 'error');
      } finally {
        deleting.value = false;
        confirmDialog.value = false;
      }
    };
    
    const showSnackbar = (message: string, color: 'success' | 'error' | 'info' | 'warning') => {
      snackbar.value = {
        show: true,
        message,
        color,
      };
    };
    
    // Watch for route changes to update the active tab
    watch(() => route.hash, (newHash) => {
      if (newHash) {
        const tab = newHash.replace('#', '');
        if (['payslips', 'summary', 'transactions', 'journal'].includes(tab)) {
          activeTab.value = tab;
        }
      }
    }, { immediate: true });
    
    // Initial data load
    onMounted(() => {
      fetchPayRun();
    });
    
    return {
      // Refs
      loading,
      processing,
      exporting,
      deleting,
      confirmDialog,
      payrun,
      activeTab,
      snackbar,
      // Computed
      breadcrumbs,
      canEdit,
      // Methods
      formatDate,
      formatDateTime,
      formatDateRange,
      formatCurrency,
      formatStatus,
      getStatusColor,
      processPayRun,
      exportPayRun,
      confirmDelete,
      deletePayRun,
    };
  },
});
</script>

<style scoped>
.payrun-view {
  padding: 20px;
}

.v-breadcrumbs {
  padding: 0;
}
</style>
