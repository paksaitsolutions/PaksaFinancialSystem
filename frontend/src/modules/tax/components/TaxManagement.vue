<template>
  <div class="tax-management">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Tax Management</h1>
        <p class="text-color-secondary">Manage tax rates, exemptions, and calculations</p>
      </div>
    </div>
    
    <TabView v-model:activeIndex="activeTab">
      <TabPanel header="Tax Rates">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Tax Rates</span>
              <Button label="Add Tax Rate" icon="pi pi-plus" @click="openTaxRateDialog" />
            </div>
          </template>
          <template #content>
            <DataTable :value="taxRates" :loading="loadingRates" paginator :rows="10">
              <Column field="name" header="Name" sortable />
              <Column field="code" header="Code" sortable />
              <Column field="rate" header="Rate" sortable>
                <template #body="{ data }">
                  {{ (data.rate * 100).toFixed(2) }}%
                </template>
              </Column>
              <Column field="tax_type" header="Type" sortable />
              <Column field="jurisdiction" header="Jurisdiction" sortable />
              <Column field="is_active" header="Status" sortable>
                <template #body="{ data }">
                  <Tag :value="data.is_active ? 'Active' : 'Inactive'" :severity="data.is_active ? 'success' : 'danger'" />
                </template>
              </Column>
              <Column header="Actions">
                <template #body="{ data }">
                  <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editTaxRate(data)" />
                  <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="deleteTaxRate(data)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>
      
      <TabPanel header="Exemptions">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Tax Exemptions</span>
              <Button label="Add Exemption" icon="pi pi-plus" @click="openExemptionDialog" />
            </div>
          </template>
          <template #content>
            <DataTable :value="exemptions" :loading="loadingExemptions" paginator :rows="10">
              <Column field="certificate_number" header="Certificate #" sortable />
              <Column field="exemption_type" header="Type" sortable />
              <Column field="tax_type" header="Tax Type" sortable />
              <Column field="is_active" header="Status" sortable>
                <template #body="{ data }">
                  <Tag :value="data.is_active ? 'Active' : 'Inactive'" :severity="data.is_active ? 'success' : 'danger'" />
                </template>
              </Column>
              <Column header="Actions">
                <template #body="{ data }">
                  <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editExemption(data)" />
                  <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="deleteExemption(data)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>
      
      <TabPanel header="Tax Calculator">
        <Card>
          <template #title>Tax Calculator</template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label>Amount</label>
                  <InputNumber v-model="calculator.amount" mode="currency" currency="USD" class="w-full" />
                </div>
              </div>
              
              <div class="col-12 md:col-6">
                <div class="field">
                  <label>Tax Type</label>
                  <Dropdown v-model="calculator.tax_type" :options="taxTypes" optionLabel="title" optionValue="value" placeholder="Select Tax Type" class="w-full" />
                </div>
              </div>
              
              <div class="col-12 md:col-6">
                <div class="field">
                  <label>Jurisdiction (Optional)</label>
                  <InputText v-model="calculator.jurisdiction" class="w-full" />
                </div>
              </div>
              
              <div class="col-12 md:col-6">
                <div class="field">
                  <label>&nbsp;</label>
                  <Button label="Calculate Tax" icon="pi pi-calculator" :loading="calculatingTax" @click="calculateTax" class="w-full" />
                </div>
              </div>
            </div>
            
            <div v-if="taxResult" class="mt-4">
              <Card>
                <template #title>Tax Calculation Result</template>
                <template #content>
                  <div class="grid">
                    <div class="col-12 md:col-4">
                      <div class="text-center">
                        <div class="text-2xl font-bold">{{ formatCurrency(taxResult.subtotal) }}</div>
                        <div class="text-color-secondary">Subtotal</div>
                      </div>
                    </div>
                    <div class="col-12 md:col-4">
                      <div class="text-center">
                        <div class="text-2xl font-bold">{{ formatCurrency(taxResult.tax_amount) }}</div>
                        <div class="text-color-secondary">Tax Amount</div>
                      </div>
                    </div>
                    <div class="col-12 md:col-4">
                      <div class="text-center">
                        <div class="text-2xl font-bold">{{ formatCurrency(taxResult.total_amount) }}</div>
                        <div class="text-color-secondary">Total Amount</div>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="taxResult.tax_details && taxResult.tax_details.length > 0" class="mt-4">
                    <h4>Tax Breakdown:</h4>
                    <div v-for="detail in taxResult.tax_details" :key="detail.tax_rate_id" class="flex justify-content-between mt-2">
                      <span>{{ detail.name }} ({{ (detail.rate * 100).toFixed(2) }}%)</span>
                      <span>{{ formatCurrency(detail.amount) }}</span>
                    </div>
                  </div>
                </template>
              </Card>
            </div>
          </template>
        </Card>
      </TabPanel>

      <TabPanel header="Nexus Tracking">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Sales Tax Nexus</span>
              <Button label="Add Nexus" icon="pi pi-plus" @click="openNexusDialog" />
            </div>
          </template>
          <template #content>
            <DataTable :value="nexusEntries" :loading="loadingNexus" paginator :rows="10">
              <Column field="jurisdiction" header="Jurisdiction" sortable />
              <Column field="nexus_type" header="Type" sortable />
              <Column field="effective_date" header="Effective Date" sortable />
              <Column field="threshold_amount" header="Threshold" sortable>
                <template #body="{ data }">
                  {{ formatCurrency(data.threshold_amount) }}
                </template>
              </Column>
              <Column field="current_sales" header="Current Sales" sortable>
                <template #body="{ data }">
                  {{ formatCurrency(data.current_sales) }}
                </template>
              </Column>
              <Column field="status" header="Status" sortable>
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="data.status === 'active' ? 'success' : 'info'" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>

      <TabPanel header="Automation Rules">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Tax Automation Rules</span>
              <Button label="Add Rule" icon="pi pi-plus" @click="openRuleDialog" />
            </div>
          </template>
          <template #content>
            <DataTable :value="automationRules" :loading="loadingRules" paginator :rows="10">
              <Column field="name" header="Rule" sortable />
              <Column field="trigger_event" header="Trigger" sortable />
              <Column field="action" header="Action" sortable />
              <Column field="tax_type" header="Tax Type" sortable />
              <Column field="is_active" header="Status" sortable>
                <template #body="{ data }">
                  <Tag :value="data.is_active ? 'Active' : 'Disabled'" :severity="data.is_active ? 'success' : 'warning'" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>

      <TabPanel header="E-Filing Integration">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>E-Filing Providers</span>
              <Button label="Add Provider" icon="pi pi-plus" @click="openEFilingDialog" />
            </div>
          </template>
          <template #content>
            <DataTable :value="efilingIntegrations" :loading="loadingEFiling" paginator :rows="10">
              <Column field="provider" header="Provider" sortable />
              <Column field="environment" header="Environment" sortable />
              <Column field="status" header="Status" sortable>
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="data.status === 'configured' ? 'success' : 'info'" />
                </template>
              </Column>
              <Column field="last_sync_at" header="Last Sync" sortable />
            </DataTable>
          </template>
        </Card>
      </TabPanel>

      <TabPanel header="Payment Scheduling">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Tax Payment Schedules</span>
              <Button label="Schedule Payment" icon="pi pi-plus" @click="openPaymentDialog" />
            </div>
          </template>
          <template #content>
            <DataTable :value="paymentSchedules" :loading="loadingSchedules" paginator :rows="10">
              <Column field="jurisdiction" header="Jurisdiction" sortable />
              <Column field="scheduled_date" header="Scheduled Date" sortable />
              <Column field="amount" header="Amount" sortable>
                <template #body="{ data }">
                  {{ formatCurrency(data.amount) }}
                </template>
              </Column>
              <Column field="payment_method" header="Method" sortable />
              <Column field="status" header="Status" sortable>
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="data.status === 'paid' ? 'success' : 'info'" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>
      
      <TabPanel header="Reports">
        <Card>
          <template #title>Tax Reports</template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-4">
                <Button label="Tax Summary Report" icon="pi pi-chart-bar" class="w-full" @click="generateTaxSummaryReport" />
              </div>
              <div class="col-12 md:col-4">
                <Button label="Tax Rate Analysis" icon="pi pi-table" class="w-full p-button-secondary" @click="generateTaxRateAnalysis" />
              </div>
              <div class="col-12 md:col-4">
                <Button label="Exemption Report" icon="pi pi-verified" class="w-full p-button-info" @click="generateExemptionReport" />
              </div>
            </div>
          </template>
        </Card>
      </TabPanel>
    </TabView>
    
    <!-- Tax Rate Dialog -->
    <Dialog v-model:visible="taxRateDialog.show" header="Tax Rate Details" :modal="true" :style="{width: '600px'}">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Name</label>
            <InputText v-model="taxRateDialog.formData.name" class="w-full" :class="{'p-invalid': submitted && !taxRateDialog.formData.name}" />
            <small class="p-error" v-if="submitted && !taxRateDialog.formData.name">Name is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Code</label>
            <InputText v-model="taxRateDialog.formData.code" class="w-full" :class="{'p-invalid': submitted && !taxRateDialog.formData.code}" />
            <small class="p-error" v-if="submitted && !taxRateDialog.formData.code">Code is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Rate (%)</label>
            <InputNumber v-model="taxRateDialog.formData.rate" :minFractionDigits="2" :maxFractionDigits="4" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Tax Type</label>
            <Dropdown v-model="taxRateDialog.formData.tax_type" :options="taxTypes" optionLabel="title" optionValue="value" placeholder="Select Tax Type" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Jurisdiction</label>
            <InputText v-model="taxRateDialog.formData.jurisdiction" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Description</label>
            <Textarea v-model="taxRateDialog.formData.description" rows="2" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="taxRateDialog.show = false" />
        <Button :label="taxRateDialog.isEdit ? 'Update' : 'Create'" :loading="taxRateDialog.saving" @click="saveTaxRate" />
      </template>
    </Dialog>

    <Dialog v-model:visible="nexusDialog.show" header="Nexus Tracking" :modal="true" :style="{width: '520px'}">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Jurisdiction</label>
            <InputText v-model="nexusDialog.formData.jurisdiction" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Nexus Type</label>
            <Dropdown v-model="nexusDialog.formData.nexus_type" :options="nexusTypes" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Effective Date</label>
            <InputText v-model="nexusDialog.formData.effective_date" placeholder="YYYY-MM-DD" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Threshold Amount</label>
            <InputNumber v-model="nexusDialog.formData.threshold_amount" mode="currency" currency="USD" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Current Sales</label>
            <InputNumber v-model="nexusDialog.formData.current_sales" mode="currency" currency="USD" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Status</label>
            <Dropdown v-model="nexusDialog.formData.status" :options="nexusStatuses" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="nexusDialog.show = false" />
        <Button label="Save" :loading="nexusDialog.saving" @click="saveNexus" />
      </template>
    </Dialog>

    <Dialog v-model:visible="ruleDialog.show" header="Automation Rule" :modal="true" :style="{width: '520px'}">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label>Rule Name</label>
            <InputText v-model="ruleDialog.formData.name" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Tax Type</label>
            <Dropdown v-model="ruleDialog.formData.tax_type" :options="taxTypes" optionLabel="title" optionValue="value" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Trigger</label>
            <InputText v-model="ruleDialog.formData.trigger_event" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Action</label>
            <InputText v-model="ruleDialog.formData.action" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="ruleDialog.show = false" />
        <Button label="Save" :loading="ruleDialog.saving" @click="saveRule" />
      </template>
    </Dialog>

    <Dialog v-model:visible="efilingDialog.show" header="E-Filing Provider" :modal="true" :style="{width: '520px'}">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label>Provider</label>
            <InputText v-model="efilingDialog.formData.provider" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Environment</label>
            <Dropdown v-model="efilingDialog.formData.environment" :options="efilingEnvironments" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Status</label>
            <Dropdown v-model="efilingDialog.formData.status" :options="efilingStatuses" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="efilingDialog.show = false" />
        <Button label="Save" :loading="efilingDialog.saving" @click="saveEFiling" />
      </template>
    </Dialog>

    <Dialog v-model:visible="paymentDialog.show" header="Tax Payment Schedule" :modal="true" :style="{width: '520px'}">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label>Jurisdiction</label>
            <InputText v-model="paymentDialog.formData.jurisdiction" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Scheduled Date</label>
            <InputText v-model="paymentDialog.formData.scheduled_date" placeholder="YYYY-MM-DD" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Amount</label>
            <InputNumber v-model="paymentDialog.formData.amount" mode="currency" currency="USD" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Payment Method</label>
            <InputText v-model="paymentDialog.formData.payment_method" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Status</label>
            <Dropdown v-model="paymentDialog.formData.status" :options="paymentStatuses" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="paymentDialog.show = false" />
        <Button label="Save" :loading="paymentDialog.saving" @click="savePaymentSchedule" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { taxApiService } from '../services/taxApiService';

