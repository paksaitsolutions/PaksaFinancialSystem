<template>
  <Card>
    <template #title>
      {{ isEdit ? 'Update Count' : 'Create Cycle Count' }}
    </template>
    
    <template #content>
      <form @submit.prevent="isEdit ? null : createCount">
        <div v-if="!isEdit" class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="location" class="font-semibold">Location *</label>
              <Dropdown
                id="location"
                v-model="formData.location_id"
                :options="locations"
                optionLabel="name"
                optionValue="id"
                placeholder="Select location"
                :class="{ 'p-invalid': !formData.location_id }"
                class="w-full"
                @change="loadLocationItems"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="counted_by" class="font-semibold">Counted By</label>
              <InputText
                id="counted_by"
                v-model="formData.counted_by"
                placeholder="Enter counter name"
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
        </div>
        
        <!-- Items to Count -->
        <div v-if="formData.location_id && !isEdit">
          <h3 class="mb-4">Items to Count</h3>
          <DataTable
            v-model:selection="selectedItems"
            :value="locationItems"
            :loading="loadingItems"
            selectionMode="multiple"
            dataKey="id"
            responsiveLayout="scroll"
            class="p-datatable-sm"
          >
            <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
            <Column field="sku" header="SKU" sortable />
            <Column field="name" header="Name" sortable />
            <Column field="quantity_on_hand" header="Current Qty" sortable>
              <template #body="{ data }">
                {{ formatQuantity(data.quantity_on_hand) }}
              </template>
            </Column>
          </DataTable>
        </div>
        
        <!-- Count Progress (Edit Mode) -->
        <div v-if="isEdit && cycleCount">
          <div class="flex align-items-center justify-content-between mb-4">
            <h3>Count Progress</h3>
            <Tag :value="formatStatus(cycleCount.status)" :severity="getStatusSeverity(cycleCount.status)" />
          </div>
          
          <DataTable
            :value="cycleCount.line_items"
            responsiveLayout="scroll"
            class="p-datatable-sm"
          >
            <Column field="is_counted" header="Counted" headerStyle="width: 4rem">
              <template #body="{ data }">
                <i :class="data.is_counted ? 'pi pi-check-circle text-green-500' : 'pi pi-circle text-400'"></i>
              </template>
            </Column>
            
            <Column field="item_sku" header="SKU" sortable />
            <Column field="item_name" header="Name" sortable />
            
            <Column field="system_quantity" header="System Qty">
              <template #body="{ data }">
                {{ formatQuantity(data.system_quantity) }}
              </template>
            </Column>
            
            <Column field="counted_quantity" header="Counted Qty">
              <template #body="{ data }">
                <InputNumber
                  v-if="!data.is_counted && cycleCount.status !== 'completed'"
                  v-model="data.counted_quantity"
                  :maxFractionDigits="4"
                  class="w-full"
                  @blur="updateLineItem(data)"
                />
                <span v-else>{{ formatQuantity(data.counted_quantity) }}</span>
              </template>
            </Column>
            
            <Column field="variance" header="Variance">
              <template #body="{ data }">
                <span :class="getVarianceClass(data.variance)">
                  {{ formatQuantity(data.variance) }}
                </span>
              </template>
            </Column>
          </DataTable>
          
          <div v-if="cycleCount.status === 'in_progress'" class="mt-4">
            <Button
              label="Complete Count"
              severity="success"
              :disabled="!allItemsCounted"
              @click="completeCount"
            />
          </div>
        </div>
      </form>
    </template>
    
    <template #footer v-if="!isEdit">
      <div class="flex justify-content-end gap-2">
        <Button label="Cancel" severity="secondary" @click="cancel" />
        <Button
          label="Create Count"
          :loading="saving"
          :disabled="selectedItems.length === 0"
          @click="createCount"
        />
      </div>
    </template>
  </Card>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { apiClient } from '@/utils/apiClient'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'

// Props
const props = defineProps({
  cycleCount: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['saved', 'cancelled'])

// Composables
const toast = useToast()

// Data
const saving = ref(false)
const loadingItems = ref(false)
const locations = ref([])
const locationItems = ref([])
const selectedItems = ref([])

// Computed
const isEdit = computed(() => !!props.cycleCount)

const allItemsCounted = computed(() => {
  if (!props.cycleCount?.line_items) return false
  return props.cycleCount.line_items.every(item => item.is_counted)
})

// Form data
const formData = reactive({
  location_id: null,
  counted_by: '',
  notes: ''
})

// Methods
const fetchLocations = async () => {
  try {
    // Mock data
    locations.value = [
      { id: 1, name: 'Main Warehouse' },
      { id: 2, name: 'Retail Store' },
      { id: 3, name: 'Production Floor' }
    ]
  } catch (error) {
    console.error('Error fetching locations:', error)
  }
}

const loadLocationItems = async () => {
  if (!formData.location_id) return
  
  loadingItems.value = true
  try {
    // Mock data
    locationItems.value = [
      { id: 1, sku: 'WDG-001', name: 'Widget Pro Max', quantity_on_hand: 150 },
      { id: 2, sku: 'CMP-002', name: 'Component X', quantity_on_hand: 8 }
    ]
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load location items' })
    console.error('Error loading items:', error)
  } finally {
    loadingItems.value = false
  }
}

const createCount = async () => {
  if (selectedItems.value.length === 0) return
  
  saving.value = true
  try {
    const payload = {
      location_id: formData.location_id,
      counted_by: formData.counted_by,
      notes: formData.notes,
      line_items: selectedItems.value.map(item => ({
        item_id: item.id,
        system_quantity: item.quantity_on_hand
      }))
    }
    
    // await apiClient.post('/api/v1/inventory/cycle-counts', payload)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Cycle count created successfully' })
    emit('saved')
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create cycle count' })
    console.error('Error creating cycle count:', error)
  } finally {
    saving.value = false
  }
}

const updateLineItem = async (item) => {
  if (!item.counted_quantity) return
  
  try {
    // await apiClient.put(`/api/v1/inventory/cycle-counts/line-items/${item.id}`, {
    //   counted_quantity: Number(item.counted_quantity),
    //   notes: item.notes || ''
    // })
    
    // Update local data
    item.variance = Number(item.counted_quantity) - Number(item.system_quantity)
    item.is_counted = true
    
    toast.add({ severity: 'success', summary: 'Success', detail: 'Count updated' })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to update count' })
    console.error('Error updating line item:', error)
  }
}

const completeCount = async () => {
  try {
    // await apiClient.post(`/api/v1/inventory/cycle-counts/${props.cycleCount.id}/complete`)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Cycle count completed successfully' })
    emit('saved')
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to complete count' })
    console.error('Error completing count:', error)
  }
}

const cancel = () => {
  emit('cancelled')
}

// Helper methods
const formatQuantity = (quantity) => {
  return Number(quantity || 0).toLocaleString()
}

const formatStatus = (status) => {
  return status.replace('_', ' ').toUpperCase()
}

const getStatusSeverity = (status) => {
  const severities = {
    pending: 'warning',
    in_progress: 'info',
    completed: 'success',
    cancelled: 'danger'
  }
  return severities[status] || 'info'
}

const getVarianceClass = (variance) => {
  const num = Number(variance || 0)
  if (num > 0) return 'text-green-600 font-semibold'
  if (num < 0) return 'text-red-600 font-semibold'
  return ''
}

// Lifecycle hooks
onMounted(() => {
  fetchLocations()
})
</script>

<style scoped>
.field {
  margin-bottom: 1.5rem;
}
</style>