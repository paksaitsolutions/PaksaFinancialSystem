<template>
  <div class="record-payment">
    <Card>
      <template #title>Record Payment</template>
      <template #content>
        <form @submit.prevent="handleSubmit">
          <div class="p-fluid">
            <div class="field">
              <label for="bill">Select Bill</label>
              <Dropdown 
                id="bill"
                v-model="form.billId" 
                :options="bills" 
                optionLabel="displayName" 
                optionValue="id"
                placeholder="Select a bill to pay"
                :class="{ 'p-invalid': errors.billId }"
              />
              <small v-if="errors.billId" class="p-error">{{ errors.billId }}</small>
            </div>

            <div class="field">
              <label for="paymentAmount">Payment Amount</label>
              <InputNumber 
                id="paymentAmount"
                v-model="form.paymentAmount" 
                mode="currency" 
                currency="USD"
                :class="{ 'p-invalid': errors.paymentAmount }"
              />
              <small v-if="errors.paymentAmount" class="p-error">{{ errors.paymentAmount }}</small>
            </div>

            <div class="field">
              <label for="paymentDate">Payment Date</label>
              <Calendar 
                id="paymentDate"
                v-model="form.paymentDate" 
                dateFormat="mm/dd/yy"
                :class="{ 'p-invalid': errors.paymentDate }"
              />
              <small v-if="errors.paymentDate" class="p-error">{{ errors.paymentDate }}</small>
            </div>

            <div class="field">
              <label for="paymentMethod">Payment Method</label>
              <Dropdown 
                id="paymentMethod"
                v-model="form.paymentMethod" 
                :options="paymentMethods" 
                optionLabel="label" 
                optionValue="value"
                placeholder="Select payment method"
                :class="{ 'p-invalid': errors.paymentMethod }"
              />
              <small v-if="errors.paymentMethod" class="p-error">{{ errors.paymentMethod }}</small>
            </div>

            <div class="field">
              <label for="reference">Reference Number</label>
              <InputText 
                id="reference"
                v-model="form.reference" 
                placeholder="Enter reference number (check #, etc.)"
              />
            </div>

            <div class="field">
              <label for="notes">Notes</label>
              <Textarea 
                id="notes"
                v-model="form.notes" 
                rows="3"
                placeholder="Enter payment notes"
              />
            </div>

            <div class="flex gap-2">
              <Button type="submit" label="Record Payment" :loading="loading" />
              <Button type="button" label="Cancel" class="p-button-secondary" @click="$router.go(-1)" />
            </div>
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  billId: null,
  paymentAmount: null,
  paymentDate: new Date(),
  paymentMethod: null,
  reference: '',
  notes: ''
})

const errors = reactive({
  billId: '',
  paymentAmount: '',
  paymentDate: '',
  paymentMethod: ''
})

const bills = ref([
  { id: 1, displayName: 'BILL-001 - ABC Supplies Co. ($2,500.00)' },
  { id: 2, displayName: 'BILL-002 - XYZ Services Ltd. ($1,800.00)' },
  { id: 3, displayName: 'BILL-003 - Tech Solutions Inc. ($3,200.00)' }
])

const paymentMethods = ref([
  { label: 'Check', value: 'check' },
  { label: 'ACH Transfer', value: 'ach' },
  { label: 'Wire Transfer', value: 'wire' },
  { label: 'Credit Card', value: 'credit_card' },
  { label: 'Cash', value: 'cash' }
])

const handleSubmit = async () => {
  // Clear errors
  Object.keys(errors).forEach(key => errors[key] = '')
  
  // Validate
  if (!form.billId) errors.billId = 'Bill selection is required'
  if (!form.paymentAmount) errors.paymentAmount = 'Payment amount is required'
  if (!form.paymentDate) errors.paymentDate = 'Payment date is required'
  if (!form.paymentMethod) errors.paymentMethod = 'Payment method is required'
  
  if (Object.values(errors).some(error => error)) return
  
  loading.value = true
  try {
    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    router.push('/ap')
  } catch (error) {
    console.error('Failed to record payment:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.record-payment {
  max-width: 600px;
  margin: 0 auto;
}
</style>