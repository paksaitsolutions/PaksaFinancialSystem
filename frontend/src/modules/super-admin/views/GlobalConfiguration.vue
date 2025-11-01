<template>
  <div class="configuration-dashboard">
    <!-- Header -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-3xl font-bold text-900 m-0">System Configuration</h1>
        <p class="text-600 mt-1 mb-0">Comprehensive configuration for all modules and system settings</p>
      </div>
      <div class="flex gap-2">
        <Button icon="pi pi-refresh" label="Refresh" @click="loadConfigurations" />
        <Button icon="pi pi-download" label="Export" severity="secondary" @click="exportConfig" />
      </div>
    </div>

    <!-- Tab Navigation -->
    <div class="mb-4">
      <div class="flex gap-2">
        <Button 
          @click="state.activeTab = 0" 
          :severity="state.activeTab === 0 ? 'primary' : 'secondary'"
          :outlined="state.activeTab !== 0"
          label="Platform Settings"
          icon="pi pi-cog"
        />
        <Button 
          @click="state.activeTab = 1" 
          :severity="state.activeTab === 1 ? 'primary' : 'secondary'"
          :outlined="state.activeTab !== 1"
          label="Financial Settings"
          icon="pi pi-dollar"
        />
        <Button 
          @click="state.activeTab = 2" 
          :severity="state.activeTab === 2 ? 'primary' : 'secondary'"
          :outlined="state.activeTab !== 2"
          label="Integration"
          icon="pi pi-link"
        />
      </div>
    </div>

    <div v-if="state.activeTab === 0">
        <div class="grid">
          <div class="col-12 md:col-4">
            <Card>
              <template #title>Platform Configuration</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>Platform Name</label>
                    <InputText v-model="platformConfig.name" class="w-full" />
                  </div>
                  <div>
                    <label>Company Name</label>
                    <InputText v-model="platformConfig.companyName" class="w-full" />
                  </div>
                  <div>
                    <label>Environment</label>
                    <Dropdown v-model="platformConfig.environment" :options="environments" class="w-full" />
                  </div>
                  <div>
                    <label>Default Language</label>
                    <Dropdown 
                      v-model="platformConfig.defaultLanguage" 
                      :options="languages" 
                      optionLabel="label" 
                      optionValue="value"
                      @change="changeLanguage"
                      class="w-full" 
                    />
                  </div>
                  <div>
                    <label>Default Currency</label>
                    <Dropdown v-model="platformConfig.defaultCurrency" :options="currencies" class="w-full" />
                  </div>
                  <div>
                    <label>Time Zone</label>
                    <Dropdown v-model="platformConfig.timeZone" :options="timeZones" class="w-full" />
                  </div>
                  <div>
                    <label>Date Format</label>
                    <Dropdown v-model="platformConfig.dateFormat" :options="dateFormats" class="w-full" />
                  </div>
                  <div>
                    <label>Number Format</label>
                    <Dropdown v-model="platformConfig.numberFormat" :options="numberFormats" class="w-full" />
                  </div>
                  <div>
                    <label>Theme</label>
                    <Dropdown v-model="platformConfig.theme" :options="themes" class="w-full" />
                  </div>
                  <div>
                    <label>Logo URL</label>
                    <InputText v-model="platformConfig.logoUrl" class="w-full" />
                  </div>
                  <div>
                    <label>Support Email</label>
                    <InputText v-model="platformConfig.supportEmail" type="email" class="w-full" />
                  </div>
                  <div>
                    <label>Support Phone</label>
                    <InputText v-model="platformConfig.supportPhone" class="w-full" />
                  </div>
                  <div>
                    <label>Max File Upload Size (MB)</label>
                    <InputNumber v-model="platformConfig.maxFileSize" :min="1" :max="100" class="w-full" />
                  </div>
                  <div>
                    <label>Session Warning Time (minutes)</label>
                    <InputNumber v-model="platformConfig.sessionWarning" :min="1" :max="30" class="w-full" />
                  </div>
                  <div>
                    <label>Auto-save Interval (seconds)</label>
                    <InputNumber v-model="platformConfig.autoSaveInterval" :min="30" :max="300" class="w-full" />
                  </div>
                  <div>
                    <label>Enable Notifications</label>
                    <InputSwitch v-model="platformConfig.enableNotifications" />
                  </div>
                  <div>
                    <label>Enable Dark Mode</label>
                    <InputSwitch v-model="platformConfig.enableDarkMode" />
                  </div>
                  <div>
                    <label>Enable Multi-tenancy</label>
                    <InputSwitch v-model="platformConfig.enableMultiTenancy" />
                  </div>
                  <div>
                    <label>Maintenance Mode</label>
                    <InputSwitch v-model="platformConfig.maintenanceMode" />
                  </div>
                  <div>
                    <label>Debug Mode</label>
                    <InputSwitch v-model="platformConfig.debugMode" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
          <div class="col-12 md:col-4">
            <Card>
              <template #title>Security Settings</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>Session Timeout (minutes)</label>
                    <InputNumber v-model="securityConfig.sessionTimeout" class="w-full" />
                  </div>
                  <div>
                    <label>Max Login Attempts</label>
                    <InputNumber v-model="securityConfig.maxLoginAttempts" class="w-full" />
                  </div>
                  <div>
                    <label>Password Min Length</label>
                    <InputNumber v-model="securityConfig.passwordMinLength" class="w-full" />
                  </div>
                  <div>
                    <label>JWT Expiry (hours)</label>
                    <InputNumber v-model="securityConfig.jwtExpiry" class="w-full" />
                  </div>
                  <div>
                    <label>Enforce SSL</label>
                    <InputSwitch v-model="securityConfig.enforceSSL" />
                  </div>
                  <div>
                    <label>Enable 2FA</label>
                    <InputSwitch v-model="securityConfig.enableTwoFactor" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
          <div class="col-12 md:col-4">
            <Card>
              <template #title>System Performance</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>Cache TTL (minutes)</label>
                    <InputNumber v-model="platformConfig.cacheTTL" :min="1" :max="1440" class="w-full" />
                  </div>
                  <div>
                    <label>Database Pool Size</label>
                    <InputNumber v-model="platformConfig.dbPoolSize" :min="5" :max="100" class="w-full" />
                  </div>
                  <div>
                    <label>Request Timeout (seconds)</label>
                    <InputNumber v-model="platformConfig.requestTimeout" :min="10" :max="300" class="w-full" />
                  </div>
                  <div>
                    <label>Enable Compression</label>
                    <InputSwitch v-model="platformConfig.enableCompression" />
                  </div>
                  <div>
                    <label>Enable Caching</label>
                    <InputSwitch v-model="platformConfig.enableCaching" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
          <div class="col-12 md:col-4">
            <Card>
              <template #title>Audit & Logging</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>Log Level</label>
                    <Dropdown v-model="platformConfig.logLevel" :options="logLevels" class="w-full" />
                  </div>
                  <div>
                    <label>Log Retention (days)</label>
                    <InputNumber v-model="platformConfig.logRetention" :min="1" :max="365" class="w-full" />
                  </div>
                  <div>
                    <label>Enable Audit Trail</label>
                    <InputSwitch v-model="platformConfig.enableAuditTrail" />
                  </div>
                  <div>
                    <label>Enable Performance Monitoring</label>
                    <InputSwitch v-model="platformConfig.enablePerformanceMonitoring" />
                  </div>
                  <div>
                    <label>Enable Error Tracking</label>
                    <InputSwitch v-model="platformConfig.enableErrorTracking" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
    </div>

    <div v-if="state.activeTab === 1">
        <div class="grid">
          <div class="col-12 md:col-4">
            <Card>
              <template #title>General Ledger</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>Fiscal Year Start</label>
                    <Dropdown v-model="financialConfig.fiscalYearStart" :options="months" class="w-full" />
                  </div>
                  <div>
                    <label>Account Code Length</label>
                    <InputNumber v-model="financialConfig.accountCodeLength" class="w-full" />
                  </div>
                  <div>
                    <label>Auto-post Journals</label>
                    <InputSwitch v-model="financialConfig.autoPostJournals" />
                  </div>
                  <div>
                    <label>Require Approval</label>
                    <InputSwitch v-model="financialConfig.requireApproval" />
                  </div>
                  <div>
                    <label>Enable Multi-Currency</label>
                    <InputSwitch v-model="financialConfig.enableMultiCurrency" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
          <div class="col-12 md:col-4">
            <Card>
              <template #title>AP/AR Settings</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>Default Payment Terms</label>
                    <Dropdown v-model="financialConfig.defaultPaymentTerms" :options="paymentTerms" class="w-full" />
                  </div>
                  <div>
                    <label>Late Payment Fee (%)</label>
                    <InputNumber v-model="financialConfig.latePaymentFee" :min="0" :max="100" class="w-full" />
                  </div>
                  <div>
                    <label>Auto-send Reminders</label>
                    <InputSwitch v-model="financialConfig.autoSendReminders" />
                  </div>
                  <div>
                    <label>Credit Limit Check</label>
                    <InputSwitch v-model="financialConfig.enableCreditCheck" />
                  </div>
                  <div>
                    <label>Auto-apply Payments</label>
                    <InputSwitch v-model="financialConfig.autoApplyPayments" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
          <div class="col-12 md:col-4">
            <Card>
              <template #title>Tax Configuration</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>Default Tax Rate (%)</label>
                    <InputNumber v-model="taxConfig.defaultTaxRate" :min="0" :max="100" class="w-full" />
                  </div>
                  <div>
                    <label>Tax Jurisdiction</label>
                    <Dropdown v-model="taxConfig.jurisdiction" :options="jurisdictions" class="w-full" />
                  </div>
                  <div>
                    <label>Auto-calculate Tax</label>
                    <InputSwitch v-model="taxConfig.autoCalculate" />
                  </div>
                  <div>
                    <label>Include Tax in Price</label>
                    <InputSwitch v-model="taxConfig.includeTaxInPrice" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
          <div class="col-12 md:col-4">
            <Card>
              <template #title>Budget & Planning</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>Budget Period</label>
                    <Dropdown v-model="financialConfig.budgetPeriod" :options="budgetPeriods" class="w-full" />
                  </div>
                  <div>
                    <label>Variance Threshold (%)</label>
                    <InputNumber v-model="financialConfig.varianceThreshold" :min="1" :max="100" class="w-full" />
                  </div>
                  <div>
                    <label>Enable Budget Alerts</label>
                    <InputSwitch v-model="financialConfig.enableBudgetAlerts" />
                  </div>
                  <div>
                    <label>Auto-rollover Budget</label>
                    <InputSwitch v-model="financialConfig.autoRolloverBudget" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
    </div>

    <div v-if="state.activeTab === 2">
        <div class="grid">
          <div class="col-12 md:col-4">
            <Card>
              <template #title>Inventory Management</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>Default Costing Method</label>
                    <Dropdown v-model="inventoryConfig.costingMethod" :options="costingMethods" class="w-full" />
                  </div>
                  <div>
                    <label>Low Stock Threshold (%)</label>
                    <InputNumber v-model="inventoryConfig.lowStockThreshold" :min="0" :max="100" class="w-full" />
                  </div>
                  <div>
                    <label>Auto Reorder</label>
                    <InputSwitch v-model="inventoryConfig.autoReorder" />
                  </div>
                  <div>
                    <label>Track Serial Numbers</label>
                    <InputSwitch v-model="inventoryConfig.trackSerialNumbers" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
          <div class="col-12 md:col-4">
            <Card>
              <template #title>Fixed Assets</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>Depreciation Method</label>
                    <Dropdown v-model="assetsConfig.depreciationMethod" :options="depreciationMethods" class="w-full" />
                  </div>
                  <div>
                    <label>Capitalization Threshold</label>
                    <InputNumber v-model="assetsConfig.capitalizationThreshold" mode="currency" currency="USD" class="w-full" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>

        <div class="grid">
          <div class="col-12 md:col-4">
            <Card>
              <template #title>Email Configuration</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>SMTP Server</label>
                    <InputText v-model="integrationConfig.smtpServer" class="w-full" />
                  </div>
                  <div>
                    <label>SMTP Port</label>
                    <InputNumber v-model="integrationConfig.smtpPort" class="w-full" />
                  </div>
                  <div>
                    <label>From Email</label>
                    <InputText v-model="integrationConfig.fromEmail" class="w-full" />
                  </div>
                  <div>
                    <label>From Name</label>
                    <InputText v-model="integrationConfig.fromName" class="w-full" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
          <div class="col-12 md:col-4">
            <Card>
              <template #title>API & Webhooks</template>
              <template #content>
                <div class="flex flex-column gap-3">
                  <div>
                    <label>API Rate Limit (requests/minute)</label>
                    <InputNumber v-model="integrationConfig.apiRateLimit" class="w-full" />
                  </div>
                  <div>
                    <label>Webhook Timeout (seconds)</label>
                    <InputNumber v-model="integrationConfig.webhookTimeout" class="w-full" />
                  </div>
                  <div>
                    <label>Enable REST API</label>
                    <InputSwitch v-model="integrationConfig.enableAPI" />
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex justify-content-between align-items-center mt-6 pt-4 border-top-1 surface-border">
      <div class="text-sm text-500">
        Last saved: {{ lastSaved || 'Never' }}
      </div>
      <div class="flex gap-2">
        <Button label="Reset to Defaults" icon="pi pi-refresh" severity="secondary" outlined @click="resetToDefaults" />
        <Button label="Save All" icon="pi pi-save" @click="saveAllConfigurations" />
      </div>
    </div>
  </div>

  <Dialog v-model:visible="showAddFeature" modal header="Add Feature Flag" :style="{ width: '500px' }">
    <div class="flex flex-column gap-3">
      <div>
        <label>Feature Name</label>
        <InputText v-model="newFeature.name" class="w-full" />
      </div>
      <div>
        <label>Module</label>
        <Dropdown v-model="newFeature.module" :options="moduleOptions" class="w-full" />
      </div>
      <div>
        <label>Description</label>
        <Textarea v-model="newFeature.description" rows="3" class="w-full" />
      </div>
      <div>
        <label>Enable by default</label>
        <InputSwitch v-model="newFeature.enabled" />
      </div>
    </div>
    <template #footer>
      <Button label="Cancel" severity="secondary" @click="showAddFeature = false" />
      <Button label="Add" @click="addFeature" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import InputSwitch from 'primevue/inputswitch'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'
