<template>
  <Dialog 
    v-model:visible="visible" 
    :header="payment?.id ? 'Edit Payment' : 'New Payment'" 
    :modal="true"
    :style="{ width: '700px' }"
    @hide="close"
  >
    <form @submit.prevent="handleSubmit" class="p-fluid">
      <div class="formgrid grid">
        <!-- Payment Details -->
        <div class="field col-12 md:col-6">
          <label for="paymentNumber">Payment Number</label>
          <InputText 
            id="paymentNumber" 
            v-model="formData.paymentNumber" 
            required
            :disabled="!!payment?.id"
          />
        </div>
        
        <div class="field col-12 md:col-6">
          <label for="paymentDate">Payment Date</label>
          <Calendar 
            id="paymentDate" 
            v-model="formData.paymentDate" 
            required
            dateFormat="yy-mm-dd"
            showIcon
          />
        </div>
        
        <div class="field col-12">
          <label for="vendorId">Vendor</label>
          <Dropdown 
            id="vendorId"
            v-model="formData.vendorId"
            :options="vendors"
            optionLabel="name"
            optionValue="id"
            placeholder="Select a vendor"
            required
          />
        </div>
        
        <div class="field col-12 md:col-6">
          <label for="amount">Amount</label>
          <InputNumber 
            id="amount" 
            v-model="formData.amount" 
            mode="currency" 
            currency="USD" 
            locale="en-US"
            required
          />
        </div>
        
        <div class="field col-12 md:col-6">
          <label for="method">Payment Method</label>
          <Dropdown 
            id="method"
            v-model="formData.method"
            :options="paymentMethods"
            optionLabel="label"
            optionValue="value"
            required
          />
        </div>
        
        <div class="field col-12">
          <label for="reference">Reference</label>
          <InputText 
            id="reference" 
            v-model="formData.reference" 
            placeholder="e.g., Invoice #, PO #"
          />
        </div>
        
        <div class="field col-12">
          <label for="memo">Memo</label>
          <Textarea 
            id="memo" 
            v-model="formData.memo" 
            rows="3" 
            autoResize 
            placeholder="Additional notes about this payment"
          />
        </div>
      </div>
      
      <div class="flex justify-content-end gap-2 mt-4">
        <Button 
          type="button" 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="close"
        />
        <Button 
          type="submit" 
          :label="payment?.id ? 'Update' : 'Create'" 
          icon="pi pi-check" 
          :loading="isSubmitting"
        />
      </div>
    </form>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import type { Payment, PaymentMethod as PaymentMethodType } from '@/types/payments'

const emit = defineEmits(['update:visible', 'save', 'cancel'])
const props = defineProps<{
  visible: boolean
  payment: Payment | null
}>()

const toast = useToast()
const isSubmitting = ref(false)

// Mock vendor data - replace with API call
const vendors = ref([
  { id: 'VEND-001', name: 'ABC Suppliers Inc.' },
  { id: 'VEND-002', name: 'XYZ Manufacturing' },
  { id: 'VEND-003', name: 'Global Distributors' },
  { id: 'VEND-004', name: 'Tech Solutions Ltd.' },
])

// Payment method options
const paymentMethods = [
  { value: 'bank_transfer', label: 'Bank Transfer' },
  { value: 'credit_card', label: 'Credit Card' },
  { value: 'debit_card', label: 'Debit Card' },
  { value: 'check', label: 'Check' },
  { value: 'cash', label: 'Cash' },
  { value: 'other', label: 'Other' }
]

// Form data
const formData = reactive({
  paymentNumber: '',
  paymentDate: new Date(),
  vendorId: '',
  amount: 0,
  method: 'bank_transfer' as PaymentMethodType,
  reference: '',
  memo: '',
  status: 'draft' as const
})

// Reset form when modal is opened/closed
watch(() => props.visible, (newVal) => {
  if (newVal) {
    resetForm()
  }
})

// Populate form when editing
watch(() => props.payment, (newPayment) => {
  if (newPayment) {
    Object.assign(formData, {
      paymentNumber: newPayment.paymentNumber,
      paymentDate: new Date(newPayment.paymentDate),
      vendorId: newPayment.vendorId,
      amount: newPayment.amount,
      method: newPayment.method,
      reference: newPayment.reference || '',
      memo: newPayment.memo || '',
      status: newPayment.status
    })
  }
}, { immediate: true })

const resetForm = () => {
  formData.paymentNumber = ''
  formData.paymentDate = new Date()
  formData.vendorId = ''
  formData.amount = 0
  formData.method = 'bank_transfer'
  formData.reference = ''
  formData.memo = ''
  formData.status = 'draft'
  
  // Generate a new payment number if creating
  if (!props.payment?.id) {
    generatePaymentNumber()
  }
}

const generatePaymentNumber = () => {
  // In a real app, this would come from the backend
  const random = Math.floor(1000 + Math.random() * 9000)
  const date = new Date()
  formData.paymentNumber = `PAY-${date.getFullYear()}${(date.getMonth() + 1).toString().padStart(2, '0')}-${random}`
}

const close = () => {
  emit('update:visible', false)
  emit('cancel')
}

const handleSubmit = async () => {
  isSubmitting.value = true
  
  try {
    // Validate form data
    if (!formData.paymentNumber || !formData.vendorId || formData.amount <= 0) {
      throw new Error('Please fill in all required fields')
    }
    
    // Prepare payment data
    const paymentData = {
      ...formData,
      id: props.payment?.id || Date.now().toString(),
      paymentDate: formData.paymentDate.toISOString(),
      vendorName: vendors.value.find(v => v.id === formData.vendorId)?.name || 'Unknown Vendor',
      currency: 'USD',
      createdAt: props.payment?.createdAt || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      createdBy: 'currentUser', // Replace with actual user
      updatedBy: 'currentUser'  // Replace with actual user
    }
    
    // Emit save event with payment data
    emit('save', paymentData)
    
    // Close modal after a short delay
    setTimeout(() => {
      close()
      isSubmitting.value = false
    }, 500)
    
  } catch (error) {
    console.error('Error saving payment:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error instanceof Error ? error.message : 'Failed to save payment',
      life: 3000
    })
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.field {
  margin-bottom: 1.5rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.p-fluid .p-inputtext,
.p-fluid .p-dropdown,
.p-fluid .p-calendar,
.p-fluid .p-inputnumber,
.p-fluid .p-textarea {
  width: 100%;
}

/* Responsive adjustments */
@media screen and (max-width: 768px) {
  .formgrid > .field {
    width: 100%;
  }
}
</style>
