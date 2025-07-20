<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Approve Pay Run</span>
            <v-chip :color="payRun.status === 'pending_approval' ? 'warning' : 'success'" size="small">
              {{ formatStatus(payRun.status) }}
            </v-chip>
          </v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-list>
                  <v-list-item>
                    <template v-slot:prepend><v-icon icon="mdi-format-title" class="me-4"></v-icon></template>
                    <v-list-item-title>Pay Run ID</v-list-item-title>
                    <v-list-item-subtitle>{{ payRun.id }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <template v-slot:prepend><v-icon icon="mdi-calendar-range" class="me-4"></v-icon></template>
                    <v-list-item-title>Pay Period</v-list-item-title>
                    <v-list-item-subtitle>{{ formatDate(payRun.start_date) }} - {{ formatDate(payRun.end_date) }}</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-card variant="outlined" class="mb-4">
                  <v-card-text>
                    <div class="text-h6 mb-4">Summary</div>
                    <v-table density="compact">
                      <tbody>
                        <tr><td>Total Gross Pay</td><td class="text-right">{{ formatCurrency(payRun.total_gross) }}</td></tr>
                        <tr><td>Total Deductions</td><td class="text-right">{{ formatCurrency(payRun.total_deductions) }}</td></tr>
                        <tr><td>Total Net Pay</td><td class="text-right font-weight-bold">{{ formatCurrency(payRun.total_net) }}</td></tr>
                      </tbody>
                    </v-table>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            
            <v-divider class="my-4"></v-divider>
            
            <div class="d-flex justify-space-between align-center mb-4">
              <h3>Employee Payments</h3>
              <v-text-field v-model="search" append-inner-icon="mdi-magnify" label="Search" single-line hide-details density="compact" variant="outlined" class="shrink"></v-text-field>
            </div>
            
            <v-data-table :items="payRun.employee_payments || []" :search="search" :loading="loading" loading-text="Loading employee payments..." class="elevation-1" density="comfortable" :headers="headers">
              <template v-slot:item.employee="{ item }">
                <div class="d-flex align-center">
                  <v-avatar size="32" color="primary" class="me-2">
                    <span class="text-white">{{ getInitials(item.employee_name) }}</span>
                  </v-avatar>
                  <div>
                    <div class="font-weight-medium">{{ item.employee_name }}</div>
                    <div class="text-caption text-medium-emphasis">{{ item.employee_id }}</div>
                  </div>
                </div>
              </template>
              
              <template v-slot:item.gross_pay="{ item }">{{ formatCurrency(item.gross_pay) }}</template>
              <template v-slot:item.deductions="{ item }">{{ formatCurrency(item.deductions) }}</template>
              <template v-slot:item.net_pay="{ item }"><span class="font-weight-medium">{{ formatCurrency(item.net_pay) }}</span></template>
              
              <template v-slot:no-data>
                <div class="py-4 text-center">No employee payments found</div>
              </template>
            </v-data-table>
          </v-card-text>
          
          <v-card-actions class="pa-4">
            <v-spacer></v-spacer>
            <v-btn color="secondary" variant="text" @click="$router.go(-1)">Back</v-btn>
            <v-btn v-if="payRun.status === 'pending_approval'" color="error" variant="tonal" :loading="rejecting" @click="rejectPayRun">Reject</v-btn>
            <v-btn v-if="payRun.status === 'pending_approval'" color="primary" :loading="approving" @click="approvePayRun">Approve Pay Run</v-btn>
            <v-btn v-else color="primary" @click="$router.push({ name: 'payroll-runs' })">Back to Pay Runs</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    
    <v-dialog v-model="rejectDialog" max-width="500">
      <v-card>
        <v-card-title>Reject Pay Run</v-card-title>
        <v-card-text>
          <v-textarea v-model="rejectReason" label="Reason for rejection" rows="3" variant="outlined" :rules="[v => !!v || 'Please provide a reason for rejection']" required></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" variant="text" @click="rejectDialog = false">Cancel</v-btn>
          <v-btn color="error" :loading="rejecting" @click="confirmReject">Confirm Rejection</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <v-dialog v-model="successDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h5">
          <v-icon icon="mdi-check-circle" color="success" size="large" class="me-2"></v-icon>
          {{ successMessage }}
        </v-card-title>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="handleSuccess">OK</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export default defineComponent({
  name: 'PayRunApproveView',
  
  props: {
    id: { type: String, required: true }
  },
  
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    
    const loading = ref(true);
    const approving = ref(false);
    const rejecting = ref(false);
    const rejectDialog = ref(false);
    const rejectReason = ref('');
    const successDialog = ref(false);
    const successMessage = ref('');
    const search = ref('');
    
    const payRun = ref({
      id: '',
      pay_period: '',
      start_date: new Date(),
      end_date: new Date(),
      status: 'draft',
      total_gross: 0,
      total_deductions: 0,
      total_net: 0,
      notes: '',
      employee_count: 0,
      employee_payments: []
    });
    
    const headers = [
      { title: 'Employee', key: 'employee', sortable: true },
      { title: 'Department', key: 'department', sortable: true },
      { title: 'Gross Pay', key: 'gross_pay', align: 'end', sortable: true },
      { title: 'Deductions', key: 'deductions', align: 'end', sortable: true },
      { title: 'Net Pay', key: 'net_pay', align: 'end', sortable: true },
      { title: 'Status', key: 'status', sortable: true }
    ];
    
    // Mock data - replace with API call
    const fetchPayRun = () => {
      loading.value = true;
      setTimeout(() => {
        payRun.value = {
          id: props.id || 'PR-2023-08-001',
          pay_period: 'Bi-weekly',
          start_date: new Date('2023-08-01'),
          end_date: new Date('2023-08-15'),
          status: route.query.status === 'approved' ? 'approved' : 'pending_approval',
          total_gross: 125000,
          total_deductions: 25000,
          total_net: 100000,
          notes: 'Includes overtime for all employees working on the Q3 project.',
          employee_count: 87,
          employee_payments: Array.from({ length: 10 }, (_, i) => ({
            id: `EMP-${1000 + i}`,
            employee_id: `EMP-${1000 + i}`,
            employee_name: `Employee ${i + 1}`,
            department: ['Sales', 'Marketing', 'Engineering', 'HR', 'Finance'][i % 5],
            gross_pay: 5000 + (i * 200),
            deductions: 1000 + (i * 50),
            net_pay: 4000 + (i * 150),
            status: 'pending_approval'
          }))
        };
        loading.value = false;
      }, 500);
    };
    
    const formatCurrency = (value: number) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
    };
    
    const formatDate = (date: Date | string) => {
      if (!date) return '';
      const d = new Date(date);
      return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    };
    
    const formatStatus = (status: string) => {
      const statusMap: Record<string, string> = {
        draft: 'Draft',
        pending_approval: 'Pending Approval',
        approved: 'Approved',
        processed: 'Processed',
        paid: 'Paid',
        rejected: 'Rejected',
        cancelled: 'Cancelled'
      };
      return statusMap[status] || status;
    };
    
    const getInitials = (name: string) => {
      if (!name) return '??';
      return name.split(' ').map(part => part[0]).join('').toUpperCase().substring(0, 2);
    };
    
    const approvePayRun = () => {
      approving.value = true;
      setTimeout(() => {
        payRun.value.status = 'approved';
        successMessage.value = 'Pay run approved successfully!';
        successDialog.value = true;
        approving.value = false;
      }, 1000);
    };
    
    const rejectPayRun = () => {
      rejectDialog.value = true;
    };
    
    const confirmReject = () => {
      if (!rejectReason.value.trim()) return;
      
      rejecting.value = true;
      setTimeout(() => {
        payRun.value.status = 'rejected';
        successMessage.value = 'Pay run has been rejected.';
        successDialog.value = true;
        rejectDialog.value = false;
        rejecting.value = false;
        rejectReason.value = '';
      }, 1000);
    };
    
    const handleSuccess = () => {
      successDialog.value = false;
      router.push({ name: 'payroll-runs' });
    };
    
    onMounted(() => {
      fetchPayRun();
    });
    
    return {
      loading,
      approving,
      rejecting,
      rejectDialog,
      rejectReason,
      successDialog,
      successMessage,
      search,
      payRun,
      headers,
      formatCurrency,
      formatDate,
      formatStatus,
      getInitials,
      approvePayRun,
      rejectPayRun,
      confirmReject,
      handleSuccess
    };
  }
});
</script>
