<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <div>
              <v-icon class="me-2" size="large">mdi-cash-multiple</v-icon>
              <span class="text-h5">Run Payroll</span>
            </div>
            <div>
              <v-btn
                color="primary"
                class="me-2"
                :disabled="!canRunPayroll"
                @click="runPayroll"
                :loading="isRunning"
              >
                <v-icon start>mdi-play</v-icon>
                Run Payroll
              </v-btn>
            </div>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text>
            <v-stepper v-model="currentStep" class="elevation-0">
              <v-stepper-header>
                <v-stepper-item
                  :value="1"
                  :complete="currentStep > 1"
                  title="Select Pay Period"
                ></v-stepper-item>
                <v-divider></v-divider>
                <v-stepper-item
                  :value="2"
                  :complete="currentStep > 2"
                  title="Review & Adjust"
                ></v-stepper-item>
                <v-divider></v-divider>
                <v-stepper-item
                  :value="3"
                  :complete="currentStep > 3"
                  title="Approve & Submit"
                ></v-stepper-item>
              </v-stepper-header>

              <v-stepper-window>
                <!-- Step 1: Select Pay Period -->
                <v-stepper-window-item :value="1">
                  <v-card variant="outlined" class="mb-6">
                    <v-card-title class="text-subtitle-1 font-weight-bold">
                      Pay Period Details
                    </v-card-title>
                    <v-divider></v-divider>
                    <v-card-text>
                      <v-row>
                        <v-col cols="12" md="6">
                          <v-select
                            v-model="payrollType"
                            :items="payrollTypes"
                            label="Payroll Type"
                            variant="outlined"
                            density="comfortable"
                          ></v-select>
                        </v-col>
                        <v-col cols="12" md="6">
                          <v-menu
                            v-model="showStartDatePicker"
                            :close-on-content-click="false"
                            transition="scale-transition"
                            min-width="auto"
                          >
                            <template v-slot:activator="{ props }">
                              <v-text-field
                                v-model="formattedStartDate"
                                label="Pay Period Start Date"
                                variant="outlined"
                                density="comfortable"
                                readonly
                                v-bind="props"
                                append-inner-icon="mdi-calendar"
                              ></v-text-field>
                            </template>
                            <v-date-picker
                              v-model="payPeriod.startDate"
                              @update:model-value="updatePayPeriodEndDate"
                            ></v-date-picker>
                          </v-menu>
                        </v-col>
                        <v-col cols="12" md="6">
                          <v-text-field
                            v-model="formattedEndDate"
                            label="Pay Period End Date"
                            variant="outlined"
                            density="comfortable"
                            readonly
                          ></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                          <v-menu
                            v-model="showPayDatePicker"
                            :close-on-content-click="false"
                            transition="scale-transition"
                            min-width="auto"
                          >
                            <template v-slot:activator="{ props }">
                              <v-text-field
                                v-model="formattedPayDate"
                                label="Pay Date"
                                variant="outlined"
                                density="comfortable"
                                readonly
                                v-bind="props"
                                append-inner-icon="mdi-calendar"
                              ></v-text-field>
                            </template>
                            <v-date-picker
                              v-model="payDate"
                              :min="minPayDate"
                            ></v-date-picker>
                          </v-menu>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-stepper-window-item>

                <!-- Step 2: Review & Adjust -->
                <v-stepper-window-item :value="2">
                  <v-card variant="outlined" class="mb-6">
                    <v-card-title class="text-subtitle-1 font-weight-bold">
                      Payroll Summary
                    </v-card-title>
                    <v-divider></v-divider>
                    <v-card-text>
                      <v-row>
                        <v-col cols="12" md="4">
                          <v-card variant="tonal" class="text-center pa-4">
                            <div class="text-subtitle-2 text-medium-emphasis">Total Employees</div>
                            <div class="text-h4">{{ summary.totalEmployees }}</div>
                          </v-card>
                        </v-col>
                        <v-col cols="12" md="4">
                          <v-card variant="tonal" color="success" class="text-center pa-4">
                            <div class="text-subtitle-2 text-medium-emphasis">Total Gross Pay</div>
                            <div class="text-h4">{{ formatCurrency(summary.totalGrossPay) }}</div>
                          </v-card>
                        </v-col>
                        <v-col cols="12" md="4">
                          <v-card variant="tonal" color="primary" class="text-center pa-4">
                            <div class="text-subtitle-2 text-medium-emphasis">Total Net Pay</div>
                            <div class="text-h4">{{ formatCurrency(summary.totalNetPay) }}</div>
                          </v-card>
                        </v-col>
                      </v-row>

                      <v-data-table
                        :headers="payrollDetailsHeaders"
                        :items="payrollDetails"
                        :items-per-page="10"
                        class="elevation-1 mt-4"
                      >
                        <template v-slot:item.actions="{ item }">
                          <v-btn
                            icon
                            size="small"
                            variant="text"
                            @click="viewEmployeeDetails(item)"
                          >
                            <v-icon>mdi-eye</v-icon>
                          </v-btn>
                        </template>
                      </v-data-table>
                    </v-card-text>
                  </v-card>
                </v-stepper-window-item>

                <!-- Step 3: Approve & Submit -->
                <v-stepper-window-item :value="3">
                  <v-card variant="outlined" class="mb-6">
                    <v-card-title class="text-subtitle-1 font-weight-bold">
                      Approve Payroll
                    </v-card-title>
                    <v-divider></v-divider>
                    <v-card-text>
                      <v-alert
                        type="info"
                        variant="tonal"
                        class="mb-6"
                      >
                        <div class="text-subtitle-2">Review the payroll details before final submission.</div>
                      </v-alert>

                      <v-row>
                        <v-col cols="12" md="6">
                          <v-card variant="outlined" class="mb-4">
                            <v-card-text>
                              <div class="text-subtitle-2 mb-2">Pay Period</div>
                              <div>{{ formattedStartDate }} to {{ formattedEndDate }}</div>
                              <div class="text-subtitle-2 mt-4 mb-2">Pay Date</div>
                              <div>{{ formattedPayDate }}</div>
                              <div class="text-subtitle-2 mt-4 mb-2">Employees</div>
                              <div>{{ summary.totalEmployees }} employees selected</div>
                            </v-card-text>
                          </v-card>
                        </v-col>
                        <v-col cols="12" md="6">
                          <v-card variant="outlined" class="mb-4">
                            <v-card-text>
                              <div class="d-flex justify-space-between mb-2">
                                <span>Total Gross Pay:</span>
                                <span class="font-weight-bold">{{ formatCurrency(summary.totalGrossPay) }}</span>
                              </div>
                              <div class="d-flex justify-space-between mb-2">
                                <span>Total Deductions:</span>
                                <span class="font-weight-bold text-red">-{{ formatCurrency(summary.totalDeductions) }}</span>
                              </div>
                              <div class="d-flex justify-space-between mb-2">
                                <span>Total Taxes:</span>
                                <span class="font-weight-bold text-red">-{{ formatCurrency(summary.totalTaxes) }}</span>
                              </div>
                              <v-divider class="my-3"></v-divider>
                              <div class="d-flex justify-space-between text-h6">
                                <span>Net Pay:</span>
                                <span class="font-weight-bold text-primary">{{ formatCurrency(summary.totalNetPay) }}</span>
                              </div>
                            </v-card-text>
                          </v-card>
                        </v-col>
                      </v-row>

                      <v-checkbox
                        v-model="approval.approved"
                        label="I have reviewed and approve this payroll run"
                        hide-details
                        class="mt-4"
                      ></v-checkbox>
                    </v-card-text>
                  </v-card>
                </v-stepper-window-item>
              </v-stepper-window>

              <v-stepper-actions
                :next-text="currentStep === 3 ? 'Submit Payroll' : 'Continue'"
                :prev-text="currentStep === 1 ? 'Cancel' : 'Back'"
                @click:next="nextStep"
                @click:prev="prevStep"
                :next-disabled="!canProceedToNextStep"
                :loading="isSubmitting"
              ></v-stepper-actions>
            </v-stepper>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { format, parseISO, addDays } from 'date-fns';

