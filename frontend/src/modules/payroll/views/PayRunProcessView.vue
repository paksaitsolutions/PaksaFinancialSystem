<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Process Pay Run</span>
            <v-chip :color="getStatusColor(payRun.status)" size="small">
              {{ formatStatus(payRun.status) }}
            </v-chip>
          </v-card-title>
          
          <v-stepper v-model="currentStep" class="elevation-0">
            <v-stepper-header>
              <v-stepper-item :value="1" :complete="currentStep > 1" title="Review"></v-stepper-item>
              <v-divider></v-divider>
              <v-stepper-item :value="2" :complete="currentStep > 2" title="Calculate"></v-stepper-item>
              <v-divider></v-divider>
              <v-stepper-item :value="3" :complete="currentStep > 3" title="Approve"></v-stepper-item>
              <v-divider></v-divider>
              <v-stepper-item :value="4" title="Complete"></v-stepper-item>
            </v-stepper-header>
            
            <v-stepper-window>
              <!-- Step 1: Review -->
              <v-stepper-window-item :value="1">
                <v-card-text>
                  <v-alert type="info" variant="tonal" class="mb-4" icon="mdi-information">
                    Review the pay run details before processing. Make sure all employee data is accurate.
                  </v-alert>
                  
                  <v-row>
                    <v-col cols="12" md="6">
                      <v-card variant="outlined" class="mb-4">
                        <v-card-text>
                          <div class="text-h6 mb-4">Pay Run Details</div>
                          <v-list density="compact" class="bg-transparent">
                            <v-list-item>
                              <v-list-item-title>Pay Run ID</v-list-item-title>
                              <v-list-item-subtitle class="text-right">{{ payRun.id }}</v-list-item-subtitle>
                            </v-list-item>
                            <v-divider class="my-2"></v-divider>
                            <v-list-item>
                              <v-list-item-title>Pay Period</v-list-item-title>
                              <v-list-item-subtitle class="text-right">
                                {{ formatDate(payRun.start_date) }} - {{ formatDate(payRun.end_date) }}
                              </v-list-item-subtitle>
                            </v-list-item>
                          </v-list>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    
                    <v-col cols="12" md="6">
                      <v-card variant="outlined">
                        <v-card-text>
                          <div class="text-h6 mb-4">Summary</div>
                          <v-table density="compact">
                            <tbody>
                              <tr><td>Total Employees</td><td class="text-right">{{ payRun.employee_count }}</td></tr>
                              <tr><td>Total Hours</td><td class="text-right">{{ payRun.total_hours?.toFixed(2) || '0.00' }}</td></tr>
                              <tr><td>Total Gross Pay</td><td class="text-right">{{ formatCurrency(payRun.total_gross) }}</td></tr>
                              <tr><td>Total Deductions</td><td class="text-right">{{ formatCurrency(payRun.total_deductions) }}</td></tr>
                              <tr class="font-weight-bold"><td>Total Net Pay</td><td class="text-right">{{ formatCurrency(payRun.total_net) }}</td></tr>
                            </tbody>
                          </v-table>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                </v-card-text>
                
                <v-card-actions class="px-4 pb-4">
                  <v-spacer></v-spacer>
                  <v-btn color="secondary" variant="text" @click="$router.go(-1)">
                    Cancel
                  </v-btn>
                  <v-btn color="primary" @click="currentStep = 2">
                    Continue to Calculation
                    <v-icon end>mdi-arrow-right</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-stepper-window-item>
              
              <!-- Step 2: Calculate -->
              <v-stepper-window-item :value="2">
                <v-card-text>
                  <v-alert type="info" variant="tonal" class="mb-4" icon="mdi-calculator">
                    Review the calculated payroll amounts before proceeding.
                  </v-alert>
                  
                  <v-card variant="outlined" class="mb-4">
                    <v-card-title class="text-h6">Calculation Summary</v-card-title>
                    <v-card-text>
                      <v-row>
                        <v-col cols="12" md="6">
                          <v-table density="compact">
                            <tbody>
                              <tr><td>Total Regular Hours</td><td class="text-right">{{ payRunSummary.regular_hours?.toFixed(2) || '0.00' }}</td></tr>
                              <tr><td>Total Overtime Hours</td><td class="text-right">{{ payRunSummary.overtime_hours?.toFixed(2) || '0.00' }}</td></tr>
                              <tr><td>Total Hours</td><td class="text-right font-weight-bold">{{ payRunSummary.total_hours?.toFixed(2) || '0.00' }}</td></tr>
                            </tbody>
                          </v-table>
                        </v-col>
                        
                        <v-col cols="12" md="6">
                          <v-table density="compact">
                            <tbody>
                              <tr><td>Total Gross Pay</td><td class="text-right">{{ formatCurrency(payRunSummary.total_gross) }}</td></tr>
                              <tr><td>Total Taxes</td><td class="text-right">{{ formatCurrency(payRunSummary.total_taxes) }}</td></tr>
                              <tr><td>Total Deductions</td><td class="text-right">{{ formatCurrency(payRunSummary.total_deductions) }}</td></tr>
                              <tr class="font-weight-bold"><td>Total Net Pay</td><td class="text-right">{{ formatCurrency(payRunSummary.total_net) }}</td></tr>
                            </tbody>
                          </v-table>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-card-text>
                
                <v-card-actions class="px-4 pb-4">
                  <v-btn color="secondary" variant="text" @click="currentStep = 1">
                    <v-icon start>mdi-arrow-left</v-icon>
                    Back
                  </v-btn>
                  
                  <v-spacer></v-spacer>
                  
                  <v-btn color="primary" @click="currentStep = 3">
                    Continue to Approval
                    <v-icon end>mdi-arrow-right</v-icon>
                  </v-btn>
                </v-card-actions>
              </v-stepper-window-item>
              
              <!-- Step 3: Approve -->
              <v-stepper-window-item :value="3">
                <v-card-text>
                  <v-alert type="info" variant="tonal" class="mb-4" icon="mdi-shield-check">
                    Review and approve the payroll. Once approved, the payroll will be processed.
                  </v-alert>
                  
                  <v-card variant="outlined" class="mb-4">
                    <v-card-title class="text-h6">Approval Summary</v-card-title>
                    <v-card-text>
                      <v-textarea
                        v-model="approvalComments"
                        label="Approval Comments"
                        variant="outlined"
                        rows="3"
                        hint="Add any comments or notes for this approval"
                        persistent-hint
                      ></v-textarea>
                    </v-card-text>
                  </v-card>
                </v-card-text>
                
                <v-card-actions class="px-4 pb-4">
                  <v-btn color="secondary" variant="text" @click="currentStep = 2">
                    <v-icon start>mdi-arrow-left</v-icon>
                    Back
                  </v-btn>
                  
                  <v-spacer></v-spacer>
                  
                  <v-btn color="error" variant="tonal" @click="rejectDialog = true" class="me-2">
                    <v-icon start>mdi-close-circle</v-icon>
                    Reject
                  </v-btn>
                  
                  <v-btn color="primary" @click="approvePayRun" :loading="processing">
                    <v-icon start>mdi-check-circle</v-icon>
                    Approve & Process
                  </v-btn>
                </v-card-actions>
              </v-stepper-window-item>
              
              <!-- Step 4: Complete -->
              <v-stepper-window-item :value="4">
                <v-card-text class="text-center py-8">
                  <v-icon size="64" color="success" class="mb-4">
                    mdi-check-circle
                  </v-icon>
                  
                  <h2 class="text-h4 mb-2">Payroll Processed Successfully!</h2>
                  
                  <p class="text-body-1 text-medium-emphasis mb-6">
                    The payroll for {{ formatDate(payRun.start_date) }} - {{ formatDate(payRun.end_date) }} has been successfully processed.
                  </p>
                  
                  <v-card variant="outlined" class="mx-auto mb-6" max-width="400">
                    <v-card-text>
                      <v-list density="compact" class="bg-transparent">
                        <v-list-item>
                          <v-list-item-title>Pay Run ID</v-list-item-title>
                          <v-list-item-subtitle class="text-right">{{ payRun.id }}</v-list-item-subtitle>
                        </v-list-item>
                        
                        <v-divider class="my-2"></v-divider>
                        
                        <v-list-item>
                          <v-list-item-title>Total Employees</v-list-item-title>
                          <v-list-item-subtitle class="text-right">{{ payRun.employee_count }}</v-list-item-subtitle>
                        </v-list-item>
                        
                        <v-divider class="my-2"></v-divider>
                        
                        <v-list-item>
                          <v-list-item-title>Total Net Pay</v-list-item-title>
                          <v-list-item-subtitle class="text-right font-weight-bold">{{ formatCurrency(payRun.total_net) }}</v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </v-card-text>
                  </v-card>
                </v-card-text>
                
                <v-card-actions class="px-4 pb-4">
                  <v-spacer></v-spacer>
                  
                  <v-btn color="primary" @click="$router.push({ name: 'payroll-runs' })">
                    Back to Pay Runs
                  </v-btn>
                </v-card-actions>
              </v-stepper-window-item>
            </v-stepper-window>
          </v-stepper>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Reject Dialog -->
    <v-dialog v-model="rejectDialog" max-width="500">
      <v-card>
        <v-card-title>Reject Pay Run</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="rejectReason"
            label="Reason for rejection"
            variant="outlined"
            rows="3"
            :rules="[v => !!v || 'Please provide a reason for rejection']"
            required
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="secondary" variant="text" @click="rejectDialog = false">
            Cancel
          </v-btn>
          <v-btn color="error" @click="confirmReject" :loading="rejecting">
            Confirm Rejection
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

