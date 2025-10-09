<template>
  <div class="item-form">
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <div>
            <h2 class="m-0">{{ isEdit ? 'Edit' : 'Add New' }} Inventory Item</h2>
            <p class="text-600 mt-1 mb-0">{{ isEdit ? 'Update item information and settings' : 'Create a new inventory item' }}</p>
          </div>
          <div class="flex gap-2">
            <Button label="Cancel" severity="secondary" @click="$emit('cancel')" />
            <Button label="Save" :loading="saving" @click="saveItem" />
          </div>
        </div>
      </template>
      
      <template #content>
        <form @submit.prevent="saveItem">
          <TabView>
            <!-- Basic Information Tab -->
            <TabPanel header="Basic Information">
              <div class="grid">
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="sku" class="font-semibold">SKU *</label>
                    <InputText
                      id="sku"
                      v-model="form.sku"
                      :class="{ 'p-invalid': errors.sku }"
                      placeholder="Enter SKU"
                      class="w-full"
                    />
                    <small v-if="errors.sku" class="p-error">{{ errors.sku }}</small>
                  </div>
                </div>
                
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="barcode" class="font-semibold">Barcode</label>
                    <div class="p-inputgroup">
                      <InputText
                        id="barcode"
                        v-model="form.barcode"
                        placeholder="Enter or scan barcode"
                        class="w-full"
                      />
                      <Button icon="pi pi-qrcode" @click="scanBarcode" />
                    </div>
                  </div>
                </div>
                
                <div class="col-12">
                  <div class="field">
                    <label for="name" class="font-semibold">Item Name *</label>
                    <InputText
                      id="name"
                      v-model="form.name"
                      :class="{ 'p-invalid': errors.name }"
                      placeholder="Enter item name"
                      class="w-full"
                    />
                    <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
                  </div>
                </div>
                
                <div class="col-12">
                  <div class="field">
                    <label for="description" class="font-semibold">Description</label>
                    <Textarea
                      id="description"
                      v-model="form.description"
                      placeholder="Enter item description"
                      rows="3"
                      class="w-full"
                    />
                  </div>
                </div>
                
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="category" class="font-semibold">Category</label>
                    <Dropdown
                      id="category"
                      v-model="form.category_id"
                      :options="categories"
                      optionLabel="name"
                      optionValue="id"
                      placeholder="Select category"
                      class="w-full"
                      showClear
                    />
                  </div>
                </div>
                
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="status" class="font-semibold">Status *</label>
                    <Dropdown
                      id="status"
                      v-model="form.status"
                      :options="statusOptions"
                      optionLabel="label"
                      optionValue="value"
                      placeholder="Select status"
                      class="w-full"
                    />
                  </div>
                </div>
              </div>
            </TabPanel>
            
            <!-- Inventory Details Tab -->
            <TabPanel header="Inventory Details">
              <div class="grid">
                <div class="col-12 md:col-4">
                  <div class="field">
                    <label for="unit_of_measure" class="font-semibold">Unit of Measure *</label>
                    <Dropdown
                      id="unit_of_measure"
                      v-model="form.unit_of_measure"
                      :options="uomOptions"
                      optionLabel="label"
                      optionValue="value"
                      placeholder="Select UOM"
                      class="w-full"
                      editable
                    />
                  </div>
                </div>
                
                <div class="col-12 md:col-4">
                  <div class="field">
                    <label for="reorder_point" class="font-semibold">Reorder Point</label>
                    <InputNumber
                      id="reorder_point"
                      v-model="form.reorder_point"
                      placeholder="0"
                      class="w-full"
                      :min="0"
                      :maxFractionDigits="4"
                    />
                  </div>
                </div>
                
                <div class="col-12 md:col-4">
                  <div class="field">
                    <label for="reorder_quantity" class="font-semibold">Reorder Quantity</label>
                    <InputNumber
                      id="reorder_quantity"
                      v-model="form.reorder_quantity"
                      placeholder="0"
                      class="w-full"
                      :min="0"
                      :maxFractionDigits="4"
                    />
                  </div>
                </div>
                
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="default_location" class="font-semibold">Default Location</label>
                    <Dropdown
                      id="default_location"
                      v-model="form.default_location_id"
                      :options="locations"
                      optionLabel="name"
                      optionValue="id"
                      placeholder="Select location"
                      class="w-full"
                      showClear
                    />
                  </div>
                </div>
                
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="valuation_method" class="font-semibold">Valuation Method</label>
                    <Dropdown
                      id="valuation_method"
                      v-model="form.valuation_method"
                      :options="valuationMethods"
                      optionLabel="label"
                      optionValue="value"
                      placeholder="Select method"
                      class="w-full"
                    />
                  </div>
                </div>
                
                <div class="col-12">
                  <div class="field-checkbox">
                    <Checkbox id="is_tracked" v-model="form.is_tracked" :binary="true" />
                    <label for="is_tracked" class="ml-2">Track inventory for this item</label>
                  </div>
                </div>
              </div>
            </TabPanel>
            
            <!-- Costing Tab -->
            <TabPanel header="Costing">
              <div class="grid">
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="unit_cost" class="font-semibold">Unit Cost</label>
                    <InputNumber
                      id="unit_cost"
                      v-model="form.unit_cost"
                      mode="currency"
                      currency="USD"
                      locale="en-US"
                      placeholder="0.00"
                      class="w-full"
                      :min="0"
                      :maxFractionDigits="4"
                    />
                  </div>
                </div>
                
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="standard_cost" class="font-semibold">Standard Cost</label>
                    <InputNumber
                      id="standard_cost"
                      v-model="form.standard_cost"
                      mode="currency"
                      currency="USD"
                      locale="en-US"
                      placeholder="0.00"
                      class="w-full"
                      :min="0"
                      :maxFractionDigits="4"
                    />
                  </div>
                </div>
                
                <div class="col-12">
                  <Message severity="info" :closable="false">
                    <p class="m-0">
                      <strong>Unit Cost:</strong> Current cost per unit for inventory valuation.<br>
                      <strong>Standard Cost:</strong> Expected or budgeted cost per unit for variance analysis.
                    </p>
                  </Message>
                </div>
              </div>
            </TabPanel>
            
            <!-- Physical Attributes Tab -->
            <TabPanel header="Physical Attributes">
              <div class="grid">
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="weight" class="font-semibold">Weight</label>
                    <div class="p-inputgroup">
                      <InputNumber
                        id="weight"
                        v-model="form.weight"
                        placeholder="0.00"
                        class="w-full"
                        :min="0"
                        :maxFractionDigits="4"
                      />
                      <span class="p-inputgroup-addon">lbs</span>
                    </div>
                  </div>
                </div>
                
                <div class="col-12 md:col-6">
                  <div class="field">
                    <label for="dimensions" class="font-semibold">Dimensions</label>
                    <InputText
                      id="dimensions"
                      v-model="form.dimensions"
                      placeholder="L x W x H (inches)"
                      class="w-full"
                    />
                  </div>
                </div>
                
                <div class="col-12">
                  <div class="field">
                    <label class="font-semibold">Item Image</label>
                    <FileUpload
                      mode="basic"
                      name="image"
                      accept="image/*"
                      :maxFileSize="1000000"
                      @select="onImageSelect"
                      chooseLabel="Choose Image"
                      class="w-full"
                    />
                    <small class="text-500">Maximum file size: 1MB. Supported formats: JPG, PNG, GIF</small>
                  </div>
                </div>
                
                <div v-if="imagePreview" class="col-12">
                  <div class="field">
                    <label class="font-semibold">Preview</label>
                    <div class="mt-2">
                      <img :src="imagePreview" alt="Item preview" class="border-round" style="max-width: 200px; max-height: 200px;" />
                    </div>
                  </div>
                </div>
              </div>
            </TabPanel>
          </TabView>
        </form>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { inventoryService, type InventoryItem } from '@/services/inventoryService'
