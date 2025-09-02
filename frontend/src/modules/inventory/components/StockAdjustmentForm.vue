<template>
  <div class="stock-adjustment-form">
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <div>
            <h2 class="m-0">Stock Adjustment</h2>
            <p class="text-600 mt-1 mb-0">Adjust inventory quantities and track changes</p>
          </div>
          <div class="flex gap-2">
            <Button label="Cancel" severity="secondary" @click="$emit('cancelled')" />
            <Button label="Save Adjustment" :loading="saving" @click="saveAdjustment" />
          </div>
        </div>
      </template>
      
      <template #content>
        <form @submit.prevent="saveAdjustment">
          <div class="grid">
            <!-- Item Selection -->
            <div class="col-12">
              <div class="field">
                <label for="item" class="font-semibold">Select Item *</label>
                <Dropdown
                  id="item"
                  v-model="formData.item_id"
                  :options="items"
                  optionLabel="name"
                  optionValue="id"
                  placeholder="Search and select an item"
                  :class="{ 'p-invalid': errors.item_id }"
                  class="w-full"
                  filter
                  @change="onItemSelected"
                >
                  <template #option="{ option }">
                    <div class="flex align-items-center gap-2">
                      <div class="flex-1">
                        <div class="font-medium">{{ option.name }}</div>
                        <div class="text-sm text-500">SKU: {{ option.sku }} | On Hand: {{ option.quantity_on_hand }}</div>
                      </div>
                    </div>
                  </template>
                </Dropdown>
                <small v-if="errors.item_id" class="p-error">{{ errors.item_id }}</small>
              </div>
            </div>
            
            <!-- Current Stock Info -->
            <div v-if="selectedItem" class="col-12">
              <Card class="bg-primary-50">
                <template #content>
                  <div class="grid">
                    <div class="col-12 md:col-3">
                      <div class="text-center">
                        <div class="text-500 font-medium mb-1">Current Stock</div>
                        <div class="text-2xl font-bold text-900">{{ selectedItem.quantity_on_hand.toLocaleString() }}</div>
                        <div class="text-sm text-500">{{ selectedItem.unit_of_measure }}</div>
                      </div>
                    </div>
                    <div class="col-12 md:col-3">
                      <div class="text-center">
                        <div class="text-500 font-medium mb-1">Unit Cost</div>
                        <div class="text-xl font-semibold text-900">{{ formatCurrency(selectedItem.unit_cost) }}</div>
                      </div>
                    </div>
                    <div class="col-12 md:col-3">
                      <div class="text-center">
                        <div class="text-500 font-medium mb-1">Total Value</div>
                        <div class="text-xl font-semibold text-900">{{ formatCurrency(selectedItem.unit_cost * selectedItem.quantity_on_hand) }}</div>
                      </div>
                    </div>
                    <div class="col-12 md:col-3">
                      <div class="text-center">
                        <div class="text-500 font-medium mb-1">Reorder Point</div>
                        <div class="text-xl font-semibold text-900">{{ selectedItem.reorder_point || 0 }}</div>
                      </div>
                    </div>
                  </div>
                </template>
              </Card>
            </div>
            
            <!-- Adjustment Details -->
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="adjustment_type" class="font-semibold">Adjustment Type *</label>
                <Dropdown
                  id="adjustment_type"
                  v-model="formData.adjustment_type"
                  :options="adjustmentTypes"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Select adjustment type"
                  :class="{ 'p-invalid': errors.adjustment_type }"
                  class="w-full"
                />
                <small v-if="errors.adjustment_type" class="p-error">{{ errors.adjustment_type }}</small>
              </div>
            </div>
            
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="quantity" class="font-semibold">{{ getQuantityLabel() }} *</label>
                <InputNumber
                  id="quantity"
                  v-model="formData.quantity"
                  :class="{ 'p-invalid': errors.quantity }"
                  placeholder="Enter quantity"
                  class="w-full"
                  :min="0"
                  :maxFractionDigits="4"
                />
                <small v-if="errors.quantity" class="p-error">{{ errors.quantity }}</small>
              </div>
            </div>
            
            <!-- New Quantity Preview -->
            <div v-if="selectedItem && formData.quantity && formData.adjustment_type" class="col-12">
              <Message severity="info" :closable="false">
                <div class="flex align-items-center gap-3">
                  <i class="pi pi-info-circle"></i>
                  <div>
                    <strong>Adjustment Preview:</strong>
                    {{ selectedItem.quantity_on_hand.toLocaleString() }} → 
                    <span :class="getNewQuantityClass()">{{ newQuantity.toLocaleString() }}</span>
                    ({{ getAdjustmentDescription() }})
                  </div>
                </div>
              </Message>
            </div>
            
            <!-- Reason and Notes -->
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="reason_code" class="font-semibold">Reason Code *</label>
                <Dropdown
                  id="reason_code"
                  v-model="formData.reason_code"
                  :options="reasonCodes"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Select reason"
                  :class="{ 'p-invalid': errors.reason_code }"
                  class="w-full"
                />
                <small v-if="errors.reason_code" class="p-error">{{ errors.reason_code }}</small>
              </div>
            </div>
            
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="location" class="font-semibold">Location</label>
                <Dropdown
                  id="location"
                  v-model="formData.location_id"
                  :options="locations"
                  optionLabel="name"
                  optionValue="id"
                  placeholder="Select location (optional)"
                  class="w-full"
                  showClear
                />
              </div>
            </div>
            
            <div class="col-12">
              <div class="field">
                <label for="notes" class="font-semibold">Notes</label>
                <Textarea
                  id="notes"
                  v-model="formData.notes"
                  placeholder="Enter additional notes or comments"
                  rows="3"
                  class="w-full"
                />
              </div>
            </div>
            
            <!-- Cost Impact -->
            <div v-if="selectedItem && formData.quantity && formData.adjustment_type" class="col-12">
              <Card class="bg-orange-50">
                <template #content>
                  <div class="flex align-items-center gap-3">
                    <i class="pi pi-dollar text-orange-500 text-2xl"></i>
                    <div>
                      <div class="font-semibold text-900">Cost Impact</div>
                      <div class="text-sm text-600">
                        Value change: <span :class="getCostImpactClass()">{{ formatCurrency(getCostImpact()) }}</span>
                      </div>
                    </div>
                  </div>
                </template>
              </Card>
            </div>
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { formatCurrency } from '@/utils/formatters'
import { apiClient } from '@/utils/apiClient'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Message from 'primevue/message'