const toast = useToast();

// Data
const activeTab = ref(0);
const submitted = ref(false);
const taxRates = ref([]);
const exemptions = ref([]);
const loadingRates = ref(false);
const loadingExemptions = ref(false);
const calculatingTax = ref(false);
const taxResult = ref(null);
const nexusEntries = ref([]);
const automationRules = ref([]);
const efilingIntegrations = ref([]);
const paymentSchedules = ref([]);
const loadingNexus = ref(false);
const loadingRules = ref(false);
const loadingEFiling = ref(false);
const loadingSchedules = ref(false);

// Tax Rate Dialog
const taxRateDialog = reactive({
  show: false,
  isEdit: false,
  valid: false,
  saving: false,
  formData: {
    name: '',
    code: '',
    rate: 0,
    tax_type: '',
    jurisdiction: '',
    description: '',
  },
  editId: null,
});

const nexusDialog = reactive({
  show: false,
  saving: false,
  formData: {
    jurisdiction: '',
    nexus_type: 'economic',
    effective_date: '',
    threshold_amount: 0,
    current_sales: 0,
    status: 'tracking',
  },
});

const ruleDialog = reactive({
  show: false,
  saving: false,
  formData: {
    name: '',
    tax_type: 'sales',
    trigger_event: 'return_due',
    action: 'notify',
  },
});

