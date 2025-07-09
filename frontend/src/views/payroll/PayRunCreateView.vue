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
      </v-window>
    </v-form>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatDate } from '@/utils/formatters';

const router = useRouter();
const { showSuccess, showError } = useSnackbar();

// Form state
const currentStep = ref(0);
const totalSteps = 4;
const isFormValid = ref(false);
const isSubmitting = ref(false);
const form = ref(null);

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

const nextStep = async () => {
  const { valid } = await form.value.validate();
  if (valid) {
    currentStep.value = Math.min(currentStep.value + 1, totalSteps - 1);
  }
};

const prevStep = () => {
  currentStep.value = Math.max(currentStep.value - 1, 0);
};

const submitPayRun = async () => {
  isSubmitting.value = true;
  try {
    // TODO: Implement API call to submit pay run
    console.log('Submitting pay run:', payRun.value);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    showSuccess('Pay run created successfully');
    router.push({ name: 'payroll-runs' });
  } catch (error) {
    console.error('Error creating pay run:', error);
    showError('Failed to create pay run. Please try again.');
  } finally {
    isSubmitting.value = false;
  }
};

// Initialize form with default values
onMounted(() => {
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
