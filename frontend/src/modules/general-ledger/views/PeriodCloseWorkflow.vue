<template>
  <v-container fluid>
    <v-card>
      <v-card-title>Period-End Closing</v-card-title>
      <v-card-text>
        <v-stepper v-model="step">
          <v-stepper-header>
            <v-stepper-item :complete="step > 1" :value="1">Validation</v-stepper-item>
            <v-divider />
            <v-stepper-item :complete="step > 2" :value="2">Review</v-stepper-item>
            <v-divider />
            <v-stepper-item :value="3">Close</v-stepper-item>
          </v-stepper-header>

          <v-stepper-window>
            <v-stepper-window-item :value="1">
              <v-text-field
                v-model="periodEndDate"
                type="date"
                label="Period End Date"
                class="mb-4"
              />
              <v-btn @click="validatePeriod" :loading="validating" color="primary">
                Validate Period
              </v-btn>
              <div v-if="validation" class="mt-4">
                <v-alert :type="validation.can_close ? 'success' : 'error'">
                  {{ validation.can_close ? 'Period can be closed' : 'Period cannot be closed' }}
                </v-alert>
                <div v-if="validation.unposted_entries > 0">
                  Unposted entries: {{ validation.unposted_entries }}
                </div>
              </div>
            </v-stepper-window-item>

            <v-stepper-window-item :value="2">
              <v-list>
                <v-list-item>
                  <v-list-item-title>Total Debits: {{ formatCurrency(validation?.total_debits || 0) }}</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Total Credits: {{ formatCurrency(validation?.total_credits || 0) }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-stepper-window-item>

            <v-stepper-window-item :value="3">
              <v-btn @click="closePeriod" :loading="closing" color="error">
                Close Period
              </v-btn>
            </v-stepper-window-item>
          </v-stepper-window>
        </v-stepper>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'

const step = ref(1)
const validating = ref(false)
const closing = ref(false)
const periodEndDate = ref('')
const validation = ref(null)

const validatePeriod = async () => {
  validating.value = true
  // Mock validation
  validation.value = {
    can_close: true,
    unposted_entries: 0,
    total_debits: 100000,
    total_credits: 100000
  }
  step.value = 2
  validating.value = false
}

const closePeriod = async () => {
  closing.value = true
  setTimeout(() => {
    closing.value = false
    step.value = 1
  }, 2000)
}

const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
</script>