const efilingDialog = reactive({
  show: false,
  saving: false,
  formData: {
    provider: '',
    environment: 'sandbox',
    status: 'configured',
  },
});

const paymentDialog = reactive({
  show: false,
  saving: false,
  formData: {
    jurisdiction: '',
    scheduled_date: '',
    amount: 0,
    payment_method: '',
    status: 'scheduled',
  },
});

// Calculator
const calculator = reactive({
  amount: 0,
  tax_type: '',
  jurisdiction: '',
});

// Headers
const taxRateHeaders = [
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Code', key: 'code', sortable: true },
  { title: 'Rate', key: 'rate', sortable: true },
  { title: 'Type', key: 'tax_type', sortable: true },
  { title: 'Jurisdiction', key: 'jurisdiction', sortable: true },
  { title: 'Status', key: 'is_active', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false },
];

const exemptionHeaders = [
  { title: 'Certificate #', key: 'certificate_number', sortable: true },
  { title: 'Type', key: 'exemption_type', sortable: true },
  { title: 'Tax Type', key: 'tax_type', sortable: true },
  { title: 'Status', key: 'is_active', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false },
];

const taxTypes = [
  { title: 'Sales Tax', value: 'sales' },
  { title: 'VAT', value: 'vat' },
  { title: 'GST', value: 'gst' },
  { title: 'Income Tax', value: 'income' },
];

