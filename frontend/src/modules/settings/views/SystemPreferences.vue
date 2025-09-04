<template>
  <div class="system-preferences">
    <div class="dashboard-header">
      <h1>System Preferences</h1>
      <p>Configure system-wide settings and preferences</p>
    </div>

    <div class="main-content">
      <Card class="content-card">
        <template #title>General Preferences</template>
        <template #content>
          <div class="grid p-fluid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Date Format</label>
                <Dropdown v-model="preferences.dateFormat" :options="dateFormats" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Time Zone</label>
                <Dropdown v-model="preferences.timeZone" :options="timeZones" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Language</label>
                <Dropdown v-model="preferences.language" :options="languages" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Theme</label>
                <Dropdown v-model="preferences.theme" :options="themes" />
              </div>
            </div>
          </div>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>Financial Preferences</template>
        <template #content>
          <div class="grid p-fluid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Fiscal Year Start</label>
                <Dropdown v-model="preferences.fiscalYearStart" :options="months" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Decimal Places</label>
                <Dropdown v-model="preferences.decimalPlaces" :options="decimalOptions" />
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="preferences.enableMultiCurrency" binary />
                  <span class="ml-2">Enable multi-currency support</span>
                </label>
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="preferences.requireApprovals" binary />
                  <span class="ml-2">Require approvals for transactions above threshold</span>
                </label>
              </div>
            </div>
          </div>
        </template>
      </Card>
      
      <Card class="content-card">
        <template #title>Notification Preferences</template>
        <template #content>
          <div class="grid p-fluid">
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="preferences.emailNotifications" binary />
                  <span class="ml-2">Enable email notifications</span>
                </label>
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="preferences.smsNotifications" binary />
                  <span class="ml-2">Enable SMS notifications</span>
                </label>
              </div>
            </div>
            <div class="col-12">
              <div class="field">
                <label class="flex align-items-center">
                  <Checkbox v-model="preferences.pushNotifications" binary />
                  <span class="ml-2">Enable push notifications</span>
                </label>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <div class="actions-footer">
      <Button label="Reset to Defaults" severity="secondary" @click="resetDefaults" />
      <Button label="Save Preferences" icon="pi pi-check" @click="savePreferences" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const preferences = ref({
  dateFormat: 'MM/DD/YYYY',
  timeZone: 'America/New_York',
  language: 'English',
  theme: 'Light',
  fiscalYearStart: 'January',
  decimalPlaces: '2',
  enableMultiCurrency: true,
  requireApprovals: true,
  emailNotifications: true,
  smsNotifications: false,
  pushNotifications: true
})

const dateFormats = ref(['MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD'])
const timeZones = ref(['America/New_York', 'America/Los_Angeles', 'Europe/London', 'Asia/Tokyo'])
const languages = ref(['English', 'Spanish', 'French', 'German'])
const themes = ref(['Light', 'Dark', 'Auto'])
const months = ref(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
const decimalOptions = ref(['0', '1', '2', '3', '4'])

const savePreferences = () => {
  console.log('Saving preferences:', preferences.value)
}

const resetDefaults = () => {
  preferences.value = {
    dateFormat: 'MM/DD/YYYY',
    timeZone: 'America/New_York',
    language: 'English',
    theme: 'Light',
    fiscalYearStart: 'January',
    decimalPlaces: '2',
    enableMultiCurrency: false,
    requireApprovals: false,
    emailNotifications: true,
    smsNotifications: false,
    pushNotifications: true
  }
}
</script>

<style scoped>
.system-preferences {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.dashboard-header p {
  color: #6b7280;
  margin: 0;
}

.main-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.content-card {
  height: fit-content;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}

.actions-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

@media (max-width: 768px) {
  .system-preferences {
    padding: 1rem;
  }
  
  .actions-footer {
    flex-direction: column;
  }
}
</style>