import Card from 'primevue/card'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import FileUpload from 'primevue/fileupload'
import Message from 'primevue/message'

// Props
const props = defineProps({
  item: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['save', 'cancel'])

// Composables
const toast = useToast()

// Data
const saving = ref(false)
const imagePreview = ref(null)
const isEdit = ref(!!props.item)

// Form data
const form = reactive({
  sku: '',
  barcode: '',
  name: '',
  description: '',
  category_id: null,
  status: 'active',
  unit_of_measure: 'EA',
  reorder_point: 0,
  reorder_quantity: 0,
  default_location_id: null,
  valuation_method: 'average',
  is_tracked: true,
  unit_cost: 0,
  standard_cost: 0,
  weight: null,
  dimensions: ''
})

// Validation errors
const errors = reactive({})

// Options
const statusOptions = [
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'Discontinued', value: 'discontinued' }
]

const uomOptions = [
  { label: 'Each (EA)', value: 'EA' },
  { label: 'Piece (PC)', value: 'PC' },
  { label: 'Box (BOX)', value: 'BOX' },
  { label: 'Case (CS)', value: 'CS' },
  { label: 'Pound (LB)', value: 'LB' },
  { label: 'Kilogram (KG)', value: 'KG' },
  { label: 'Liter (L)', value: 'L' },
  { label: 'Gallon (GAL)', value: 'GAL' },
  { label: 'Meter (M)', value: 'M' },
  { label: 'Foot (FT)', value: 'FT' }
]