const nexusTypes = [
  { label: 'Economic', value: 'economic' },
  { label: 'Physical', value: 'physical' },
  { label: 'Marketplace', value: 'marketplace' },
];

const nexusStatuses = [
  { label: 'Tracking', value: 'tracking' },
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
];

const efilingEnvironments = [
  { label: 'Sandbox', value: 'sandbox' },
  { label: 'Production', value: 'production' },
];

const efilingStatuses = [
  { label: 'Configured', value: 'configured' },
  { label: 'Pending', value: 'pending' },
  { label: 'Error', value: 'error' },
];

const paymentStatuses = [
  { label: 'Scheduled', value: 'scheduled' },
  { label: 'Paid', value: 'paid' },
  { label: 'Failed', value: 'failed' },
];

// Methods
const fetchTaxRates = async () => {
  loadingRates.value = true;
  try {
    // Mock data
    taxRates.value = [
      { id: '1', name: 'Sales Tax', code: 'ST', rate: 0.08, tax_type: 'sales', jurisdiction: 'State', is_active: true },
      { id: '2', name: 'VAT', code: 'VAT', rate: 0.20, tax_type: 'vat', jurisdiction: 'Federal', is_active: true },
      { id: '3', name: 'GST', code: 'GST', rate: 0.15, tax_type: 'gst', jurisdiction: 'Provincial', is_active: false }
    ];
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load tax rates', life: 3000 });
  } finally {
    loadingRates.value = false;
  }
};

const fetchNexus = async () => {
  loadingNexus.value = true;
  try {
    nexusEntries.value = await taxApiService.getSalesTaxNexus();
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load nexus tracking', life: 3000 });
  } finally {
    loadingNexus.value = false;
  }
};

const fetchAutomationRules = async () => {
  loadingRules.value = true;
  try {
    automationRules.value = await taxApiService.getAutomationRules();
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load automation rules', life: 3000 });
  } finally {
    loadingRules.value = false;
  }
};

