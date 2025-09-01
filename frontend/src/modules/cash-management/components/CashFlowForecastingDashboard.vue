<template>
  <div class="cash-flow-forecasting-dashboard">
    <Card>
      <template #title>Cash Flow Forecasting</template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="forecastPeriod">Forecast Period</label>
              <Dropdown 
                id="forecastPeriod"
                v-model="forecastParams.period"
                :options="periodOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Select period"
                class="w-full"
              />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="forecastMethod">Method</label>
              <Dropdown 
                id="forecastMethod"
                v-model="forecastParams.method"
                :options="methodOptions"
                optionLabel="label"
                optionValue="value"
                placeholder="Select method"
                class="w-full"
              />
            </div>
          </div>
        </div>
        
        <Button 
          label="Generate Forecast" 
          icon="pi pi-chart-line"
          @click="generateForecast"
          :loading="loading"
        />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const emit = defineEmits(['forecast'])

const loading = ref(false)
const forecastParams = reactive({
  period: '3months',
  method: 'historical'
})

const periodOptions = [
  { label: '1 Month', value: '1month' },
  { label: '3 Months', value: '3months' },
  { label: '6 Months', value: '6months' },
  { label: '1 Year', value: '1year' }
]

const methodOptions = [
  { label: 'Historical Analysis', value: 'historical' },
  { label: 'Trend Analysis', value: 'trend' },
  { label: 'Seasonal Analysis', value: 'seasonal' }
]

const generateForecast = async () => {
  loading.value = true
  try {
    emit('forecast', forecastParams)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
</style>