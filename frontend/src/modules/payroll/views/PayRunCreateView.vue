<template>
  <v-container fluid class="pa-6">
    <!-- Page Header -->
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
            <h1 class="text-h4 font-weight-bold">Create New Pay Run</h1>
            <p class="text-subtitle-1 text-medium-emphasis">
              Follow the steps to create a new payroll run
            </p>
          </div>
        </div>
      </v-col>
      <v-col cols="12" sm="6" md="4" class="text-right">
        <v-btn
          variant="outlined"
          color="secondary"
          class="mr-2"
          :to="{ name: 'payroll-runs' }"
          :disabled="isSubmitting"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          :loading="isSubmitting"
          :disabled="!isFormValid || isSubmitting"
          @click="nextStep"
          v-if="currentStep < totalSteps - 1"
        >
          Next
          <v-icon end>mdi-arrow-right</v-icon>
        </v-btn>
        <v-btn
          color="primary"
          :loading="isSubmitting"
          :disabled="!isFormValid || isSubmitting"
          @click="submitPayRun"
          v-else
        >
          <v-icon start>mdi-check</v-icon>
          Submit Pay Run
        </v-btn>
      </v-col>
    </v-row>

    <ErrorPanel
      v-if="formError"
      :visible="!!formError"
      title="Unable to create pay run"
      :message="formError.message"
      :request-id="formError.requestId"
      :details="formError.details"
    />

    <!-- Progress Stepper -->
    <v-stepper v-model="currentStep" class="elevation-0 mb-6" :items="stepItems">
      <template v-slot:item.1.title>
        <div class="text-subtitle-2">Pay Period</div>
      </template>
      <template v-slot:item.2.title>
        <div class="text-subtitle-2">Employees</div>
      </template>
      <template v-slot:item.3.title>
        <div class="text-subtitle-2">Earnings & Deductions</div>
      </template>
      <template v-slot:item.4.title>
        <div class="text-subtitle-2">Review & Submit</div>
      </template>
    </v-stepper>

    <!-- Form Content -->
    <v-form ref="form" v-model="isFormValid" @submit.prevent>
      <!-- Step 1: Pay Period -->
      <v-window v-model="currentStep" class="elevation-1 rounded">
        <v-window-item :value="0">
          <v-card variant="flat" class="rounded-0">
            <v-card-title class="text-subtitle-1 font-weight-bold">
              Pay Period Details
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pt-6">
              <v-row>
                <v-col cols="12" md="6">
                  <v-select
                    v-model="payRun.payPeriodType"
                    :items="payPeriodTypes"
                    item-title="label"
                    item-value="value"
                    label="Pay Period Type"
                    variant="outlined"
                    :rules="[required]"
                    :error-messages="formErrors.payPeriodType ? [formErrors.payPeriodType] : []"
                    density="comfortable"
                    :disabled="isSubmitting"
                    @update:modelValue="updatePayPeriodDates"
                  ></v-select>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="payRun.payRunName"
                    label="Pay Run Name"
                    variant="outlined"
                    :rules="[required]"
                    :error-messages="formErrors.payRunName ? [formErrors.payRunName] : []"
                    density="comfortable"
                    :disabled="isSubmitting"
                    hint="A descriptive name for this pay run (e.g., 'January 2025 Monthly Payroll')"
                    persistent-hint
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-menu
                    v-model="startDateMenu"
                    :close-on-content-click="false"
                    transition="scale-transition"
                    min-width="auto"
                  >
                    <template v-slot:activator="{ props }">
                      <v-text-field
                        v-model="payRun.payPeriodStartDate"
                        label="Pay Period Start Date"
                        variant="outlined"
                        :rules="[required]"
                        :error-messages="formErrors.payPeriodStartDate ? [formErrors.payPeriodStartDate] : []"
                        density="comfortable"
                        :disabled="isSubmitting"
                        v-bind="props"
                        readonly
                        append-inner-icon="mdi-calendar"
                      ></v-text-field>
                    </template>
                    <v-date-picker
                      v-model="payRun.payPeriodStartDate"
                      @update:modelValue="updatePayPeriodDates"
                      :max="new Date().toISOString().substr(0, 10)"
                    ></v-date-picker>
                  </v-menu>
                </v-col>
                <v-col cols="12" md="6">
                  <v-menu
                    v-model="endDateMenu"
                    :close-on-content-click="false"
                    transition="scale-transition"
                    min-width="auto"
                  >
                    <template v-slot:activator="{ props }">
                      <v-text-field
                        v-bind="props"
                        v-model="payRun.payPeriodEndDate"
                        label="Pay Period End Date"
                        variant="outlined"
                        :rules="[required]"
                        :error-messages="formErrors.payPeriodEndDate ? [formErrors.payPeriodEndDate] : []"
                        density="comfortable"
                        :disabled="isSubmitting || !payRun.payPeriodStartDate"
                        readonly
                        append-inner-icon="mdi-calendar"
                      ></v-text-field>
                    </template>
                    <v-date-picker
                      v-model="payRun.payPeriodEndDate"
                      :min="payRun.payPeriodStartDate"
                      :max="new Date().toISOString().substr(0, 10)"
                    ></v-date-picker>
                  </v-menu>
                </v-col>
                <v-col cols="12" md="6">
                  <v-menu
                    v-model="paymentDateMenu"
                    :close-on-content-click="false"
                    transition="scale-transition"
                    min-width="auto"
                  >
                    <template v-slot:activator="{ props }">
                      <v-text-field
                        v-bind="props"
                        v-model="payRun.paymentDate"
                        label="Payment Date"
                        variant="outlined"
                        :rules="[required]"
                        :error-messages="formErrors.paymentDate ? [formErrors.paymentDate] : []"
                        density="comfortable"
                        :disabled="isSubmitting"
                        readonly
                        append-inner-icon="mdi-calendar"
                      ></v-text-field>
                    </template>
                    <v-date-picker
                      v-model="payRun.paymentDate"
                      :min="new Date().toISOString().substr(0, 10)"
                    ></v-date-picker>
                  </v-menu>
                </v-col>
                <v-col cols="12" md="6">
                  <v-select
                    v-model="payRun.payFrequency"
                    :items="payFrequencies"
                    item-title="label"
                    item-value="value"
                    label="Pay Frequency"
                    variant="outlined"
                    :rules="[required]"
                    :error-messages="formErrors.payFrequency ? [formErrors.payFrequency] : []"
                    density="comfortable"
                    :disabled="isSubmitting"
                  ></v-select>
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    v-model="payRun.notes"
                    label="Notes"
                    variant="outlined"
                    rows="2"
                    density="comfortable"
                    :disabled="isSubmitting"
                    hint="Any additional notes about this pay run"
                    persistent-hint
                  ></v-textarea>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-window-item>
        <v-window-item :value="3">
          <v-card variant="flat" class="rounded-0">
            <v-card-title class="text-subtitle-1 font-weight-bold">
              Review and Submit
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text class="pt-6">
              <v-row>
                <v-col cols="12">
                  <v-card class="pa-4 mb-4">
                    <v-card-title class="text-subtitle-1 font-weight-bold">
                      Tax Summary
                    </v-card-title>
                    <v-divider class="mb-4"></v-divider>
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-card-text class="pa-0">
                          <div class="text-subtitle-2">Total Employees: {{ payRun.employeeCount }}</div>
                          <div class="text-subtitle-2">Total Amount: {{ formatCurrency(payRun.totalAmount) }}</div>
                        </v-card-text>
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-card-text class="pa-0">
                          <div class="text-subtitle-2">Total Tax: {{ formatCurrency(payRun.taxAmount) }}</div>
                          <div class="text-subtitle-2">Tax Breakdown:</div>
                          <div v-for="(amount, bracket) in payRun.taxBreakdown" :key="bracket" class="text-caption">
                            {{ bracket }}: {{ formatCurrency(amount) }}
                          </div>
                        </v-card-text>
                      </v-col>
                    </v-row>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-window-item>
      </v-window>
    </v-form>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useTaxPolicyStore } from '@/modules/tax/store/policy';
