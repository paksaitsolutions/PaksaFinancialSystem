<template>
  <div class="general-settings">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2 class="text-2xl font-semibold text-900 m-0">General Settings</h2>
      <div class="flex gap-2">
        <Button 
          label="Reset to Defaults" 
          icon="pi pi-refresh" 
          severity="secondary" 
          outlined 
          @click="resetToDefaults"
        />
        <Button 
          label="Save All Changes" 
          icon="pi pi-save" 
          :loading="saving" 
          @click="saveAllSettings"
        />
      </div>
    </div>

    <div class="grid">
      <!-- Company Information -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-building text-primary"></i>
              <span>Company Information</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="companyName" class="font-semibold">Company Name *</label>
                  <InputText 
                    id="companyName" 
                    v-model="settings.companyName" 
                    class="w-full" 
                    placeholder="Enter company name"
                    :class="{ 'p-invalid': !settings.companyName }"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="companyCode" class="font-semibold">Company Code</label>
                  <InputText 
                    id="companyCode" 
                    v-model="settings.companyCode" 
                    class="w-full" 
                    placeholder="e.g., PAKSA001"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="taxId" class="font-semibold">Tax ID / EIN</label>
                  <InputText 
                    id="taxId" 
                    v-model="settings.taxId" 
                    class="w-full" 
                    placeholder="Enter tax identification number"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="registrationNumber" class="font-semibold">Registration Number</label>
                  <InputText 
                    id="registrationNumber" 
                    v-model="settings.registrationNumber" 
                    class="w-full" 
                    placeholder="Enter business registration number"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="field">
                  <label for="companyAddress" class="font-semibold">Company Address</label>
                  <Textarea 
                    id="companyAddress" 
                    v-model="settings.companyAddress" 
                    class="w-full" 
                    rows="3" 
                    placeholder="Enter complete company address"
                  />
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Financial Settings -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-dollar text-primary"></i>
              <span>Financial Settings</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="baseCurrency" class="font-semibold">Base Currency *</label>
                  <Dropdown 
                    id="baseCurrency" 
                    v-model="settings.baseCurrency" 
                    :options="currencies" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full" 
                    placeholder="Select base currency"
                    filter
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="fiscalYearStart" class="font-semibold">Fiscal Year Start *</label>
                  <Dropdown 
                    id="fiscalYearStart" 
                    v-model="settings.fiscalYearStart" 
                    :options="fiscalYearOptions" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full" 
                    placeholder="Select fiscal year start month"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="decimalPlaces" class="font-semibold">Decimal Places</label>
                  <InputNumber 
                    id="decimalPlaces" 
                    v-model="settings.decimalPlaces" 
                    class="w-full" 
                    :min="0" 
                    :max="6" 
                    placeholder="Number of decimal places"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="roundingMethod" class="font-semibold">Rounding Method</label>
                  <Dropdown 
                    id="roundingMethod" 
                    v-model="settings.roundingMethod" 
                    :options="roundingMethods" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full" 
                    placeholder="Select rounding method"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="field-checkbox">
                  <Checkbox 
                    id="multiCurrency" 
                    v-model="settings.multiCurrencyEnabled" 
                    binary
                  />
                  <label for="multiCurrency" class="font-semibold ml-2">Enable Multi-Currency Support</label>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Regional Settings -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-globe text-primary"></i>
              <span>Regional & Localization</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="timezone" class="font-semibold">Timezone *</label>
                  <Dropdown 
                    id="timezone" 
                    v-model="settings.timezone" 
                    :options="timezones" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full" 
                    placeholder="Select timezone"
                    filter
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="language" class="font-semibold">Default Language</label>
                  <Dropdown 
                    id="language" 
                    v-model="settings.language" 
                    :options="languages" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full" 
                    placeholder="Select language"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="dateFormat" class="font-semibold">Date Format</label>
                  <Dropdown 
                    id="dateFormat" 
                    v-model="settings.dateFormat" 
                    :options="dateFormats" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full" 
                    placeholder="Select date format"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="timeFormat" class="font-semibold">Time Format</label>
                  <Dropdown 
                    id="timeFormat" 
                    v-model="settings.timeFormat" 
                    :options="timeFormats" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full" 
                    placeholder="Select time format"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="numberFormat" class="font-semibold">Number Format</label>
                  <Dropdown 
                    id="numberFormat" 
                    v-model="settings.numberFormat" 
                    :options="numberFormats" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full" 
                    placeholder="Select number format"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="weekStart" class="font-semibold">Week Starts On</label>
                  <Dropdown 
                    id="weekStart" 
                    v-model="settings.weekStart" 
                    :options="weekStartOptions" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full" 
                    placeholder="Select week start day"
                  />
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Document Settings -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-file text-primary"></i>
              <span>Document & Numbering</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="invoicePrefix" class="font-semibold">Invoice Number Prefix</label>
                  <InputText 
                    id="invoicePrefix" 
                    v-model="settings.invoicePrefix" 
                    class="w-full" 
                    placeholder="e.g., INV-"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="invoiceStartNumber" class="font-semibold">Invoice Start Number</label>
                  <InputNumber 
                    id="invoiceStartNumber" 
                    v-model="settings.invoiceStartNumber" 
                    class="w-full" 
                    :min="1" 
                    placeholder="Starting invoice number"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="billPrefix" class="font-semibold">Bill Number Prefix</label>
                  <InputText 
                    id="billPrefix" 
                    v-model="settings.billPrefix" 
                    class="w-full" 
                    placeholder="e.g., BILL-"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="paymentPrefix" class="font-semibold">Payment Number Prefix</label>
                  <InputText 
                    id="paymentPrefix" 
                    v-model="settings.paymentPrefix" 
                    class="w-full" 
                    placeholder="e.g., PAY-"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="field-checkbox">
                  <Checkbox 
                    id="autoNumbering" 
                    v-model="settings.autoNumberingEnabled" 
                    binary
                  />
                  <label for="autoNumbering" class="font-semibold ml-2">Enable Automatic Document Numbering</label>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- System Preferences -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-cog text-primary"></i>
              <span>System Preferences</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="sessionTimeout" class="font-semibold">Session Timeout (minutes)</label>
                  <InputNumber 
                    id="sessionTimeout" 
                    v-model="settings.sessionTimeout" 
                    class="w-full" 
                    :min="5" 
                    :max="480" 
                    placeholder="Session timeout in minutes"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="pageSize" class="font-semibold">Default Page Size</label>
                  <Dropdown 
                    id="pageSize" 
                    v-model="settings.defaultPageSize" 
                    :options="pageSizeOptions" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full" 
                    placeholder="Select default page size"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="theme" class="font-semibold">Default Theme</label>
                  <Dropdown 
                    id="theme" 
                    v-model="settings.defaultTheme" 
                    :options="themeOptions" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full" 
                    placeholder="Select default theme"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="backupFrequency" class="font-semibold">Backup Frequency</label>
                  <Dropdown 
                    id="backupFrequency" 
                    v-model="settings.backupFrequency" 
                    :options="backupFrequencyOptions" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full" 
                    placeholder="Select backup frequency"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="grid">
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox 
                        id="auditTrail" 
                        v-model="settings.auditTrailEnabled" 
                        binary
                      />
                      <label for="auditTrail" class="font-semibold ml-2">Enable Audit Trail</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox 
                        id="emailNotifications" 
                        v-model="settings.emailNotificationsEnabled" 
                        binary
                      />
                      <label for="emailNotifications" class="font-semibold ml-2">Enable Email Notifications</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox 
                        id="twoFactorAuth" 
                        v-model="settings.twoFactorAuthRequired" 
                        binary
                      />
                      <label for="twoFactorAuth" class="font-semibold ml-2">Require Two-Factor Authentication</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox 
                        id="autoSave" 
                        v-model="settings.autoSaveEnabled" 
                        binary
                      />
                      <label for="autoSave" class="font-semibold ml-2">Enable Auto-Save</label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Integration Settings -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-link text-primary"></i>
              <span>Integration & API</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="apiRateLimit" class="font-semibold">API Rate Limit (requests/minute)</label>
                  <InputNumber 
                    id="apiRateLimit" 
                    v-model="settings.apiRateLimit" 
                    class="w-full" 
                    :min="10" 
                    :max="10000" 
                    placeholder="API rate limit"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="webhookTimeout" class="font-semibold">Webhook Timeout (seconds)</label>
                  <InputNumber 
                    id="webhookTimeout" 
                    v-model="settings.webhookTimeout" 
                    class="w-full" 
                    :min="5" 
                    :max="300" 
                    placeholder="Webhook timeout"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="grid">
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox 
                        id="apiLogging" 
                        v-model="settings.apiLoggingEnabled" 
                        binary
                      />
                      <label for="apiLogging" class="font-semibold ml-2">Enable API Request Logging</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox 
                        id="webhookRetry" 
                        v-model="settings.webhookRetryEnabled" 
                        binary
                      />
                      <label for="webhookRetry" class="font-semibold ml-2">Enable Webhook Retry</label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Success Message -->
    <Message 
      v-if="showSuccessMessage" 
      severity="success" 
      :closable="false" 
      class="mb-4"
    >
      Settings saved successfully!
    </Message>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import settingsService from '@/api/settingsService'