// Emits
const emit = defineEmits(['saved', 'cancelled'])

// Composables
const toast = useToast()

// Data
const saving = ref(false)
const selectedItem = ref(null)

const formData = reactive({
  item_id: null,
  adjustment_type: '',
  quantity: null,
  reason_code: '',
  location_id: null,
  notes: ''
})

// Validation errors
const errors = reactive({})

// Mock data
const items = ref([
  {
    id: 1,
    name: 'Widget Pro Max',
    sku: 'WDG-001',
    quantity_on_hand: 150,
    unit_cost: 25.99,
    reorder_point: 50,
    unit_of_measure: 'EA'
  },
  {
    id: 2,
    name: 'Component X',
    sku: 'CMP-002',
    quantity_on_hand: 8,
    unit_cost: 45.50,
    reorder_point: 20,
    unit_of_measure: 'EA'
  }
])

const locations = ref([
  { id: 1, name: 'Main Warehouse' },
  { id: 2, name: 'Retail Store' },
  { id: 3, name: 'Production Floor' }
])

// Options
const adjustmentTypes = [
  { label: 'Increase Quantity', value: 'increase' },
  { label: 'Decrease Quantity', value: 'decrease' },
  { label: 'Set Quantity To', value: 'set_to' }
]

const reasonCodes = [
  { label: 'Physical Count Variance', value: 'physical_count' },
  { label: 'Damaged Goods', value: 'damaged' },
  { label: 'Expired Items', value: 'expired' },
  { label: 'Theft/Loss', value: 'theft_loss' },
  { label: 'System Error', value: 'system_error' },
  { label: 'Production Consumption', value: 'production' },
  { label: 'Customer Return', value: 'return' },
  { label: 'Other', value: 'other' }
]

