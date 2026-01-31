<template>
  <Card>
    <template #title>Create Purchase Order</template>
    
    <template #content>
      <form @submit.prevent="submitPurchaseOrder">
        <div class="grid">
          <!-- Header Information -->
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="vendor" class="font-semibold">Vendor *</label>
              <Dropdown
                id="vendor"
                v-model="formData.vendor_id"
                :options="vendors"
                optionLabel="name"
                optionValue="id"
                placeholder="Select vendor"
                :class="{ 'p-invalid': errors.vendor_id }"
                class="w-full"
              />
              <small v-if="errors.vendor_id" class="p-error">{{ errors.vendor_id }}</small>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="expected_date" class="font-semibold">Expected Date</label>
              <Calendar
                id="expected_date"
                v-model="formData.expected_date"
                placeholder="Select expected date"
                class="w-full"
              />
            </div>
          </div>
          
          <div class="col-12">
            <div class="field">
              <label for="notes" class="font-semibold">Notes</label>
              <Textarea
                id="notes"
                v-model="formData.notes"
                placeholder="Enter notes"
                rows="2"
                class="w-full"
              />
            </div>
          </div>
          
          <!-- Line Items -->
          <div class="col-12">
            <div class="flex justify-content-between align-items-center mb-4">
              <h3 class="m-0">Line Items</h3>
              <Button icon="pi pi-plus" label="Add Item" size="small" @click="addLineItem" />
            </div>
            
            <Card class="border-1 surface-border">
              <template #content>
                <div v-if="formData.line_items.length === 0" class="text-center py-4">
                  <i class="pi pi-inbox text-4xl text-400 mb-3"></i>
                  <p class="text-500">No items added yet. Click "Add Item" to get started.</p>
                </div>
                
                <div v-else>
                  <div
                    v-for="(item, index) in formData.line_items"
                    :key="index"
                    class="grid align-items-end mb-3 p-3 border-round surface-50"
                  >
                    <div class="col-12 md:col-4">
                      <div class="field">
                        <label class="font-semibold">Item *</label>
                        <Dropdown
                          v-model="item.item_id"
                          :options="inventoryItems"
                          optionLabel="name"
                          optionValue="id"
                          placeholder="Select item"
                          class="w-full"
                          @change="updateLineTotal(index)"
                        />
                      </div>
                    </div>
                    
                    <div class="col-12 md:col-3">
                      <div class="field">
                        <label class="font-semibold">Quantity *</label>
                        <InputNumber
                          v-model="item.quantity_ordered"
                          placeholder="0"
                          class="w-full"
                          :min="0"
                          :maxFractionDigits="4"
                          @input="updateLineTotal(index)"
                        />
                      </div>
                    </div>
                    
                    <div class="col-12 md:col-3">
                      <div class="field">
                        <label class="font-semibold">Unit Cost *</label>
                        <InputNumber
                          v-model="item.unit_cost"
                          mode="currency"
                          currency="USD"
                          locale="en-US"
                          placeholder="0.00"
                          class="w-full"
                          :min="0"
                          @input="updateLineTotal(index)"
                        />
                      </div>
                    </div>
                    
                    <div class="col-12 md:col-2">
                      <div class="flex align-items-center justify-content-between">
                        <div class="text-right">
                          <div class="text-sm text-500">Total</div>
                          <div class="font-semibold">{{ formatCurrency(item.line_total || 0) }}</div>
                        </div>
                        <Button
                          icon="pi pi-trash"
                          size="small"
                          severity="danger"
                          text
                          @click="removeLineItem(index)"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </template>
            </Card>
          </div>
          
          <!-- Totals -->
          <div class="col-12 md:col-6 md:col-offset-6">
            <Card class="bg-primary-50">
              <template #content>
                <div class="flex justify-content-between align-items-center">
                  <span class="font-bold text-lg">Total Amount:</span>
                  <span class="font-bold text-lg text-primary">{{ formatCurrency(totalAmount) }}</span>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </form>
    </template>
    
    <template #footer>
      <div class="flex justify-content-end gap-2">
        <Button label="Cancel" severity="secondary" @click="cancel" />
        <Button
          label="Create Purchase Order"
          :loading="saving"
          :disabled="saving || formData.line_items.length === 0"
          @click="submitPurchaseOrder"
        />
      </div>
    </template>
  </Card>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { apiClient } from '@/utils/apiClient'

// Emits
const emit = defineEmits(['saved', 'cancelled'])

// Composables
const toast = useToast()

// Data
const saving = ref(false)
const vendors = ref([
  { id: 1, name: 'ABC Suppliers Inc.' },
  { id: 2, name: 'XYZ Components Ltd.' },
  { id: 3, name: 'Global Parts Co.' }
])

const inventoryItems = ref([
  { id: 1, name: 'Widget Pro Max', sku: 'WDG-001' },
  { id: 2, name: 'Component X', sku: 'CMP-002' },
  { id: 3, name: 'Assembly Kit', sku: 'ASM-003' }
])

// Form data
const formData = reactive({
  vendor_id: null,
  expected_date: null,
  notes: '',
  line_items: []
})

// Validation errors
const errors = reactive({})

// Computed
const totalAmount = computed(() => {
  return formData.line_items.reduce((sum, item) => sum + (item.line_total || 0), 0)
})

// Methods
const validateForm = () => {
  const newErrors = {}
  
  if (!formData.vendor_id) {
    newErrors.vendor_id = 'Vendor is required'
  }
  
  Object.assign(errors, newErrors)
  return Object.keys(newErrors).length === 0
}

const fetchVendors = async () => {
  try {
    // Mock API call
    // const response = await apiClient.get('/api/v1/accounts-payable/vendors')
    // vendors.value = response.data
  } catch (error) {
    console.error('Error fetching vendors:', error)
  }
}

const fetchInventoryItems = async () => {
  try {
    // Mock API call
    // const response = await apiClient.get('/api/v1/inventory/items')
    // inventoryItems.value = response.data
  } catch (error) {
    console.error('Error fetching inventory items:', error)
  }
}

const addLineItem = () => {
  formData.line_items.push({
    item_id: null,
    quantity_ordered: 1,
    unit_cost: 0,
    line_total: 0
  })
}

const removeLineItem = (index) => {
  formData.line_items.splice(index, 1)
}

const updateLineTotal = (index) => {
  const item = formData.line_items[index]
  const quantity = Number(item.quantity_ordered) || 0
  const unitCost = Number(item.unit_cost) || 0
  item.line_total = quantity * unitCost
}

const submitPurchaseOrder = async () => {
  if (!validateForm() || formData.line_items.length === 0) {
    toast.add({ severity: 'error', summary: 'Validation Error', detail: 'Please fix the errors and add at least one item' })
    return
  }
  
  saving.value = true
  try {
    const payload = {
      vendor_id: formData.vendor_id,
      expected_date: formData.expected_date,
      notes: formData.notes,
      line_items: formData.line_items.map(item => ({
        item_id: item.item_id,
        quantity_ordered: Number(item.quantity_ordered),
        unit_cost: Number(item.unit_cost)
      }))
    }
    
    // await apiClient.post('/api/v1/inventory/purchase-orders', payload)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Purchase order created successfully' })
    emit('saved')
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create purchase order' })
    console.error('Error creating purchase order:', error)
  } finally {
    saving.value = false
  }
}

const cancel = () => {
  emit('cancelled')
}

// Lifecycle hooks
onMounted(() => {
  fetchVendors()
  fetchInventoryItems()
  addLineItem() // Start with one line item
})
</script>

<style scoped>
.field {
  margin-bottom: 1.5rem;
}
</style>