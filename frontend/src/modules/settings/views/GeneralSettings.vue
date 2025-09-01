<template>
  <Card>
    <template #header>
      <h3 class="p-4 m-0">General Settings</h3>
    </template>
    <template #content>
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="companyName">Company Name</label>
            <InputText id="companyName" v-model="settings.companyName" class="w-full" />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="currency">Default Currency</label>
            <Dropdown 
              id="currency" 
              v-model="settings.currency" 
              :options="currencies" 
              optionLabel="label" 
              optionValue="value"
              class="w-full" 
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="timezone">Timezone</label>
            <Dropdown 
              id="timezone" 
              v-model="settings.timezone" 
              :options="timezones" 
              optionLabel="label" 
              optionValue="value"
              class="w-full" 
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="dateFormat">Date Format</label>
            <Dropdown 
              id="dateFormat" 
              v-model="settings.dateFormat" 
              :options="dateFormats" 
              optionLabel="label" 
              optionValue="value"
              class="w-full" 
            />
          </div>
        </div>
      </div>
      
      <div class="flex justify-content-end mt-4">
        <Button label="Save Settings" @click="saveSettings" />
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const settings = ref({
  companyName: 'Paksa Financial System',
  currency: 'USD',
  timezone: 'UTC',
  dateFormat: 'MM/DD/YYYY'
})

const currencies = [
  { label: 'US Dollar (USD)', value: 'USD' },
  { label: 'Euro (EUR)', value: 'EUR' },
  { label: 'British Pound (GBP)', value: 'GBP' }
]

const timezones = [
  { label: 'UTC', value: 'UTC' },
  { label: 'Eastern Time (ET)', value: 'America/New_York' },
  { label: 'Pacific Time (PT)', value: 'America/Los_Angeles' }
]

const dateFormats = [
  { label: 'MM/DD/YYYY', value: 'MM/DD/YYYY' },
  { label: 'DD/MM/YYYY', value: 'DD/MM/YYYY' },
  { label: 'YYYY-MM-DD', value: 'YYYY-MM-DD' }
]

const saveSettings = () => {
  console.log('Saving settings:', settings.value)
}
</script>