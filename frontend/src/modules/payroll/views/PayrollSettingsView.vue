<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <div>
              <v-icon class="me-2" size="large">mdi-cog</v-icon>
              <span class="text-h5">Payroll Settings</span>
            </div>
            <v-btn color="primary" @click="saveSettings" :loading="isSaving">
              <v-icon start>mdi-content-save</v-icon>
              Save Changes
            </v-btn>
          </v-card-title>
          
          <v-divider></v-divider>
          
          <v-card-text>
            <v-tabs v-model="activeTab" grow class="mb-6">
              <v-tab value="general">General</v-tab>
              <v-tab value="taxes">Tax Settings</v-tab>
              <v-tab value="deductions">Deductions</v-tab>
              <v-tab value="benefits">Benefits</v-tab>
            </v-tabs>

            <v-window v-model="activeTab">
              <!-- General Settings Tab -->
              <v-window-item value="general">
                <v-card variant="outlined" class="mb-6">
                  <v-card-title class="text-subtitle-1 font-weight-bold">
                    Payroll Schedule
                  </v-card-title>
                  <v-divider></v-divider>
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-select
                          v-model="settings.payFrequency"
                          :items="payFrequencyOptions"
                          label="Pay Frequency"
                          item-title="text"
                          item-value="value"
                          variant="outlined"
                          density="comfortable"
                        ></v-select>
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-select
                          v-model="settings.payDay"
                          :items="daysOfWeek"
                          label="Pay Day"
                          variant="outlined"
                          density="comfortable"
                          :disabled="settings.payFrequency === 'monthly'"
                        ></v-select>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>

                <v-card variant="outlined" class="mb-6">
                  <v-card-title class="text-subtitle-1 font-weight-bold">
                    Overtime Rules
                  </v-card-title>
                  <v-divider></v-divider>
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model.number="settings.overtimeThreshold"
                          label="Overtime Threshold (hours per week)"
                          type="number"
                          min="0"
                          step="0.5"
                          variant="outlined"
                          density="comfortable"
                          suffix="hours"
                        ></v-text-field>
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model.number="settings.overtimeRate"
                          label="Overtime Rate Multiplier"
                          type="number"
                          min="1"
                          step="0.1"
                          variant="outlined"
                          density="comfortable"
                          suffix="x"
                        ></v-text-field>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-window-item>

              <!-- Tax Settings Tab -->
              <v-window-item value="taxes">
                <v-card variant="outlined" class="mb-6">
                  <v-card-title class="text-subtitle-1 font-weight-bold">
                    Tax Withholding
                  </v-card-title>
                  <v-divider></v-divider>
                  <v-card-text>
                    <v-row>
                      <v-col cols="12">
                        <v-checkbox
                          v-model="settings.withholdFederalTax"
                          label="Withhold Federal Income Tax"
                          density="comfortable"
                        ></v-checkbox>
                        <v-checkbox
                          v-model="settings.withholdStateTax"
                          label="Withhold State Income Tax"
                          density="comfortable"
                        ></v-checkbox>
                        <v-checkbox
                          v-model="settings.withholdLocalTax"
                          label="Withhold Local Income Tax"
                          density="comfortable"
                        ></v-checkbox>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </v-window-item>

              <!-- Deductions Tab -->
              <v-window-item value="deductions">
                <v-card variant="outlined" class="mb-6">
                  <v-card-title class="d-flex justify-space-between align-center">
                    <span class="text-subtitle-1 font-weight-bold">Pre-tax Deductions</span>
                    <v-btn
                      color="primary"
                      variant="tonal"
                      size="small"
                      prepend-icon="mdi-plus"
                      @click="addDeduction('preTax')"
                    >
                      Add Deduction
                    </v-btn>
                  </v-card-title>
                  <v-divider></v-divider>
                  <v-card-text>
                    <v-data-table
                      :headers="deductionHeaders"
                      :items="settings.preTaxDeductions"
                      :items-per-page="5"
                      class="elevation-1"
                    >
                      <template v-slot:item.actions="{ item }">
                        <v-icon
                          size="small"
                          class="me-2"
                          @click="editDeduction(item, 'preTax')"
                        >
                          mdi-pencil
                        </v-icon>
                        <v-icon
                          size="small"
                          @click="deleteDeduction(item, 'preTax')"
                        >
                          mdi-delete
                        </v-icon>
                      </template>
                    </v-data-table>
                  </v-card-text>
                </v-card>
              </v-window-item>

              <!-- Benefits Tab -->
              <v-window-item value="benefits">
                <v-card variant="outlined" class="mb-6">
                  <v-card-title class="d-flex justify-space-between align-center">
                    <span class="text-subtitle-1 font-weight-bold">Employee Benefits</span>
                    <v-btn
                      color="primary"
                      variant="tonal"
                      size="small"
                      prepend-icon="mdi-plus"
                      @click="addBenefit"
                    >
                      Add Benefit
                    </v-btn>
                  </v-card-title>
                  <v-divider></v-divider>
                  <v-card-text>
                    <v-data-table
                      :headers="benefitHeaders"
                      :items="settings.benefits"
                      :items-per-page="5"
                      class="elevation-1"
                    >
                      <template v-slot:item.actions="{ item }">
                        <v-icon
                          size="small"
                          class="me-2"
                          @click="editBenefit(item)"
                        >
                          mdi-pencil
                        </v-icon>
                        <v-icon
                          size="small"
                          @click="deleteBenefit(item)"
                        >
                          mdi-delete
                        </v-icon>
                      </template>
                    </v-data-table>
                  </v-card-text>
                </v-card>
              </v-window-item>
            </v-window>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';

