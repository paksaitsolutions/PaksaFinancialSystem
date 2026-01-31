<template>
  <v-container fluid class="pa-6">
    <!-- Page Header -->
    <v-row class="mb-6" align="center">
      <v-col cols="12" sm="6" md="8">
        <h1 class="text-h4 font-weight-bold">Payroll Taxes</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Manage tax settings, calculations, and filings
        </p>
      </v-col>
      <v-col cols="12" sm="6" md="4" class="text-right">
        <v-btn
          color="primary"
          variant="outlined"
          class="mr-2"
          @click="refreshTaxData"
          :loading="isLoading"
        >
          <v-icon start>mdi-refresh</v-icon>
          Refresh
        </v-btn>
        <v-btn
          color="primary"
          @click="showTaxRuleDialog = true"
        >
          <v-icon start>mdi-plus</v-icon>
          Add Tax Rule
        </v-btn>
      </v-col>
    </v-row>

    <!-- Tax Summary Cards -->
    <v-row class="mb-6">
      <v-col cols="12" md="4">
        <v-card class="h-100" color="primary" variant="tonal">
          <v-card-text class="text-center">
            <div class="text-subtitle-1 text-medium-emphasis">Total Tax Liability</div>
            <div class="text-h4 font-weight-bold">{{ formatCurrency(taxSummary.totalLiability) }}</div>
            <v-divider class="my-3"></v-divider>
            <div class="d-flex justify-space-between">
              <div class="text-caption">YTD Paid</div>
              <div class="text-caption">{{ formatCurrency(taxSummary.ytdPaid) }}</div>
            </div>
            <div class="d-flex justify-space-between">
              <div class="text-caption">Upcoming Payment</div>
              <div class="text-caption">{{ formatCurrency(taxSummary.upcomingPayment) }}</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="h-100" color="secondary" variant="tonal">
          <v-card-text class="text-center">
            <div class="text-subtitle-1 text-medium-emphasis">Tax Types</div>
            <div class="d-flex justify-center align-center">
              <v-progress-circular
                :model-value="taxSummary.complianceRate"
                :size="120"
                :width="12"
                :color="taxSummary.complianceRate > 90 ? 'success' : taxSummary.complianceRate > 70 ? 'warning' : 'error'"
              >
                <div class="text-center">
                  <div class="text-h5">{{ taxSummary.complianceRate }}%</div>
                  <div class="text-caption">Compliant</div>
                </div>
              </v-progress-circular>
            </div>
            <v-divider class="my-3"></v-divider>
            <div class="d-flex justify-space-between">
              <div class="text-caption">{{ taxSummary.activeRules }} Active Rules</div>
              <div class="text-caption">{{ taxSummary.taxTypes }} Tax Types</div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="h-100" color="info" variant="tonal">
          <v-card-text class="text-center">
            <div class="text-subtitle-1 text-medium-emphasis">Upcoming Filings</div>
            <v-list bg-color="transparent" class="mt-2">
              <v-list-item
                v-for="(filing, index) in upcomingFilings"
                :key="index"
                :title="filing.name"
                :subtitle="`Due: ${formatDate(filing.dueDate)}`"
                :class="{ 'text-error': isDueSoon(filing.dueDate) }"
              >
                <template v-slot:prepend>
                  <v-avatar :color="isDueSoon(filing.dueDate) ? 'error' : 'primary'" size="small">
                    <v-icon size="small">mdi-file-document-outline</v-icon>
                  </v-avatar>
                </template>
                <template v-slot:append>
                  <v-btn
                    icon
                    size="x-small"
                    variant="text"
                    color="primary"
                    @click="fileTax(filing)"
                  >
                    <v-icon>mdi-file-export</v-icon>
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>
            <v-btn
              v-if="upcomingFilings.length === 0"
              variant="text"
              color="primary"
              size="small"
              class="mt-2"
            >
              No upcoming filings
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tax Calculation Tools -->
    <v-row class="mb-6">
      <v-col cols="12" md="6">
        <v-card class="h-100">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-calculator</v-icon>
            <span>Tax Calculation Example</span>
          </v-card-title>
          <v-card-text>
            <v-select
              v-model="selectedTaxRuleId"
              :items="taxRules"
              item-title="name"
              item-value="id"
              label="Select Tax Rule"
              variant="outlined"
              density="comfortable"
              class="mb-4"
              :disabled="taxRules.length === 0"
            ></v-select>
            
            <v-text-field
              v-model="taxExampleAmount"
              label="Amount"
              type="number"
              variant="outlined"
              density="comfortable"
              prefix="$"
              class="mb-4"
              :disabled="!selectedTaxRuleId"
            ></v-text-field>
            
            <v-btn
              color="primary"
              block
              :disabled="!selectedTaxRuleId || !taxExampleAmount"
              @click="calculateTaxExample"
              :loading="isCalculating"
            >
              Calculate Tax
            </v-btn>
            
            <v-alert
              v-if="taxCalculationResult"
              class="mt-4"
              :color="taxCalculationResult.type"
              variant="tonal"
            >
              <div class="d-flex align-center">
                <v-icon class="mr-2">mdi-information</v-icon>
                <div>
                  <div class="text-subtitle-2">{{ taxCalculationResult.title }}</div>
                  <div class="text-body-2 mt-1">{{ taxCalculationResult.message }}</div>
                  <div class="text-h6 mt-2">{{ taxCalculationResult.amount }}</div>
                </div>
              </div>
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-card class="h-100">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-account-cash</v-icon>
            <span>Withholding Calculator</span>
          </v-card-title>
          <v-card-text>
            <v-select
              v-model="withholdingState"
              :items="usStates"
              item-title="name"
              item-value="abbr"
              label="State"
              variant="outlined"
              density="comfortable"
              class="mb-4"
            ></v-select>
            
            <v-select
              v-model="withholdingFrequency"
              :items="payFrequencies"
              item-title="text"
              item-value="value"
              label="Pay Frequency"
              variant="outlined"
              density="comfortable"
              class="mb-4"
            ></v-select>
            
            <v-text-field
              v-model="grossPay"
              label="Gross Pay"
              type="number"
              variant="outlined"
              density="comfortable"
              prefix="$"
              class="mb-4"
            ></v-text-field>
            
            <v-text-field
              v-model="withholdingAllowances"
              label="Withholding Allowances"
              type="number"
              variant="outlined"
              density="comfortable"
              class="mb-4"
            ></v-text-field>
            
            <v-btn
              color="primary"
              block
              :disabled="!grossPay"
              @click="calculateWithholding"
              :loading="isCalculating"
            >
              Calculate Withholding
            </v-btn>
            
            <v-alert
              v-if="withholdingResult"
              class="mt-4"
              color="info"
              variant="tonal"
            >
              <div class="d-flex flex-column">
                <div class="d-flex justify-space-between mb-2">
                  <span>Federal Income Tax:</span>
                  <span class="font-weight-bold">{{ formatCurrency(withholdingResult.federal) }}</span>
                </div>
                <div class="d-flex justify-space-between mb-2">
                  <span>State Income Tax ({{ withholdingState || 'N/A' }}):</span>
                  <span class="font-weight-bold">{{ formatCurrency(withholdingResult.state) }}</span>
                </div>
                <div class="d-flex justify-space-between mb-2">
                  <span>Social Security (6.2%):</span>
                  <span class="font-weight-bold">{{ formatCurrency(withholdingResult.socialSecurity) }}</span>
                </div>
                <div class="d-flex justify-space-between mb-2">
                  <span>Medicare (1.45%):</span>
                  <span class="font-weight-bold">{{ formatCurrency(withholdingResult.medicare) }}</span>
                </div>
                <v-divider class="my-2"></v-divider>
                <div class="d-flex justify-space-between text-h6">
                  <span>Net Pay:</span>
                  <span class="font-weight-bold">{{ formatCurrency(withholdingResult.netPay) }}</span>
                </div>
              </div>
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Tax Rules Table -->
    <v-card class="mb-6">
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-format-list-checks</v-icon>
        <span>Tax Rules</span>
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          label="Search tax rules"
          single-line
          hide-details
          variant="outlined"
          density="compact"
          style="max-width: 300px;"
        ></v-text-field>
      </v-card-title>
      <v-divider></v-divider>
      <v-data-table
        :headers="taxRuleHeaders"
        :items="taxRules"
        :search="search"
        :loading="isLoading"
        :items-per-page="10"
        class="elevation-1"
      >
        <template v-slot:item.active="{ item }">
          <v-switch
            v-model="item.raw.active"
            color="primary"
            hide-details
            @change="updateTaxRuleStatus(item.raw)"
          ></v-switch>
        </template>
        <template v-slot:item.rate="{ item }">
          {{ formatTaxRate(item.raw) }}
        </template>
        <template v-slot:item.wageBase="{ item }">
          {{ item.raw.wageBase ? formatCurrency(item.raw.wageBase) : 'No limit' }}
        </template>
        <template v-slot:item.actions="{ item }">
          <v-tooltip text="Edit Rule" location="top">
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                icon
                variant="text"
                size="small"
                color="primary"
                class="mr-1"
                @click="editTaxRule(item.raw)"
              >
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
            </template>
          </v-tooltip>
          <v-tooltip text="Delete Rule" location="top">
            <template v-slot:activator="{ props }">
              <v-btn
                v-bind="props"
                icon
                variant="text"
                size="small"
                color="error"
                @click="confirmDeleteTaxRule(item.raw)"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </template>
          </v-tooltip>
        </template>
      </v-data-table>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useSnackbar } from '@/composables/useSnackbar';