const fetchEFilingIntegrations = async () => {
  loadingEFiling.value = true;
  try {
    efilingIntegrations.value = await taxApiService.getEFilingIntegrations();
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load e-filing integrations', life: 3000 });
  } finally {
    loadingEFiling.value = false;
  }
};

const fetchPaymentSchedules = async () => {
  loadingSchedules.value = true;
  try {
    paymentSchedules.value = await taxApiService.getPaymentSchedules();
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load payment schedules', life: 3000 });
  } finally {
    loadingSchedules.value = false;
  }
};

const fetchExemptions = async () => {
  loadingExemptions.value = true;
  try {
    // Mock data
    exemptions.value = [
      { id: '1', certificate_number: 'EX001', exemption_type: 'Non-Profit', tax_type: 'sales', is_active: true },
      { id: '2', certificate_number: 'EX002', exemption_type: 'Government', tax_type: 'vat', is_active: true }
    ];
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load exemptions', life: 3000 });
  } finally {
    loadingExemptions.value = false;
  }
};

const openTaxRateDialog = () => {
  taxRateDialog.isEdit = false;
  taxRateDialog.editId = null;
  taxRateDialog.formData = {
    name: '',
    code: '',
    rate: 0,
    tax_type: '',
    jurisdiction: '',
    description: '',
  };
  taxRateDialog.show = true;
};

const editTaxRate = (taxRate) => {
  taxRateDialog.isEdit = true;
  taxRateDialog.editId = taxRate.id;
  taxRateDialog.formData = {
    name: taxRate.name,
    code: taxRate.code,
    rate: taxRate.rate * 100, // Convert to percentage
    tax_type: taxRate.tax_type,
    jurisdiction: taxRate.jurisdiction || '',
    description: taxRate.description || '',
  };
  taxRateDialog.show = true;
};

const saveTaxRate = async () => {
  submitted.value = true;
  if (!taxRateDialog.formData.name || !taxRateDialog.formData.code) return;
  
  taxRateDialog.saving = true;
  try {
    const payload = {
      ...taxRateDialog.formData,
      rate: taxRateDialog.formData.rate / 100, // Convert back to decimal
      effective_date: new Date().toISOString().split('T')[0],
      is_active: true
    };
    
    if (taxRateDialog.isEdit) {
      const index = taxRates.value.findIndex(r => r.id === taxRateDialog.editId);
      if (index !== -1) taxRates.value[index] = { ...payload, id: taxRateDialog.editId };
      toast.add({ severity: 'success', summary: 'Success', detail: 'Tax rate updated successfully', life: 3000 });
    } else {
      payload.id = Date.now().toString();
      taxRates.value.push(payload);
      toast.add({ severity: 'success', summary: 'Success', detail: 'Tax rate created successfully', life: 3000 });
    }
    
    taxRateDialog.show = false;
    submitted.value = false;
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save tax rate', life: 3000 });
  } finally {
    taxRateDialog.saving = false;
  }
};

const calculateTax = async () => {
  if (!calculator.amount || !calculator.tax_type) return;
  
  calculatingTax.value = true;
  try {
    // Mock calculation
    const rate = 0.08; // 8% tax rate
    const subtotal = calculator.amount;
    const tax_amount = subtotal * rate;
    const total_amount = subtotal + tax_amount;
    
    taxResult.value = {
      subtotal,
      tax_amount,
      total_amount,
      tax_details: [
        { tax_rate_id: '1', name: 'Sales Tax', rate, amount: tax_amount }
      ]
    };
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to calculate tax', life: 3000 });
  } finally {
    calculatingTax.value = false;
  }
};

const openExemptionDialog = () => {
  toast.add({ severity: 'info', summary: 'Info', detail: 'Exemption management coming soon', life: 3000 });
};

const editExemption = () => {
  toast.add({ severity: 'info', summary: 'Info', detail: 'Exemption editing coming soon', life: 3000 });
};

const deleteTaxRate = (taxRate: any) => {
  taxRates.value = taxRates.value.filter(r => r.id !== taxRate.id);
  toast.add({ severity: 'success', summary: 'Success', detail: 'Tax rate deleted', life: 3000 });
};

const deleteExemption = (exemption: any) => {
  exemptions.value = exemptions.value.filter(e => e.id !== exemption.id);
  toast.add({ severity: 'success', summary: 'Success', detail: 'Exemption deleted', life: 3000 });
};

const openNexusDialog = () => {
  nexusDialog.formData = {
    jurisdiction: '',
    nexus_type: 'economic',
    effective_date: '',
    threshold_amount: 0,
    current_sales: 0,
    status: 'tracking',
  };
  nexusDialog.show = true;
};