const valuationMethods = [
  { label: 'Average Cost', value: 'average' },
  { label: 'FIFO (First In, First Out)', value: 'fifo' },
  { label: 'LIFO (Last In, First Out)', value: 'lifo' },
  { label: 'Standard Cost', value: 'standard' }
]

const categories = ref([])
const locations = ref([])

const loadCategories = async () => {
  try {
    const response = await inventoryService.getCategories()
    categories.value = response
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

const loadLocations = async () => {
  try {
    const response = await inventoryService.getLocations()
    locations.value = response
  } catch (error) {
    console.error('Error loading locations:', error)
  }
}

// Methods
const validateForm = () => {
  const newErrors = {}
  
  if (!form.sku.trim()) {
    newErrors.sku = 'SKU is required'
  }
  
  if (!form.name.trim()) {
    newErrors.name = 'Item name is required'
  }
  
  Object.assign(errors, newErrors)
  return Object.keys(newErrors).length === 0
}

const saveItem = async () => {
  if (!validateForm()) {
    toast.add({ severity: 'error', summary: 'Validation Error', detail: 'Please fix the errors and try again' })
    return
  }
  
  saving.value = true
  try {
    const itemData: InventoryItem = {
      item_code: form.sku,
      item_name: form.name,
      description: form.description,
      category_id: form.category_id,
      unit_of_measure: form.unit_of_measure,
      cost_price: form.unit_cost,
      selling_price: form.standard_cost,
      reorder_level: form.reorder_point,
      maximum_level: form.reorder_quantity,
      barcode: form.barcode,
      is_active: form.status === 'active'
    }
    
    if (isEdit.value && props.item?.id) {
      await inventoryService.updateItem(props.item.id, itemData)
    } else {
      await inventoryService.createItem(itemData)
    }
    
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: `Item ${isEdit.value ? 'updated' : 'created'} successfully` 
    })
    
    emit('save', itemData)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save item' })
    console.error('Error saving item:', error)
  } finally {
    saving.value = false
  }
}

const scanBarcode = () => {
  // Implement barcode scanning
  toast.add({ severity: 'info', summary: 'Barcode Scanner', detail: 'Barcode scanning will be implemented' })
}

const onImageSelect = (event) => {
  const file = event.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

// Initialize form with item data if editing
const initializeForm = () => {
  if (props.item) {
    form.sku = props.item.item_code || ''
    form.name = props.item.item_name || ''
    form.description = props.item.description || ''
    form.category_id = props.item.category_id || null
    form.unit_of_measure = props.item.unit_of_measure || 'EA'
    form.unit_cost = props.item.cost_price || 0
    form.standard_cost = props.item.selling_price || 0
    form.reorder_point = props.item.reorder_level || 0
    form.reorder_quantity = props.item.maximum_level || 0
    form.barcode = props.item.barcode || ''
    form.status = props.item.is_active ? 'active' : 'inactive'
  }
}

// Watch for prop changes
watch(() => props.item, () => {
  isEdit.value = !!props.item
  initializeForm()
}, { immediate: true })

// Lifecycle
onMounted(() => {
  initializeForm()
  loadCategories()
  loadLocations()
})
</script>

<style scoped>
.item-form {
  padding: 1.5rem;
}

.field {
  margin-bottom: 1.5rem;
}

.field-checkbox {
  margin-bottom: 1.5rem;
}

:deep(.p-tabview-nav) {
  background: var(--surface-50);
}

:deep(.p-tabview-panels) {
  padding: 1.5rem 0;
}

:deep(.p-inputgroup-addon) {
  min-width: 3rem;
}
</style>