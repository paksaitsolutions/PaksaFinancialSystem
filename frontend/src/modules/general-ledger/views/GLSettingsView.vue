<template>
  <div class="gl-settings">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2 class="text-2xl font-semibold text-900 m-0">General Ledger Settings</h2>
      <Button 
        label="Save All Changes" 
        icon="pi pi-save" 
        :loading="saving" 
        @click="saveSettings"
      />
    </div>

    <TabView v-model:activeIndex="activeTab">
      <!-- Account Settings -->
      <TabPanel header="Account Settings">
        <Card>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="defaultCurrency" class="font-semibold">Default Currency</label>
                  <Dropdown 
                    id="defaultCurrency" 
                    v-model="settings.defaultCurrency" 
                    :options="currencies" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="accountCodeFormat" class="font-semibold">Account Code Format</label>
                  <Dropdown 
                    id="accountCodeFormat" 
                    v-model="settings.accountCodeFormat" 
                    :options="accountCodeFormats" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="accountLevels" class="font-semibold">Account Hierarchy Levels</label>
                  <InputNumber 
                    id="accountLevels" 
                    v-model="settings.accountLevels" 
                    :min="2" 
                    :max="6" 
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="decimalPlaces" class="font-semibold">Decimal Places</label>
                  <InputNumber 
                    id="decimalPlaces" 
                    v-model="settings.decimalPlaces" 
                    :min="0" 
                    :max="6" 
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="field-checkbox">
                  <Checkbox id="allowNegativeBalances" v-model="settings.allowNegativeBalances" :binary="true" />
                  <label for="allowNegativeBalances" class="font-semibold ml-2">Allow Negative Account Balances</label>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </TabPanel>

      <!-- Period Settings -->
      <TabPanel header="Period Settings">
        <Card>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="fiscalYearStart" class="font-semibold">Fiscal Year Start Month</label>
                  <Dropdown 
                    id="fiscalYearStart" 
                    v-model="settings.fiscalYearStart" 
                    :options="months" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="periodLength" class="font-semibold">Period Length</label>
                  <Dropdown 
                    id="periodLength" 
                    v-model="settings.periodLength" 
                    :options="periodLengths" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="grid">
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="autoCreatePeriods" v-model="settings.autoCreatePeriods" :binary="true" />
                      <label for="autoCreatePeriods" class="font-semibold ml-2">Auto Create Periods</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="autoClosePeriods" v-model="settings.autoClosePeriods" :binary="true" />
                      <label for="autoClosePeriods" class="font-semibold ml-2">Auto Close Periods</label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </TabPanel>

      <!-- Posting Rules -->
      <TabPanel header="Posting Rules">
        <Card>
          <template #content>
            <div class="grid">
              <div class="col-12">
                <div class="grid">
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="requireBalancedEntries" v-model="settings.requireBalancedEntries" :binary="true" />
                      <label for="requireBalancedEntries" class="font-semibold ml-2">Require Balanced Journal Entries</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="requireApproval" v-model="settings.requireApproval" :binary="true" />
                      <label for="requireApproval" class="font-semibold ml-2">Require Journal Entry Approval</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="allowFutureDates" v-model="settings.allowFutureDates" :binary="true" />
                      <label for="allowFutureDates" class="font-semibold ml-2">Allow Future Posting Dates</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="requireReference" v-model="settings.requireReference" :binary="true" />
                      <label for="requireReference" class="font-semibold ml-2">Require Reference Numbers</label>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="maxPostingDays" class="font-semibold">Max Days for Backdated Posting</label>
                  <InputNumber 
                    id="maxPostingDays" 
                    v-model="settings.maxPostingDays" 
                    :min="0" 
                    :max="365" 
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="approvalLimit" class="font-semibold">Approval Required Above Amount</label>
                  <InputNumber 
                    id="approvalLimit" 
                    v-model="settings.approvalLimit" 
                    :min="0" 
                    mode="currency" 
                    currency="USD" 
                    class="w-full"
                  />
                </div>
              </div>
            </div>
          </template>
        </Card>
      </TabPanel>

      <!-- Numbering -->
      <TabPanel header="Numbering">
        <Card>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="journalEntryPrefix" class="font-semibold">Journal Entry Prefix</label>
                  <InputText 
                    id="journalEntryPrefix" 
                    v-model="settings.journalEntryPrefix" 
                    class="w-full" 
                    placeholder="JE"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="nextJournalNumber" class="font-semibold">Next Journal Entry Number</label>
                  <InputNumber 
                    id="nextJournalNumber" 
                    v-model="settings.nextJournalNumber" 
                    :min="1" 
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="accountPrefix" class="font-semibold">Account Code Prefix</label>
                  <InputText 
                    id="accountPrefix" 
                    v-model="settings.accountPrefix" 
                    class="w-full" 
                    placeholder="ACC"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="numberingFormat" class="font-semibold">Numbering Format</label>
                  <Dropdown 
                    id="numberingFormat" 
                    v-model="settings.numberingFormat" 
                    :options="numberingFormats" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="field-checkbox">
                  <Checkbox id="resetNumberingYearly" v-model="settings.resetNumberingYearly" :binary="true" />
                  <label for="resetNumberingYearly" class="font-semibold ml-2">Reset Numbering Each Fiscal Year</label>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </TabPanel>
    </TabView>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import settingsService from '@/api/settingsService'

