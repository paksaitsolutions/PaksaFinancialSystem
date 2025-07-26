<template>
  <v-container fluid>
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
  </v-container>
</template>

<script setup>
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
</script>