import { useTaxStore } from '@/modules/payroll/stores/taxStore';

// Types
interface TaxRule {
  id: string;
  name: string;
  type: 'federal' | 'state' | 'local' | 'fica' | 'other';
  rate: number;
  calculationType: 'percentage' | 'fixed' | 'tiered' | 'progressive';
  wageBase?: number;
  active?: boolean;
  description?: string;
}

interface TaxSummary {
  totalLiability: number;
  ytdPaid: number;
  upcomingPayment: number;
}

interface CalculationExample {
  grossPay: number;
  federalTax: number;
  stateTax: number;
  socialSecurity: number;
  medicare: number;
  netPay: number;
  taxRule?: TaxRule;
}

interface WithholdingResult {
  federalWithholding: number;
  stateWithholding: number;
  socialSecurity: number;
  medicare: number;
  netPay: number;
  effectiveTaxRate: number;
}

const router = useRouter();
const { showSnackbar } = useSnackbar();
const taxStore = useTaxStore();

// Refs
const selectedTaxRuleId = ref('');
const taxExampleAmount = ref('');
const taxRuleForm = ref<HTMLFormElement | null>(null);
const isLoading = ref(false);

// State
const taxRules = ref<TaxRule[]>([]);
const taxSummary = reactive<TaxSummary>({
  totalLiability: 0,
  ytdPaid: 0,
  upcomingPayment: 0
});