import { createPayRun } from '@/modules/payroll/services/payrollService';
import ErrorPanel from '@/components/common/ErrorPanel.vue';
import { validateSchema } from '@/utils/formValidation';
// Mock tax calculation service
const taxCalculationService = {
  calculatePayRunTax: (payRun: any) => ({
    taxAmount: payRun.payslips.reduce((sum: number, payslip: any) => sum + (payslip.gross_income * 0.15), 0),
    taxBreakdown: {
      'Federal Tax': payRun.payslips.reduce((sum: number, payslip: any) => sum + (payslip.gross_income * 0.10), 0),
      'State Tax': payRun.payslips.reduce((sum: number, payslip: any) => sum + (payslip.gross_income * 0.05), 0)
    },
    exemptions: {}
  })
};
import { useSnackbar } from '@/composables/useSnackbar';

const router = useRouter();
const { showSuccess, showError } = useSnackbar();

// Form state
const currentStep = ref(0);
const totalSteps = 4;
const isFormValid = ref(false);
const isSubmitting = ref(false);
const form = ref(null);
const formError = ref<{ message: string; requestId?: string; details?: string[] } | null>(null);
const formErrors = ref<Record<string, string>>({});

// UI state
const startDateMenu = ref(false);
const endDateMenu = ref(false);
const paymentDateMenu = ref(false);

