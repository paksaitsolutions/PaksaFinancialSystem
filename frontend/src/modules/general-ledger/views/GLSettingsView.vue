<template>
  <v-container fluid>
<<<<<<< HEAD
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">General Ledger Settings</h1>
        
        <v-tabs v-model="activeTab">
          <v-tab value="general">General Settings</v-tab>
          <v-tab value="periods">Accounting Periods</v-tab>
          <v-tab value="closing">Period Closing</v-tab>
          <v-tab value="audit">Audit Settings</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="general">
            <v-card>
              <v-card-title>General GL Settings</v-card-title>
              <v-card-text>
                <v-form @submit.prevent="saveGeneralSettings">
                  <v-row>
                    <v-col cols="12" md="6">
                      <v-select
                        v-model="settings.defaultCurrency"
                        :items="currencies"
                        label="Default Currency"
                        required
                      />
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-select
                        v-model="settings.fiscalYearEnd"
                        :items="fiscalYearOptions"
                        label="Fiscal Year End"
                        required
                      />
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-switch
                        v-model="settings.requireApproval"
                        label="Require Journal Entry Approval"
                      />
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-switch
                        v-model="settings.enableMultiCurrency"
                        label="Enable Multi-Currency"
                      />
                    </v-col>
                  </v-row>
                  <v-btn type="submit" color="primary" :loading="saving">
                    Save Settings
                  </v-btn>
                </v-form>
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <v-window-item value="periods">
            <v-card>
              <v-card-title>Accounting Periods</v-card-title>
              <v-card-text>
                <v-data-table
                  :headers="periodHeaders"
                  :items="accountingPeriods"
                  :loading="loading"
                >
                  <template v-slot:item.status="{ item }">
                    <v-chip :color="getPeriodStatusColor(item.status)" small>
                      {{ item.status }}
                    </v-chip>
                  </template>
                  <template v-slot:item.actions="{ item }">
                    <v-btn
                      icon
                      small
                      @click="openPeriod(item)"
                      :disabled="item.status === 'open'"
                    >
                      <v-icon>mdi-lock-open</v-icon>
                    </v-btn>
                    <v-btn
                      icon
                      small
                      @click="closePeriod(item)"
                      :disabled="item.status === 'closed'"
                    >
                      <v-icon>mdi-lock</v-icon>
                    </v-btn>
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-window-item>
          
          <v-window-item value="closing">
            <period-closing-settings @save="savePeriodClosingSettings" />
          </v-window-item>
          
          <v-window-item value="audit">
            <audit-settings @save="saveAuditSettings" />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
=======
    <v-card>
      <v-card-title>General Ledger Settings</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="saveSettings">
          <v-row>
            <v-col cols="12" md="6">
              <v-switch
                v-model="settings.allow_future_posting"
                label="Allow Future Date Posting"
                color="primary"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-switch
                v-model="settings.require_balanced_entries"
                label="Require Balanced Entries"
                color="primary"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="settings.base_currency"
                :items="['USD', 'EUR', 'GBP']"
                label="Base Currency"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="settings.fiscal_year_start_month"
                :items="months"
                label="Fiscal Year Start Month"
              />
            </v-col>
          </v-row>
          <v-btn type="submit" color="primary" :loading="saving">Save Settings</v-btn>
        </v-form>
      </v-card-text>
    </v-card>
>>>>>>> 1f165d554f9014f0b749be3a8fe06df77942d7c1
  </v-container>
</template>

<script setup>
<<<<<<< HEAD
import { ref, onMounted } from 'vue'
import PeriodClosingSettings from '../components/PeriodClosingSettings.vue'
import AuditSettings from '../components/AuditSettings.vue'
import { useGLSettingsStore } from '../store/gl-settings'

const glSettingsStore = useGLSettingsStore()
const activeTab = ref('general')
const loading = ref(false)
const saving = ref(false)

const settings = ref({
  defaultCurrency: 'USD',
  fiscalYearEnd: 'December',
  requireApproval: false,
  enableMultiCurrency: false
})

const currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']
const fiscalYearOptions = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

const periodHeaders = [
  { title: 'Period', key: 'name' },
  { title: 'Start Date', key: 'startDate' },
  { title: 'End Date', key: 'endDate' },
  { title: 'Status', key: 'status' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const accountingPeriods = ref([])

const getPeriodStatusColor = (status) => {
  switch (status) {
    case 'open': return 'success'
    case 'closed': return 'error'
    case 'pending': return 'warning'
    default: return 'grey'
  }
}

const saveGeneralSettings = async () => {
  saving.value = true
  try {
    await glSettingsStore.updateSettings(settings.value)
  } finally {
    saving.value = false
  }
}

const openPeriod = async (period) => {
  await glSettingsStore.openPeriod(period.id)
  loadAccountingPeriods()
}

const closePeriod = async (period) => {
  await glSettingsStore.closePeriod(period.id)
  loadAccountingPeriods()
}

const savePeriodClosingSettings = async (closingSettings) => {
  await glSettingsStore.updatePeriodClosingSettings(closingSettings)
}

const saveAuditSettings = async (auditSettings) => {
  await glSettingsStore.updateAuditSettings(auditSettings)
}

const loadAccountingPeriods = async () => {
  loading.value = true
  try {
    accountingPeriods.value = await glSettingsStore.getAccountingPeriods()
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const currentSettings = await glSettingsStore.getSettings()
  if (currentSettings) {
    settings.value = { ...currentSettings }
  }
  await loadAccountingPeriods()
})
=======
import { ref } from 'vue'

const saving = ref(false)
const settings = ref({
  allow_future_posting: false,
  require_balanced_entries: true,
  base_currency: 'USD',
  fiscal_year_start_month: 1
})

const months = Array.from({length: 12}, (_, i) => ({
  title: new Date(0, i).toLocaleString('default', {month: 'long'}),
  value: i + 1
}))

const saveSettings = async () => {
  saving.value = true
  // API call would go here
  setTimeout(() => { saving.value = false }, 1000)
}
>>>>>>> 1f165d554f9014f0b749be3a8fe06df77942d7c1
</script>