// Computed
const newQuantity = computed(() => {
  if (!selectedItem.value || !formData.quantity || !formData.adjustment_type) {
    return selectedItem.value?.quantity_on_hand || 0
  }
  
  const current = selectedItem.value.quantity_on_hand
  const adjustment = parseFloat(formData.quantity)
  
  switch (formData.adjustment_type) {
    case 'increase':
      return current + adjustment
    case 'decrease':
      return Math.max(0, current - adjustment)
    case 'set_to':
      return adjustment
    default:
      return current
  }
})

// Methods
const validateForm = () => {
  const newErrors = {}
  
  if (!formData.item_id) {
    newErrors.item_id = 'Item is required'
  }
  
  if (!formData.adjustment_type) {
    newErrors.adjustment_type = 'Adjustment type is required'
  }
  
  if (!formData.quantity || formData.quantity <= 0) {
    newErrors.quantity = 'Quantity is required and must be greater than 0'
  }
  
  if (!formData.reason_code) {
    newErrors.reason_code = 'Reason code is required'
  }
  
  Object.assign(errors, newErrors)
  return Object.keys(newErrors).length === 0
}

const onItemSelected = () => {
  selectedItem.value = items.value.find(item => item.id === formData.item_id)
}

const getQuantityLabel = () => {
  switch (formData.adjustment_type) {
    case 'increase':
      return 'Quantity to Add'
    case 'decrease':
      return 'Quantity to Remove'
    case 'set_to':
      return 'New Quantity'
    default:
      return 'Quantity'
  }
}

const getAdjustmentDescription = () => {
  if (!selectedItem.value || !formData.quantity) return ''
  
  const current = selectedItem.value.quantity_on_hand
  const adjustment = parseFloat(formData.quantity)
  const difference = newQuantity.value - current
  
  if (difference > 0) {
    return `+${difference.toLocaleString()}`
  } else if (difference < 0) {
    return `${difference.toLocaleString()}`
  }
  return 'No change'
}

const getNewQuantityClass = () => {
  if (!selectedItem.value) return ''
  
  const current = selectedItem.value.quantity_on_hand
  const difference = newQuantity.value - current
  
  if (difference > 0) return 'text-green-600 font-semibold'
  if (difference < 0) return 'text-red-600 font-semibold'
  return 'text-600'
}

const getCostImpact = () => {
  if (!selectedItem.value || !formData.quantity) return 0
  
  const current = selectedItem.value.quantity_on_hand
  const difference = newQuantity.value - current
  return difference * selectedItem.value.unit_cost
}

const getCostImpactClass = () => {
  const impact = getCostImpact()
  if (impact > 0) return 'text-green-600 font-semibold'
  if (impact < 0) return 'text-red-600 font-semibold'
  return 'text-600'
}

const saveAdjustment = async () => {
  if (!validateForm()) {
    toast.add({ severity: 'error', summary: 'Validation Error', detail: 'Please fix the errors and try again' })
    return
  }
  
  saving.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    toast.add({ severity: 'success', summary: 'Success', detail: 'Stock adjustment saved successfully' })
    emit('saved')
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save adjustment' })
    console.error('Error saving adjustment:', error)
  } finally {
    saving.value = false
  }
}

// Lifecycle hooks
onMounted(() => {
  // fetchItems() - would load from API
})
</script>

<style scoped>
.stock-adjustment-form {
  padding: 1.5rem;
}

.field {
  margin-bottom: 1.5rem;
}

:deep(.p-message .p-message-wrapper) {
  padding: 1rem;
}
</style>