export default defineComponent({
  name: 'PayRunProcessView',
  
  props: {
    id: {
      type: String,
      required: true
    }
  },
  
  setup(props) {
    const route = useRoute();
    const router = useRouter();
    
    const currentStep = ref(1);
    const processing = ref(false);
    const rejecting = ref(false);
    const rejectDialog = ref(false);
    const rejectReason = ref('');
    const approvalComments = ref('');
    
    // Mock data - replace with API calls
    const payRun = ref({
      id: props.id || 'PR-2023-08-001',
      status: 'draft',
      start_date: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
      end_date: new Date(),
      payment_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
      pay_frequency: 'Bi-weekly',
      employee_count: 24,
      total_hours: 920.5,
      total_gross: 32567.89,
      total_deductions: 8567.23,
      total_net: 24000.66,
      employee_payments: []
    });
    
    const payRunSummary = ref({
      regular_hours: 840,
      overtime_hours: 80.5,
      total_hours: 920.5,
      total_gross: 32567.89,
      total_taxes: 7567.23,
      total_benefits: 1000,
      total_deductions: 8567.23,
      total_net: 24000.66
    });
    
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
    const formatDate = (date: Date | string) => {
      if (!date) return 'N/A';
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    };
    
    // Get status color
    const getStatusColor = (status: string) => {
      const statusMap: Record<string, string> = {
        draft: 'grey',
        pending: 'warning',
        processing: 'info',
        approved: 'success',
        rejected: 'error',
        paid: 'success'
      };
      return statusMap[status.toLowerCase()] || 'grey';
    };
    
    // Format status
    const formatStatus = (status: string) => {
      return status
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    };
    
    // Approve pay run
    const approvePayRun = () => {
      processing.value = true;
      
      // Simulate API call
      setTimeout(() => {
        payRun.value.status = 'approved';
        currentStep.value = 4;
        processing.value = false;
      }, 1500);
    };
    
    // Confirm reject
    const confirmReject = () => {
      if (!rejectReason.value.trim()) return;
      
      rejecting.value = true;
      
      // Simulate API call
      setTimeout(() => {
        payRun.value.status = 'rejected';
        rejectDialog.value = false;
        rejecting.value = false;
        rejectReason.value = '';
        
        // Go back to previous step
        if (currentStep.value > 1) {
          currentStep.value--;
        }
      }, 1000);
    };
    
    // Initial load
    onMounted(() => {
      // Fetch pay run details from API
      // fetchPayRunDetails();
    });
    
    return {
      currentStep,
      processing,
      rejecting,
      rejectDialog,
      rejectReason,
      approvalComments,
      payRun,
      payRunSummary,
      formatCurrency,
      formatDate,
      getStatusColor,
      formatStatus,
      approvePayRun,
      confirmReject
    };
  }
});
</script>