const calculationExample = reactive<CalculationExample>({
  grossPay: 0,
  federalTax: 0,
  stateTax: 0,
  socialSecurity: 0,
  medicare: 0,
  netPay: 0
});

const withholdingCalculator = reactive({
  grossPay: 0,
  filingStatus: 'single' as 'single' | 'married' | 'head_of_household',
  payFrequency: 'monthly' as 'weekly' | 'biweekly' | 'semimonthly' | 'monthly' | 'quarterly' | 'semiannually' | 'annually',
  allowances: 0,
  state: 'CA',
  additionalWithholding: 0,
  result: null as WithholdingResult | null
});

// ... (rest of the code remains the same)

// Calculate tax example - used in template
const calculateTaxExample = (): void => {
  if (!selectedTaxRuleId.value || !taxExampleAmount.value) return;

  const rule = taxRules.value.find((r: TaxRule) => r.id === selectedTaxRuleId.value);
  const amount = parseFloat(taxExampleAmount.value);

  if (!rule) {
    showSnackbar('Selected tax rule not found', 'error');
    return;
  }

  // Simple calculation for example
  const taxAmount = amount * (rule.rate / 100);

  // Update the calculation example
  calculationExample.value = {
    grossPay: amount,
    federalTax: rule.type === 'federal' ? taxAmount : 0,
    stateTax: rule.type === 'state' ? taxAmount : 0,
    socialSecurity: rule.name === 'Social Security' ? taxAmount : 0,
    medicare: rule.name === 'Medicare' ? taxAmount : 0,
    netPay: amount - taxAmount
  };
};