const toast = useToast()
const saving = ref(false)
const showSuccessMessage = ref(false)

const settings = ref({
  // Company Information
  companyName: 'Paksa Financial System',
  companyCode: 'PAKSA001',
  taxId: '',
  registrationNumber: '',
  companyAddress: '',
  
  // Financial Settings
  baseCurrency: 'USD',
  fiscalYearStart: 'January',
  decimalPlaces: 2,
  roundingMethod: 'round',
  multiCurrencyEnabled: false,
  
  // Regional Settings
  timezone: 'UTC',
  language: 'en',
  dateFormat: 'MM/DD/YYYY',
  timeFormat: '12',
  numberFormat: 'US',
  weekStart: 'Sunday',
  
  // Document Settings
  invoicePrefix: 'INV-',
  invoiceStartNumber: 1000,
  billPrefix: 'BILL-',
  paymentPrefix: 'PAY-',
  autoNumberingEnabled: true,
  
  // System Preferences
  sessionTimeout: 60,
  defaultPageSize: 25,
  defaultTheme: 'light',
  backupFrequency: 'daily',
  auditTrailEnabled: true,
  emailNotificationsEnabled: true,
  twoFactorAuthRequired: false,
  autoSaveEnabled: true,
  
  // Integration Settings
  apiRateLimit: 1000,
  webhookTimeout: 30,
  apiLoggingEnabled: true,
  webhookRetryEnabled: true
})