// Form data
const payRun = ref({
  payPeriodType: 'monthly',
  payRunName: '',
  payPeriodStartDate: '',
  payPeriodEndDate: '',
  paymentDate: '',
  payFrequency: 'monthly',
  notes: '',
  status: 'draft',
  employeeCount: 0,
  totalAmount: 0,
  taxAmount: 0,
  taxBreakdown: {},
  exemptions: {},
  employeeIds: [] as string[],
  earnings: [],
  deductions: [],
});

// Dropdown options
const payPeriodTypes = [
  { label: 'Monthly', value: 'monthly' },
  { label: 'Bi-Monthly', value: 'bimonthly' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Bi-Weekly', value: 'biweekly' },
  { label: 'Custom', value: 'custom' },
];

const payFrequencies = [
  { label: 'Monthly', value: 'monthly' },
  { label: 'Semi-Monthly', value: 'semi_monthly' },
  { label: 'Bi-Weekly', value: 'biweekly' },
  { label: 'Weekly', value: 'weekly' },
];

// Step items for the stepper
const stepItems = computed(() => {
  return [
    { title: 'Pay Period', value: 1 },
    { title: 'Employees', value: 2 },
    { title: 'Earnings & Deductions', value: 3 },
    { title: 'Review & Submit', value: 4 },
  ];
});

// Validation rules
const required = (v: any) => !!v || 'This field is required';

const payRunSchema = {
  payPeriodType: { required: true, label: 'Pay period type' },
  payRunName: { required: true, label: 'Pay run name' },
  payPeriodStartDate: { required: true, label: 'Pay period start date' },
  payPeriodEndDate: { required: true, label: 'Pay period end date' },
  paymentDate: { required: true, label: 'Payment date' },
  payFrequency: { required: true, label: 'Pay frequency' }
};

const validatePayRunForm = () => {
  const validation = validateSchema(payRun.value, payRunSchema);
  formErrors.value = validation.errors;
  return validation.isValid;
};

// Methods
const updatePayPeriodDates = () => {
  if (payRun.value.payPeriodStartDate && !payRun.value.payPeriodType === 'custom') {
    const startDate = new Date(payRun.value.payPeriodStartDate);
    let endDate = new Date(startDate);
    
    switch (payRun.value.payPeriodType) {
      case 'weekly':
        endDate.setDate(startDate.getDate() + 6);
        break;
      case 'biweekly':
        endDate.setDate(startDate.getDate() + 13);
        break;
      case 'monthly':
        endDate.setMonth(startDate.getMonth() + 1);
        endDate.setDate(0); // Last day of the month
        break;
      case 'bimonthly':
        // Set to 15th or end of month based on start date
        if (startDate.getDate() <= 15) {
          endDate.setDate(15);
        } else {
          endDate.setMonth(startDate.getMonth() + 1);
          endDate.setDate(0);
        }
        break;
    }
    
    payRun.value.payPeriodEndDate = endDate.toISOString().split('T')[0];
    
    // Set default payment date to 5 days after period end
    const paymentDate = new Date(payRun.value.payPeriodEndDate);
    paymentDate.setDate(paymentDate.getDate() + 5);
    payRun.value.paymentDate = paymentDate.toISOString().split('T')[0];
  }
};

const calculateTotalTax = () => {
  if (!payRun.value.employeeCount || !payRun.value.totalAmount) return;
  
  const mockPayslips = Array(payRun.value.employeeCount).fill({
    gross_income: payRun.value.totalAmount / payRun.value.employeeCount,
    earnings: []
  });

  const mockPayRun = {
    payslips: mockPayslips,
    period_start: payRun.value.payPeriodStartDate,
    period_end: payRun.value.payPeriodEndDate
  };

  const taxResult = taxCalculationService.calculatePayRunTax(mockPayRun);
  payRun.value.taxAmount = taxResult.taxAmount;
  payRun.value.taxBreakdown = taxResult.taxBreakdown;
  payRun.value.exemptions = taxResult.exemptions;
};

const nextStep = async () => {
  const { valid } = await form.value.validate();
  if (valid && validatePayRunForm()) {
    currentStep.value = Math.min(currentStep.value + 1, totalSteps - 1);
  }
};

const prevStep = () => {
  currentStep.value = Math.max(currentStep.value - 1, 0);
};

const submitPayRun = async () => {
  try {
    formError.value = null;
    if (!validatePayRunForm()) {
      return;
    }
    isSubmitting.value = true;
    
    // Calculate tax before submission
    calculateTotalTax();

    const response = await createPayRun({
      period_id: payRun.value.payPeriodStartDate,
      notes: payRun.value.notes,
      tax_policy_id: useTaxPolicyStore().getCurrentPolicy()?.id,
      custom_tax_rates: useTaxPolicyStore().getTaxRates(),
      custom_exemptions: useTaxPolicyStore().getTaxExemptions()
    });

    router.push({ name: 'payroll-run-details', params: { id: response.id } });
  } catch (error) {
    console.error('Error creating pay run:', error);
    formError.value = {
      message: 'Failed to create pay run. Please try again.',
      requestId: (error as any)?.requestId || (error as any)?.response?.headers?.['x-request-id']
    };
    snackbar.value = {
      message: 'Failed to create pay run. Please try again.',
      color: 'error'
    };
  } finally {
    isSubmitting.value = false;
  }
};

// Initialize form with default values
onMounted(() => {
  // Initialize tax policy store
  const taxPolicyStore = useTaxPolicyStore();
  taxPolicyStore.fetchPolicy();

  // Watch for tax policy changes
  watch(() => taxPolicyStore.getCurrentPolicy(), (newPolicy) => {
    if (newPolicy) {
      calculateTotalTax();
    }
  });

  const today = new Date();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
  const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
  
  payRun.value.payPeriodStartDate = firstDay.toISOString().split('T')[0];
  payRun.value.payPeriodEndDate = lastDay.toISOString().split('T')[0];
  
  // Set default payment date to 5 days from now
  const paymentDate = new Date();
  paymentDate.setDate(paymentDate.getDate() + 5);
  payRun.value.paymentDate = paymentDate.toISOString().split('T')[0];
  
  // Generate default pay run name (e.g., "July 2025 Monthly Payroll")
  payRun.value.payRunName = `${new Date().toLocaleString('default', { month: 'long' })} ${today.getFullYear()} Monthly Payroll`;
});
</script>

<style scoped>
/* Add any custom styles here */
</style>