const { showSnackbar } = useSnackbar();
const isSaving = ref(false);
const activeTab = ref('general');

// Settings data
const settings = reactive({
  // General
  payFrequency: 'biweekly',
  payDay: 'Friday',
  autoProcessPayroll: true,
  notifyEmployees: true,
  
  // Overtime
  overtimeThreshold: 40,
  overtimeRate: 1.5,
  
  // Tax
  withholdFederalTax: true,
  withholdStateTax: true,
  withholdLocalTax: false,
  
  // Deductions
  preTaxDeductions: [
    { id: 1, name: 'Health Insurance', type: 'insurance', calculationType: 'fixed', amount: 200 },
    { id: 2, name: 'Dental Insurance', type: 'insurance', calculationType: 'fixed', amount: 25 },
  ],
  
  // Benefits
  benefits: [
    { 
      id: 1, 
      name: 'Health Insurance', 
      coverageType: 'health', 
      calculationType: 'fixed',
      employeeCost: 200,
      employerCost: 500,
    },
  ],
});

// Options
const payFrequencyOptions = [
  { text: 'Weekly', value: 'weekly' },
  { text: 'Bi-Weekly', value: 'biweekly' },
  { text: 'Semi-Monthly', value: 'semimonthly' },
  { text: 'Monthly', value: 'monthly' },
];

const daysOfWeek = [
  'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
];

const deductionTypes = [
  'insurance', 'retirement', 'garnishment', 'loan', 'other'
];

const coverageTypes = [
  { text: 'Health', value: 'health' },
  { text: 'Dental', value: 'dental' },
  { text: 'Vision', value: 'vision' },
  { text: 'Life Insurance', value: 'life_insurance' },
  { text: 'Disability', value: 'disability' },
  { text: 'Other', value: 'other' },
];

// Table Headers
const deductionHeaders = [
  { title: 'Name', key: 'name' },
  { title: 'Type', key: 'type' },
  { title: 'Amount', key: 'amount' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' },
];

const benefitHeaders = [
  { title: 'Name', key: 'name' },
  { title: 'Coverage Type', key: 'coverageType' },
  { title: 'Employee Cost', key: 'employeeCost' },
  { title: 'Employer Cost', key: 'employerCost' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' },
];

// Methods
const saveSettings = async () => {
  try {
    isSaving.value = true;
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    showSnackbar('Settings saved successfully', 'success');
  } catch (error) {
    console.error('Error saving settings:', error);
    showSnackbar('Failed to save settings', 'error');
  } finally {
    isSaving.value = false;
  }
};

const addDeduction = (type: string) => {
  // Implementation for adding a deduction
  console.log('Add deduction:', type);
};

const editDeduction = (item: any, type: string) => {
  // Implementation for editing a deduction
  console.log('Edit deduction:', item, type);
};

const deleteDeduction = (item: any, type: string) => {
  // Implementation for deleting a deduction
  console.log('Delete deduction:', item, type);
};

const addBenefit = () => {
  // Implementation for adding a benefit
  console.log('Add benefit');
};

const editBenefit = (item: any) => {
  // Implementation for editing a benefit
  console.log('Edit benefit:', item);
};

const deleteBenefit = (item: any) => {
  // Implementation for deleting a benefit
  console.log('Delete benefit:', item);
};

// Lifecycle Hooks
onMounted(() => {
  // Load settings from API
});
</script>