const currencies = [
  { label: 'US Dollar (USD)', value: 'USD' },
  { label: 'Euro (EUR)', value: 'EUR' },
  { label: 'British Pound (GBP)', value: 'GBP' },
  { label: 'Canadian Dollar (CAD)', value: 'CAD' },
  { label: 'Australian Dollar (AUD)', value: 'AUD' },
  { label: 'Japanese Yen (JPY)', value: 'JPY' },
  { label: 'Swiss Franc (CHF)', value: 'CHF' },
  { label: 'Chinese Yuan (CNY)', value: 'CNY' },
  { label: 'Indian Rupee (INR)', value: 'INR' },
  { label: 'Pakistani Rupee (PKR)', value: 'PKR' }
]

const fiscalYearOptions = [
  { label: 'January', value: 'January' },
  { label: 'February', value: 'February' },
  { label: 'March', value: 'March' },
  { label: 'April', value: 'April' },
  { label: 'May', value: 'May' },
  { label: 'June', value: 'June' },
  { label: 'July', value: 'July' },
  { label: 'August', value: 'August' },
  { label: 'September', value: 'September' },
  { label: 'October', value: 'October' },
  { label: 'November', value: 'November' },
  { label: 'December', value: 'December' }
]

const roundingMethods = [
  { label: 'Round (0.5 rounds up)', value: 'round' },
  { label: 'Round Up (ceiling)', value: 'ceil' },
  { label: 'Round Down (floor)', value: 'floor' },
  { label: 'Banker\'s Rounding', value: 'bankers' }
]

const timezones = [
  { label: 'UTC', value: 'UTC' },
  { label: 'Eastern Time (ET)', value: 'America/New_York' },
  { label: 'Central Time (CT)', value: 'America/Chicago' },
  { label: 'Mountain Time (MT)', value: 'America/Denver' },
  { label: 'Pacific Time (PT)', value: 'America/Los_Angeles' },
  { label: 'London (GMT)', value: 'Europe/London' },
  { label: 'Paris (CET)', value: 'Europe/Paris' },
  { label: 'Tokyo (JST)', value: 'Asia/Tokyo' },
  { label: 'Sydney (AEST)', value: 'Australia/Sydney' },
  { label: 'Karachi (PKT)', value: 'Asia/Karachi' },
  { label: 'Dubai (GST)', value: 'Asia/Dubai' }
]