const saveNexus = async () => {
  if (!nexusDialog.formData.jurisdiction || !nexusDialog.formData.effective_date) {
    toast.add({ severity: 'warn', summary: 'Required', detail: 'Jurisdiction and effective date are required', life: 3000 });
    return;
  }
  nexusDialog.saving = true;
  try {
    await taxApiService.createSalesTaxNexus({
      ...nexusDialog.formData,
      company_id: '12345678-1234-5678-9012-123456789012',
      threshold_transactions: 0,
    });
    await fetchNexus();
    nexusDialog.show = false;
    toast.add({ severity: 'success', summary: 'Saved', detail: 'Nexus entry created', life: 3000 });
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save nexus entry', life: 3000 });
  } finally {
    nexusDialog.saving = false;
  }
};

const openRuleDialog = () => {
  ruleDialog.formData = {
    name: '',
    tax_type: 'sales',
    trigger_event: 'return_due',
    action: 'notify',
  };
  ruleDialog.show = true;
};

const saveRule = async () => {
  if (!ruleDialog.formData.name) {
    toast.add({ severity: 'warn', summary: 'Required', detail: 'Rule name is required', life: 3000 });
    return;
  }
  ruleDialog.saving = true;
  try {
    await taxApiService.createAutomationRule({
      ...ruleDialog.formData,
      company_id: '12345678-1234-5678-9012-123456789012',
      jurisdiction: undefined,
      threshold_amount: 0,
      schedule_cron: undefined,
      priority: 1,
      is_active: true,
    });
    await fetchAutomationRules();
    ruleDialog.show = false;
    toast.add({ severity: 'success', summary: 'Saved', detail: 'Automation rule created', life: 3000 });
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save automation rule', life: 3000 });
  } finally {
    ruleDialog.saving = false;
  }
};

const openEFilingDialog = () => {
  efilingDialog.formData = {
    provider: '',
    environment: 'sandbox',
    status: 'configured',
  };
  efilingDialog.show = true;
};

const saveEFiling = async () => {
  if (!efilingDialog.formData.provider) {
    toast.add({ severity: 'warn', summary: 'Required', detail: 'Provider is required', life: 3000 });
    return;
  }
  efilingDialog.saving = true;
  try {
    await taxApiService.createEFilingIntegration({
      ...efilingDialog.formData,
      company_id: '12345678-1234-5678-9012-123456789012',
    });
    await fetchEFilingIntegrations();
    efilingDialog.show = false;
    toast.add({ severity: 'success', summary: 'Saved', detail: 'E-filing integration saved', life: 3000 });
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save e-filing integration', life: 3000 });
  } finally {
    efilingDialog.saving = false;
  }
};

const openPaymentDialog = () => {
  paymentDialog.formData = {
    jurisdiction: '',
    scheduled_date: '',
    amount: 0,
    payment_method: '',
    status: 'scheduled',
  };
  paymentDialog.show = true;
};

const savePaymentSchedule = async () => {
  if (!paymentDialog.formData.scheduled_date) {
    toast.add({ severity: 'warn', summary: 'Required', detail: 'Scheduled date is required', life: 3000 });
    return;
  }
  paymentDialog.saving = true;
  try {
    await taxApiService.createPaymentSchedule({
      ...paymentDialog.formData,
      company_id: '12345678-1234-5678-9012-123456789012',
      tax_return_id: undefined,
    });
    await fetchPaymentSchedules();
    paymentDialog.show = false;
    toast.add({ severity: 'success', summary: 'Saved', detail: 'Payment scheduled', life: 3000 });
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to schedule payment', life: 3000 });
  } finally {
    paymentDialog.saving = false;
  }
};

const generateTaxSummaryReport = () => {
  toast.add({ severity: 'info', summary: 'Report', detail: 'Generating tax summary report...', life: 3000 });
};

const generateTaxRateAnalysis = () => {
  toast.add({ severity: 'info', summary: 'Report', detail: 'Generating tax rate analysis...', life: 3000 });
};

const generateExemptionReport = () => {
  toast.add({ severity: 'info', summary: 'Report', detail: 'Generating exemption report...', life: 3000 });
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount || 0);
};

// Lifecycle hooks
onMounted(() => {
  fetchTaxRates();
  fetchExemptions();
  fetchNexus();
  fetchAutomationRules();
  fetchEFilingIntegrations();
  fetchPaymentSchedules();
});
</script>

<style scoped>
.tax-management {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>