const toast = useToast()
const saving = ref(false)
const activeTab = ref(0)

const settings = ref({
  defaultCurrency: 'USD',
  accountCodeFormat: 'numeric',
  accountLevels: 4,
  decimalPlaces: 2,
  allowNegativeBalances: false,
  fiscalYearStart: 1,
  periodLength: 'monthly',
  autoCreatePeriods: true,
  autoClosePeriods: false,
  requireBalancedEntries: true,
  requireApproval: false,
  allowFutureDates: false,
  requireReference: true,
  maxPostingDays: 30,
  approvalLimit: 10000,
  journalEntryPrefix: 'JE',
  nextJournalNumber: 1,
  accountPrefix: '',
  numberingFormat: 'sequential',
  resetNumberingYearly: false
})

const currencies = [
  { label: 'US Dollar (USD)', value: 'USD' },
  { label: 'Euro (EUR)', value: 'EUR' },
  { label: 'British Pound (GBP)', value: 'GBP' },
  { label: 'Pakistani Rupee (PKR)', value: 'PKR' }
]

const accountCodeFormats = [
  { label: 'Numeric (1000, 2000)', value: 'numeric' },
  { label: 'Alphanumeric (A1000, B2000)', value: 'alphanumeric' },
  { label: 'Hierarchical (1000.01.001)', value: 'hierarchical' }
]

const months = [
  { label: 'January', value: 1 },
  { label: 'February', value: 2 },
  { label: 'March', value: 3 },
  { label: 'April', value: 4 },
  { label: 'May', value: 5 },
  { label: 'June', value: 6 },
  { label: 'July', value: 7 },
  { label: 'August', value: 8 },
  { label: 'September', value: 9 },
  { label: 'October', value: 10 },
  { label: 'November', value: 11 },
  { label: 'December', value: 12 }
]

const periodLengths = [
  { label: 'Monthly', value: 'monthly' },
  { label: 'Quarterly', value: 'quarterly' },
  { label: 'Semi-Annual', value: 'semi-annual' },
  { label: 'Annual', value: 'annual' }
]

const numberingFormats = [
  { label: 'Sequential (1, 2, 3)', value: 'sequential' },
  { label: 'Year-Sequential (2024-001)', value: 'year-sequential' },
  { label: 'Month-Sequential (202401-001)', value: 'month-sequential' }
]

const loadSettings = async () => {
  try {
    const systemSettings = await settingsService.getSystemSettings()
    
    // Map system settings to GL settings
    systemSettings.forEach(setting => {
      if (setting.setting_key.startsWith('gl_')) {
        const key = setting.setting_key.replace('gl_', '')
        if (key in settings.value) {
          const value = setting.setting_value
          if (typeof settings.value[key] === 'boolean') {
            settings.value[key] = value === 'true'
          } else if (typeof settings.value[key] === 'number') {
            settings.value[key] = parseInt(value)
          } else {
            settings.value[key] = value
          }
        }
      }
    })
  } catch (error) {
    console.error('Error loading GL settings:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load GL settings',
      life: 3000
    })
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    // Save each GL setting as a system setting
    const promises = Object.entries(settings.value).map(([key, value]) => {
      return settingsService.updateSystemSetting(
        `gl_${key}`,
        String(value),
        `GL setting: ${key}`
      )
    })
    
    await Promise.all(promises)
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'GL settings saved successfully',
      life: 3000
    })
  } catch (error) {
    console.error('Error saving GL settings:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save GL settings',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.gl-settings {
  max-width: 1200px;
  margin: 0 auto;
}

.field {
  margin-bottom: 1rem;
}

.field-checkbox {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}
</style>