const languages = [
  { label: 'English', value: 'en' },
  { label: 'Spanish', value: 'es' },
  { label: 'French', value: 'fr' },
  { label: 'German', value: 'de' },
  { label: 'Italian', value: 'it' },
  { label: 'Portuguese', value: 'pt' },
  { label: 'Arabic', value: 'ar' },
  { label: 'Urdu', value: 'ur' },
  { label: 'Chinese (Simplified)', value: 'zh-CN' },
  { label: 'Japanese', value: 'ja' }
]

const dateFormats = [
  { label: 'MM/DD/YYYY (US)', value: 'MM/DD/YYYY' },
  { label: 'DD/MM/YYYY (UK)', value: 'DD/MM/YYYY' },
  { label: 'YYYY-MM-DD (ISO)', value: 'YYYY-MM-DD' },
  { label: 'DD.MM.YYYY (German)', value: 'DD.MM.YYYY' },
  { label: 'DD-MM-YYYY', value: 'DD-MM-YYYY' }
]

const timeFormats = [
  { label: '12 Hour (AM/PM)', value: '12' },
  { label: '24 Hour', value: '24' }
]

const numberFormats = [
  { label: 'US (1,234.56)', value: 'US' },
  { label: 'European (1.234,56)', value: 'EU' },
  { label: 'Indian (1,23,456.78)', value: 'IN' },
  { label: 'Swiss (1\'234.56)', value: 'CH' }
]

const weekStartOptions = [
  { label: 'Sunday', value: 'Sunday' },
  { label: 'Monday', value: 'Monday' },
  { label: 'Saturday', value: 'Saturday' }
]

const pageSizeOptions = [
  { label: '10 items', value: 10 },
  { label: '25 items', value: 25 },
  { label: '50 items', value: 50 },
  { label: '100 items', value: 100 }
]

const themeOptions = [
  { label: 'Light Theme', value: 'light' },
  { label: 'Dark Theme', value: 'dark' },
  { label: 'Auto (System)', value: 'auto' }
]

const backupFrequencyOptions = [
  { label: 'Hourly', value: 'hourly' },
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' }
]

const loadSettings = async () => {
  try {
    // Get current company ID (you may need to adjust this based on your auth system)
    const companyId = 1 // TODO: Get from auth store or context
    
    const companySettings = await settingsService.getCompanySettings(companyId)
    
    // Map API response to component settings
    settings.value = {
      companyName: companySettings.company_name,
      companyCode: companySettings.company_code || '',
      taxId: companySettings.tax_id || '',
      registrationNumber: companySettings.registration_number || '',
      companyAddress: companySettings.company_address || '',
      baseCurrency: companySettings.base_currency,
      fiscalYearStart: companySettings.fiscal_year_start,
      decimalPlaces: companySettings.decimal_places,
      roundingMethod: companySettings.rounding_method,
      multiCurrencyEnabled: companySettings.multi_currency_enabled,
      timezone: companySettings.timezone,
      language: companySettings.language,
      dateFormat: companySettings.date_format,
      timeFormat: companySettings.time_format,
      numberFormat: companySettings.number_format,
      weekStart: companySettings.week_start,
      invoicePrefix: companySettings.invoice_prefix || '',
      invoiceStartNumber: companySettings.invoice_start_number,
      billPrefix: companySettings.bill_prefix || '',
      paymentPrefix: companySettings.payment_prefix || '',
      autoNumberingEnabled: companySettings.auto_numbering_enabled,
      sessionTimeout: companySettings.session_timeout,
      defaultPageSize: companySettings.default_page_size,
      defaultTheme: companySettings.default_theme,
      backupFrequency: companySettings.backup_frequency,
      auditTrailEnabled: companySettings.audit_trail_enabled,
      emailNotificationsEnabled: companySettings.email_notifications_enabled,
      twoFactorAuthRequired: companySettings.two_factor_auth_required,
      autoSaveEnabled: companySettings.auto_save_enabled,
      apiRateLimit: companySettings.api_rate_limit,
      webhookTimeout: companySettings.webhook_timeout,
      apiLoggingEnabled: companySettings.api_logging_enabled,
      webhookRetryEnabled: companySettings.webhook_retry_enabled
    }
  } catch (error) {
    console.error('Error loading settings:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load settings',
      life: 3000
    })
  }
}