// Format currency helper
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value);
};

// Format percentage helper
const formatPercentage = (value: number): string => {
  return `${value.toFixed(2)}%`;
};

// Calculate withholding
const calculateWithholding = (): void => {
  const { grossPay } = withholdingCalculator;
  
  if (!grossPay || grossPay <= 0) {
    showSnackbar('Please enter a valid gross pay amount', 'error');
    return;
  }
  
  // Simple calculation for demo purposes
  const federalWithholding = grossPay * 0.15; // Simplified
  const stateWithholding = grossPay * 0.05; // Simplified
  const socialSecurity = Math.min(grossPay * 0.062, 160200 * 0.062); // 6.2% up to wage base
  const medicare = grossPay * 0.0145; // 1.45%
  
  const totalTaxes = federalWithholding + stateWithholding + socialSecurity + medicare;
  const netPay = grossPay - totalTaxes;
  const effectiveTaxRate = (totalTaxes / grossPay) * 100;
  
  // Update the result object
  withholdingCalculator.result = {
    federalWithholding,
    stateWithholding,
    socialSecurity,
    medicare,
    netPay,
    effectiveTaxRate
  };
};

// Update tax rule status
const updateTaxRuleStatus = async (rule: TaxRule) => {
  try {
    // In a real app, this would be an API call
    // await payrollApiService.updateTaxRule(rule.id, { active: rule.active });
    showSnackbar('Tax rule updated successfully', 'success');
  } catch (error) {
    console.error('Error updating tax rule status:', error);
    showSnackbar('Failed to update tax rule', 'error');
    // Revert the change on error
    rule.active = !rule.active;
  }
};

// Initial data load
const loadTaxData = async () => {
  isLoading.value = true;
  try {
    // Mock data for development
    taxRules.value = [
      {
        id: 'federal_income',
        name: 'Federal Income Tax',
        type: 'federal',
        rate: 22,
        calculationType: 'progressive',
        active: true
      },
      {
        id: 'social_security',
        name: 'Social Security',
        type: 'fica',
        rate: 6.2,
        calculationType: 'percentage',
        wageBase: 147000,
        active: true
      },
      {
        id: 'medicare',
        name: 'Medicare',
        type: 'fica',
        rate: 1.45,
        calculationType: 'percentage',
        active: true
      }
    ];
    
    // Set initial tax rule for calculation example
    if (taxRules.value.length > 0) {
      selectedTaxRuleId.value = taxRules.value[0].id;
      calculationExample.taxRule = taxRules.value[0];
      calculateTaxExample();
    }
    
    // Initialize tax summary
    taxSummary.totalLiability = 12500;
    taxSummary.ytdPaid = 8500;
    taxSummary.upcomingPayment = 4000;
    
    calculateWithholding();
    isLoading.value = false;
  } catch (error) {
    console.error('Error loading tax data:', error);
    showSnackbar('Failed to load tax data', 'error');
    isLoading.value = false;
  }
};

// Refresh tax data
const refreshTaxData = () => {
  loadTaxData();
};

// Initialize component
onMounted(() => {
  loadTaxData();
});
</script>