const router = useRouter();

// Stepper state
const currentStep = ref(1);
const isSubmitting = ref(false);
const isRunning = ref(false);
const canRunPayroll = ref(true);

// Pay period state
const payrollType = ref('regular');
const showStartDatePicker = ref(false);
const showPayDatePicker = ref(false);

// Date handling
const today = new Date();
const payPeriod = ref({
  startDate: format(today, 'yyyy-MM-dd'),
  endDate: format(addDays(today, 13), 'yyyy-MM-dd'),
});

const payDate = ref(format(addDays(today, 7), 'yyyy-MM-dd'));
const minPayDate = computed(() => {
  return format(addDays(new Date(payPeriod.value.endDate), 1), 'yyyy-MM-dd');
});

// Format dates for display
const formattedStartDate = computed(() => {
  return format(parseISO(payPeriod.value.startDate), 'MMM d, yyyy');
});

const formattedEndDate = computed(() => {
  return format(parseISO(payPeriod.value.endDate), 'MMM d, yyyy');
});

const formattedPayDate = computed(() => {
  return payDate.value ? format(parseISO(payDate.value), 'EEEE, MMM d, yyyy') : '';
});

// Update end date when start date changes
const updatePayPeriodEndDate = () => {
  const start = parseISO(payPeriod.value.startDate);
  payPeriod.value.endDate = format(addDays(start, 13), 'yyyy-MM-dd');
  showStartDatePicker.value = false;
};