import {
  CURRENCIES, TIME_ZONES, DATE_FORMATS, NUMBER_FORMATS, THEMES, MONTHS,
  PAYMENT_TERMS, COSTING_METHODS, DEPRECIATION_METHODS, PAY_FREQUENCIES,
  JURISDICTIONS, BACKUP_FREQUENCIES, MODULE_OPTIONS, ENVIRONMENTS, LANGUAGES
} from '@/constants/systemSettings'

const toast = useToast()
const state = reactive({
  activeTab: 0
})

const lastSaved = ref(null)
const showAddFeature = ref(false)

const platformConfig = ref({
  name: 'Paksa Financial System',
  companyName: 'Paksa IT Solutions',
  environment: 'production',
  defaultLanguage: 'en',
  defaultCurrency: 'USD',
  timeZone: 'UTC',
  dateFormat: 'MM/DD/YYYY',
  numberFormat: '1,234.56',
  theme: 'default',
  logoUrl: '/assets/logo.png',
  supportEmail: 'support@paksa.com',
  supportPhone: '+1-800-PAKSA-IT',
  maxFileSize: 10,
  sessionWarning: 5,
  autoSaveInterval: 60,
  enableNotifications: true,
  enableDarkMode: false,
  enableMultiTenancy: true,
  maintenanceMode: false,
  debugMode: false,
  cacheTTL: 60,
  dbPoolSize: 20,
  requestTimeout: 30,
  enableCompression: true,
  enableCaching: true,
  logLevel: 'INFO',
  logRetention: 30,
  enableAuditTrail: true,
  enablePerformanceMonitoring: true,
  enableErrorTracking: true
})