const saveAllSettings = async () => {
  // Validate required fields
  const validationErrors = settingsService.validateSettings({
    company_name: settings.value.companyName,
    base_currency: settings.value.baseCurrency,
    decimal_places: settings.value.decimalPlaces,
    session_timeout: settings.value.sessionTimeout,
    default_page_size: settings.value.defaultPageSize,
    api_rate_limit: settings.value.apiRateLimit,
    webhook_timeout: settings.value.webhookTimeout
  })

  if (validationErrors.length > 0) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: validationErrors[0],
      life: 5000
    })
    return
  }

  saving.value = true
  try {
    const companyId = 1 // TODO: Get from auth store or context
    
    // Map component settings to API format
    const apiSettings = {
      company_name: settings.value.companyName,
      company_code: settings.value.companyCode,
      tax_id: settings.value.taxId,
      registration_number: settings.value.registrationNumber,
      company_address: settings.value.companyAddress,
      base_currency: settings.value.baseCurrency,
      fiscal_year_start: settings.value.fiscalYearStart,
      decimal_places: settings.value.decimalPlaces,
      rounding_method: settings.value.roundingMethod,
      multi_currency_enabled: settings.value.multiCurrencyEnabled,
      timezone: settings.value.timezone,
      language: settings.value.language,
      date_format: settings.value.dateFormat,
      time_format: settings.value.timeFormat,
      number_format: settings.value.numberFormat,
      week_start: settings.value.weekStart,
      invoice_prefix: settings.value.invoicePrefix,
      invoice_start_number: settings.value.invoiceStartNumber,
      bill_prefix: settings.value.billPrefix,
      payment_prefix: settings.value.paymentPrefix,
      auto_numbering_enabled: settings.value.autoNumberingEnabled,
      session_timeout: settings.value.sessionTimeout,
      default_page_size: settings.value.defaultPageSize,
      default_theme: settings.value.defaultTheme,
      backup_frequency: settings.value.backupFrequency,
      audit_trail_enabled: settings.value.auditTrailEnabled,
      email_notifications_enabled: settings.value.emailNotificationsEnabled,
      two_factor_auth_required: settings.value.twoFactorAuthRequired,
      auto_save_enabled: settings.value.autoSaveEnabled,
      api_rate_limit: settings.value.apiRateLimit,
      webhook_timeout: settings.value.webhookTimeout,
      api_logging_enabled: settings.value.apiLoggingEnabled,
      webhook_retry_enabled: settings.value.webhookRetryEnabled
    }
    
    await settingsService.updateCompanySettings(companyId, apiSettings)
    
    showSuccessMessage.value = true
    setTimeout(() => {
      showSuccessMessage.value = false
    }, 3000)
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Settings saved successfully',
      life: 3000
    })
  } catch (error) {
    console.error('Error saving settings:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save settings. Please try again.',
      life: 5000
    })
  } finally {
    saving.value = false
  }
}

const resetToDefaults = () => {
  settings.value = {
    companyName: 'Paksa Financial System',
    companyCode: 'PAKSA001',
    taxId: '',
    registrationNumber: '',
    companyAddress: '',
    baseCurrency: 'USD',
    fiscalYearStart: 'January',
    decimalPlaces: 2,
    roundingMethod: 'round',
    multiCurrencyEnabled: false,
    timezone: 'UTC',
    language: 'en',
    dateFormat: 'MM/DD/YYYY',
    timeFormat: '12',
    numberFormat: 'US',
    weekStart: 'Sunday',
    invoicePrefix: 'INV-',
    invoiceStartNumber: 1000,
    billPrefix: 'BILL-',
    paymentPrefix: 'PAY-',
    autoNumberingEnabled: true,
    sessionTimeout: 60,
    defaultPageSize: 25,
    defaultTheme: 'light',
    backupFrequency: 'daily',
    auditTrailEnabled: true,
    emailNotificationsEnabled: true,
    twoFactorAuthRequired: false,
    autoSaveEnabled: true,
    apiRateLimit: 1000,
    webhookTimeout: 30,
    apiLoggingEnabled: true,
    webhookRetryEnabled: true
  }
  
  toast.add({
    severity: 'info',
    summary: 'Reset',
    detail: 'Settings reset to defaults',
    life: 3000
  })
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.general-settings {
  max-width: 1200px;
  margin: 0 auto;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

.field-checkbox {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.p-card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.p-card .p-card-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.text-primary {
  color: var(--primary-color) !important;
}

.p-invalid {
  border-color: var(--red-500) !important;
}
</style>