// Payroll types
const payrollTypes = [
  'Regular Payroll',
  'Bonus Payroll',
  'Off-Cycle Payroll',
  'Termination Pay',
];

// Summary data
const summary = ref({
  totalEmployees: 1,
  totalRegularPay: 3640,
  totalOvertimePay: 546,
  totalBonus: 0,
  totalCommission: 0,
  totalGrossPay: 4186,
  totalDeductions: 420,
  totalTaxes: 641.15,
  totalNetPay: 3124.85,
});

// Payroll details
const payrollDetails = ref([
  {
    id: 1,
    name: 'John Doe',
    employeeId: 'EMP-001',
    department: 'Engineering',
    regularPay: 3640,
    overtimePay: 546,
    grossPay: 4186,
    deductions: 420,
    taxes: 641.15,
    netPay: 3124.85,
  },
]);

// Table headers
const payrollDetailsHeaders = [
  { title: 'Employee', key: 'name' },
  { title: 'Employee ID', key: 'employeeId' },
  { title: 'Department', key: 'department' },
  { title: 'Regular Pay', key: 'regularPay', align: 'end' },
  { title: 'Overtime Pay', key: 'overtimePay', align: 'end' },
  { title: 'Gross Pay', key: 'grossPay', align: 'end' },
  { title: 'Deductions', key: 'deductions', align: 'end' },
  { title: 'Taxes', key: 'taxes', align: 'end' },
  { title: 'Net Pay', key: 'netPay', align: 'end' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

// Approval
const approval = ref({
  approved: false,
  notes: '',
});

// Navigation
const canProceedToNextStep = computed(() => {
  if (currentStep.value === 1) {
    return payPeriod.value.startDate && payPeriod.value.endDate && payDate.value;
  } else if (currentStep.value === 2) {
    return true;
  } else if (currentStep.value === 3) {
    return approval.value.approved;
  }
  return false;
});

const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++;
  } else {
    submitPayroll();
  }
};

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--;
  } else {
    router.push('/payroll');
  }
};

// Actions
const runPayroll = async () => {
  try {
    isRunning.value = true;
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    currentStep.value = 2;
  } catch (error) {
    console.error('Error calculating payroll:', error);
  } finally {
    isRunning.value = false;
  }
};

const submitPayroll = async () => {
  try {
    isSubmitting.value = true;
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    router.push('/payroll/history');
  } catch (error) {
    console.error('Error submitting payroll:', error);
  } finally {
    isSubmitting.value = false;
  }
};

const viewEmployeeDetails = (employee: any) => {
  // Implementation for viewing employee details
  console.log('View employee details:', employee);
};

// Format currency
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(value);
};

// Lifecycle hooks
onMounted(() => {
  // Load initial data
});
</script>