const securityConfig = ref({
  sessionTimeout: 30,
  maxLoginAttempts: 5,
  passwordMinLength: 8,
  jwtExpiry: 24,
  enforceSSL: true,
  enableTwoFactor: false
})

const financialConfig = ref({
  fiscalYearStart: 'January',
  accountCodeLength: 6,
  autoPostJournals: false,
  requireApproval: true,
  defaultPaymentTerms: 'Net 30',
  latePaymentFee: 1.5,
  autoSendReminders: true,
  enableMultiCurrency: false,
  enableCreditCheck: true,
  autoApplyPayments: false,
  budgetPeriod: 'Annually',
  varianceThreshold: 10,
  enableBudgetAlerts: true,
  autoRolloverBudget: false
})

const inventoryConfig = ref({
  costingMethod: 'FIFO',
  lowStockThreshold: 20,
  autoReorder: false,
  trackSerialNumbers: true
})

const assetsConfig = ref({
  depreciationMethod: 'Straight Line',
  capitalizationThreshold: 1000
})

const hrConfig = ref({
  defaultWorkHours: 8,
  annualLeaveDays: 25,
  requireApproval: true
})

const payrollConfig = ref({
  payFrequency: 'Monthly',
  overtimeRate: 1.5,
  autoCalculateTax: true
})

