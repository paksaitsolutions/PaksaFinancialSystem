<template>
  <div class="payslips-tab">
    <v-card variant="flat">
      <v-card-actions class="px-4 py-3">
        <v-text-field
          v-model="search"
          label="Search employees"
          prepend-inner-icon="mdi-magnify"
          variant="outlined"
          density="compact"
          hide-details
          clearable
          class="mr-2"
          style="max-width: 300px;"
        />
        <v-spacer />
        <v-btn
          color="primary"
          variant="tonal"
          prepend-icon="mdi-file-pdf-box"
          @click="exportAllPayslips"
          :loading="exportingAll"
          :disabled="!payslips.length"
        >
          Export All
        </v-btn>
      </v-card-actions>
      
      <v-data-table
        :headers="headers"
        :items="filteredPayslips"
        :loading="loading"
        :items-per-page="pagination.itemsPerPage"
        :page="pagination.page"
        :items-length="pagination.totalItems"
        :server-items-length="pagination.totalItems"
        :items-per-page-options="[10, 25, 50]"
        @update:options="onTableOptionsChange"
        class="elevation-1"
      >
        <template v-slot:item.employee="{ item }">
          <div class="d-flex align-center">
            <v-avatar size="36" class="mr-2">
              <v-img :src="item.employee.avatar" :alt="item.employee.name" />
            </v-avatar>
            <div>
              <div class="font-weight-medium">{{ item.employee.name }}</div>
              <div class="text-caption text-medium-emphasis">{{ item.employee.employeeId }}</div>
            </div>
          </div>
        </template>
        
        <template v-slot:item.netPay="{ item }">
          {{ formatCurrency(item.netPay) }}
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
          <v-btn
            icon
            variant="text"
            size="small"
            color="primary"
            :to="{ name: 'payroll-payslips-view', params: { id: item.id } }"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          <v-btn
            icon
            variant="text"
            size="small"
            color="secondary"
            @click="exportPayslip(item.id)"
            :loading="exportingPayslips[item.id]"
          >
            <v-icon>mdi-download</v-icon>
          </v-btn>
        </template>
        
        <template v-slot:no-data>
          <div class="py-4 text-medium-emphasis">
            No payslips found for this pay run.
          </div>
        </template>
      </v-data-table>
    </v-card>
    
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
import { useRouter } from 'vue-router';
import { format } from 'date-fns';
import { payrollService } from '@/services/payroll/payrollService';
import type { Payslip } from '@/services/payroll/types';

export default defineComponent({
  name: 'PayRunPayslipsTab',
  
  props: {
    payrunId: {
      type: String,
      required: true,
    },
    employeeCount: {
      type: Number,
      default: 0,
    },
    referenceNumber: {
      type: String,
      default: '',
    },
  },
  
  setup(props) {
    const router = useRouter();
    
    const loading = ref(false);
    const exportingAll = ref(false);
    const exportingPayslips = ref<Record<string, boolean>>({});
    const search = ref('');
    
    const payslips = ref<Payslip[]>([]);
    
    const snackbar = ref({
      show: false,
      message: '',
      color: 'success',
    });
    
    const pagination = ref({
      page: 1,
      itemsPerPage: 10,
      totalItems: 0,
      sortBy: ['employee.name'],
      sortDesc: [false],
    });
    
    const headers = [
      { title: 'Employee', key: 'employee', sortable: true },
      { title: 'Net Pay', key: 'netPay', sortable: true, align: 'end' },
      { title: 'Status', key: 'status', sortable: true, width: '150px' },
      { title: 'Actions', key: 'actions', sortable: false, align: 'end', width: '120px' },
    ];
    
    const filteredPayslips = computed(() => {
      if (!search.value) return payslips.value;
      
      const searchTerm = search.value.toLowerCase();
      return payslips.value.filter(payslip => 
        payslip.employee.name.toLowerCase().includes(searchTerm) ||
        payslip.employee.employeeId?.toLowerCase().includes(searchTerm) ||
        payslip.employee.email?.toLowerCase().includes(searchTerm)
      );
    });
    
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
    
    const fetchPayslips = async () => {
      try {
        loading.value = true;
        const response = await payrollService.getPayslips({
          payRunId: props.payrunId,
          page: pagination.value.page,
          limit: pagination.value.itemsPerPage,
          sortBy: pagination.value.sortBy[0],
          sortOrder: pagination.value.sortDesc[0] ? 'desc' : 'asc',
        });
        
        payslips.value = response.data;
        pagination.value.totalItems = response.total;
      } catch (error) {
        console.error('Error fetching payslips:', error);
        showSnackbar('Failed to load payslips', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const exportPayslip = async (payslipId: string) => {
      try {
        // Set loading state for this specific payslip
        exportingPayslips.value = { ...exportingPayslips.value, [payslipId]: true };
        
        const blob = await payrollService.generatePayslipPdf(payslipId);
        
        // Create a download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        // Find the payslip to get the employee name for the filename
        const payslip = payslips.value.find(p => p.id === payslipId);
        const employeeName = payslip?.employee?.name?.replace(/\s+/g, '-').toLowerCase() || 'payslip';
        link.setAttribute('download', `payslip-${employeeName}.pdf`);
        
        document.body.appendChild(link);
        link.click();
        link.remove();
        
        showSnackbar('Payslip exported successfully', 'success');
      } catch (error) {
        console.error('Error exporting payslip:', error);
        showSnackbar('Failed to export payslip', 'error');
      } finally {
        // Clear loading state
        exportingPayslips.value = { ...exportingPayslips.value, [payslipId]: false };
      }
    };
    
    const exportAllPayslips = async () => {
      try {
        exportingAll.value = true;
        
        const blob = await payrollService.generatePayslipsZip(props.payrunId);
        
        // Create a download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `payslips-${props.referenceNumber || props.payrunId}.zip`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        
        showSnackbar('All payslips exported successfully', 'success');
      } catch (error) {
        console.error('Error exporting all payslips:', error);
        showSnackbar('Failed to export payslips', 'error');
      } finally {
        exportingAll.value = false;
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
      
      fetchPayslips();
    };
    
    const showSnackbar = (message: string, color: 'success' | 'error' | 'info' | 'warning') => {
      snackbar.value = {
        show: true,
        message,
        color,
      };
    };
    
    // Initial data load
    onMounted(() => {
      fetchPayslips();
    });
    
    // Watch for changes in the payrunId prop
    watch(() => props.payrunId, (newVal, oldVal) => {
      if (newVal !== oldVal) {
        fetchPayslips();
      }
    });
    
    return {
      // Refs
      loading,
      exportingAll,
      exportingPayslips,
      search,
      payslips,
      snackbar,
      pagination,
      // Computed
      headers,
      filteredPayslips,
      // Methods
      formatCurrency,
      formatStatus,
      getStatusColor,
      exportPayslip,
      exportAllPayslips,
      onTableOptionsChange,
    };
  },
});
</script>

<style scoped>
.payslips-tab {
  width: 100%;
}
</style>