const taxConfig = ref({
  jurisdiction: 'Federal',
  defaultTaxRate: 10,
  autoCalculate: true,
  includeTaxInPrice: false
})

const complianceConfig = ref({
  auditRetention: 2555,
  backupFrequency: 'Daily',
  enableAuditTrail: true
})

const integrationConfig = ref({
  smtpServer: 'smtp.gmail.com',
  smtpPort: 587,
  fromEmail: 'noreply@paksa.com',
  fromName: 'Paksa Financial System',
  apiRateLimit: 1000,
  webhookTimeout: 30,
  enableAPI: true
})

const featureFlags = ref([])
const newFeature = ref({
  name: '',
  module: '',
  description: '',
  enabled: false
})

const environments = ref(ENVIRONMENTS)
const languages = ref(LANGUAGES)
const currencies = ref(CURRENCIES)
const timeZones = ref(TIME_ZONES)
const dateFormats = ref(DATE_FORMATS)
const numberFormats = ref(NUMBER_FORMATS)
const themes = ref(THEMES)
const months = ref(MONTHS)
const paymentTerms = ref(PAYMENT_TERMS)
const costingMethods = ref(COSTING_METHODS)
const depreciationMethods = ref(DEPRECIATION_METHODS)
const payFrequencies = ref(PAY_FREQUENCIES)
const jurisdictions = ref(JURISDICTIONS)
const backupFrequencies = ref(BACKUP_FREQUENCIES)
const moduleOptions = ref(MODULE_OPTIONS)
const logLevels = ref(['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL'])
const budgetPeriods = ref(['Monthly', 'Quarterly', 'Annually'])

const changeLanguage = (event: any) => {
  const newLocale = event.value
  localStorage.setItem('user-locale', newLocale)
  
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: `Language changed to ${languages.value.find(l => l.value === newLocale)?.label}`,
    life: 3000
  })
}

const loadConfigurations = () => {
  // Load configurations from API
  console.log('Loading configurations...')
}

const resetToDefaults = () => {
  // Reset all configurations to defaults
  console.log('Resetting to defaults...')
  toast.add({
    severity: 'info',
    summary: 'Reset',
    detail: 'All configurations reset to defaults',
    life: 3000
  })
}

const saveAllConfigurations = () => {
  const allConfigs = {
    platform: platformConfig.value,
    security: securityConfig.value,
    financial: financialConfig.value,
    inventory: inventoryConfig.value,
    assets: assetsConfig.value,
    hr: hrConfig.value,
    payroll: payrollConfig.value,
    tax: taxConfig.value,
    compliance: complianceConfig.value,
    integration: integrationConfig.value,
    features: featureFlags.value
  }
  
  console.log('Saving configurations:', allConfigs)
  lastSaved.value = new Date().toLocaleString()
  
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: 'All configurations saved successfully',
    life: 3000
  })
}

const addFeature = () => {
  featureFlags.value.push({
    id: Date.now(),
    ...newFeature.value
  })
  newFeature.value = { name: '', module: '', description: '', enabled: false }
  showAddFeature.value = false
  
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: 'Feature flag added successfully',
    life: 3000
  })
}

const updateFeatureFlag = (flag: any) => {
  console.log('Feature flag updated:', flag)
}

const deleteFeature = (feature: any) => {
  const index = featureFlags.value.findIndex(f => f.id === feature.id)
  if (index > -1) {
    featureFlags.value.splice(index, 1)
  }
}

const exportConfig = () => {
  const allConfigs = {
    platform: platformConfig.value,
    security: securityConfig.value,
    financial: financialConfig.value,
    inventory: inventoryConfig.value,
    assets: assetsConfig.value,
    hr: hrConfig.value,
    payroll: payrollConfig.value,
    tax: taxConfig.value,
    compliance: complianceConfig.value,
    integration: integrationConfig.value,
    features: featureFlags.value
  }
  
  const blob = new Blob([JSON.stringify(allConfigs, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'paksa-config.json'
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  platformConfig.value.defaultLanguage = 'en'
})
</script>

<style scoped>
.configuration-dashboard {
  padding: var(--paksa-spacing-lg);
  background: var(--paksa-background);
  min-height: 100vh;
}

.configuration-dashboard .p-card {
  background: var(--paksa-surface);
  border-radius: var(--paksa-radius-lg);
  box-shadow: var(--paksa-shadow-md);
  transition: all var(--paksa-transition-normal);
  margin-bottom: var(--paksa-spacing-md);
}

.configuration-dashboard .p-card:hover {
  box-shadow: var(--paksa-shadow-lg);
  transform: translateY(-2px);
}

.configuration-dashboard .p-button {
  border-radius: var(--paksa-radius-md);
  transition: all var(--paksa-transition-fast);
}

.configuration-dashboard .p-inputtext,
.configuration-dashboard .p-dropdown,
.configuration-dashboard .p-inputnumber {
  border-radius: var(--paksa-radius-sm);
}

.configuration-dashboard label {
  font-weight: 500;
  color: var(--paksa-text-primary);
  margin-bottom: var(--paksa-spacing-xs);
  display: block;
}
</style>