<template>
  <div class="inventory-management">
    <!-- Item Detail View -->
    <div v-if="selectedItem">
      <Card>
        <template #content>
          <div class="flex align-items-center justify-content-between p-3 bg-primary-50 border-round mb-4">
            <div class="flex align-items-center gap-3">
              <Button icon="pi pi-arrow-left" text @click="clearSelection" />
              <div>
                <h3 class="m-0 text-900">{{ selectedItem.name }}</h3>
                <p class="text-600 m-0">SKU: {{ selectedItem.sku }}</p>
              </div>
            </div>
            <div class="flex gap-2">
              <Button icon="pi pi-pencil" label="Edit" @click="editItem(selectedItem)" />
              <Button icon="pi pi-plus" label="Adjust Stock" severity="success" @click="adjustStock(selectedItem)" />
            </div>
          </div>
          
          <!-- Item details content -->
          <div class="grid">
            <div class="col-12 md:col-8">
              <h4>Item Information</h4>
              <div class="grid">
                <div class="col-6">
                  <div class="field">
                    <label class="font-semibold text-900">Status</label>
                    <div class="mt-1">
                      <Tag :value="formatStatus(selectedItem.status)" :severity="getStatusSeverity(selectedItem.status)" />
                    </div>
                  </div>
                </div>
                <div class="col-6">
                  <div class="field">
                    <label class="font-semibold text-900">Unit of Measure</label>
                    <p class="mt-1 mb-0">{{ selectedItem.unit_of_measure }}</p>
                  </div>
                </div>
                <div class="col-6">
                  <div class="field">
                    <label class="font-semibold text-900">Unit Cost</label>
                    <p class="mt-1 mb-0">{{ formatCurrency(selectedItem.unit_cost) }}</p>
                  </div>
                </div>
                <div class="col-6">
                  <div class="field">
                    <label class="font-semibold text-900">Total Value</label>
                    <p class="mt-1 mb-0">{{ formatCurrency(selectedItem.unit_cost * selectedItem.quantity_on_hand) }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="col-12 md:col-4">
              <h4>Stock Levels</h4>
              <div class="grid">
                <div class="col-12">
                  <div class="field">
                    <label class="font-semibold text-900">On Hand</label>
                    <p class="mt-1 mb-0 text-2xl font-bold">{{ selectedItem.quantity_on_hand.toLocaleString() }}</p>
                  </div>
                </div>
                <div class="col-6">
                  <div class="field">
                    <label class="font-semibold text-900">Reorder Point</label>
                    <p class="mt-1 mb-0">{{ selectedItem.reorder_point || 0 }}</p>
                  </div>
                </div>
                <div class="col-6">
                  <div class="field">
                    <label class="font-semibold text-900">Reorder Qty</label>
                    <p class="mt-1 mb-0">{{ selectedItem.reorder_quantity || 0 }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>
    
    <!-- Item Form View -->
    <div v-else-if="isCreating || isEditing">
      <ItemForm
        :item="editingItem"
        @save="handleItemSaved"
        @cancel="clearSelection"
      />
    </div>
    
    <!-- Main Inventory Management View -->
    <div v-else>
      <!-- Header -->
      <div class="flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="text-3xl font-bold text-900 m-0">Inventory Management</h1>
          <p class="text-600 mt-1 mb-0">Comprehensive inventory control and management</p>
        </div>
      </div>
      
      <!-- Navigation Tabs -->
      <TabView v-model:activeIndex="activeTabIndex">
        <TabPanel header="Items">
          <InventoryList @view="viewItem" @create="createItem" />
        </TabPanel>
        
        <TabPanel header="Reports & Analytics">
          <InventoryReports />
        </TabPanel>
        
        <TabPanel header="Forecasting">
          <InventoryForecast />
        </TabPanel>
        
        <TabPanel header="Purchase Orders">
          <Card>
            <template #title>
              <div class="flex justify-content-between align-items-center">
                <span>Purchase Orders</span>
                <Button icon="pi pi-plus" label="New Purchase Order" @click="showPurchaseOrderForm = true" />
              </div>
            </template>
            <template #content>
              <PurchaseOrderForm
                v-if="showPurchaseOrderForm"
                @saved="handlePurchaseOrderSaved"
                @cancelled="showPurchaseOrderForm = false"
              />
              <div v-else class="text-center py-6">
                <i class="pi pi-file-o text-4xl text-400 mb-3"></i>
                <p class="text-500">Purchase order management will be implemented here</p>
              </div>
            </template>
          </Card>
        </TabPanel>
        
        <TabPanel header="Cycle Counting">
          <Card>
            <template #title>
              <div class="flex justify-content-between align-items-center">
                <span>Cycle Counting</span>
                <Button icon="pi pi-plus" label="New Cycle Count" @click="showCycleCountForm = true" />
              </div>
            </template>
            <template #content>
              <CycleCountForm
                v-if="showCycleCountForm"
                @saved="handleCycleCountSaved"
                @cancelled="showCycleCountForm = false"
              />
              <div v-else class="text-center py-6">
                <i class="pi pi-calculator text-4xl text-400 mb-3"></i>
                <p class="text-500">Cycle counting management will be implemented here</p>
              </div>
            </template>
          </Card>
        </TabPanel>
        
        <TabPanel header="Stock Adjustments">
          <Card>
            <template #title>
              <div class="flex justify-content-between align-items-center">
                <span>Stock Adjustments</span>
                <Button icon="pi pi-plus" label="New Adjustment" @click="showAdjustmentForm = true" />
              </div>
            </template>
            <template #content>
              <StockAdjustmentForm
                v-if="showAdjustmentForm"
                @saved="handleAdjustmentSaved"
                @cancelled="showAdjustmentForm = false"
              />
              <div v-else class="text-center py-6">
                <i class="pi pi-sliders-h text-4xl text-400 mb-3"></i>
                <p class="text-500">Stock adjustment history will be displayed here</p>
              </div>
            </template>
          </Card>
        </TabPanel>
        
        <TabPanel header="Categories">
          <CategoryManagement />
        </TabPanel>
        
        <TabPanel header="Locations">
          <LocationManagement />
        </TabPanel>
        
        <TabPanel header="Transactions">
          <TransactionHistory />
        </TabPanel>
      </TabView>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { formatCurrency } from '@/utils/formatters'
import Card from 'primevue/card'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import InventoryList from '../components/InventoryList.vue'
import ItemForm from '../components/ItemForm.vue'
import StockAdjustmentForm from '../components/StockAdjustmentForm.vue'
import CategoryManagement from '../components/CategoryManagement.vue'
import PurchaseOrderForm from '../components/PurchaseOrderForm.vue'
import InventoryReports from '../components/InventoryReports.vue'
import CycleCountForm from '../components/CycleCountForm.vue'
import InventoryForecast from '../components/InventoryForecast.vue'
import LocationManagement from '../components/LocationManagement.vue'
import TransactionHistory from '../components/TransactionHistory.vue'

// Composables
const router = useRouter()
const toast = useToast()

// Data
const activeTabIndex = ref(0)
const selectedItem = ref(null)
const editingItem = ref(null)
const isCreating = ref(false)
const isEditing = ref(false)
const showAdjustmentForm = ref(false)
const showPurchaseOrderForm = ref(false)
const showCycleCountForm = ref(false)

// Methods
const viewItem = (item) => {
  selectedItem.value = item
  isCreating.value = false
  isEditing.value = false
}

const createItem = () => {
  selectedItem.value = null
  editingItem.value = null
  isCreating.value = true
  isEditing.value = false
}

const editItem = (item) => {
  selectedItem.value = null
  editingItem.value = item
  isCreating.value = false
  isEditing.value = true
}

const adjustStock = (item) => {
  router.push({ name: 'inventory-adjust', params: { id: item.id } })
}

const clearSelection = () => {
  selectedItem.value = null
  editingItem.value = null
  isCreating.value = false
  isEditing.value = false
}

const handleItemSaved = (itemData) => {
  toast.add({ 
    severity: 'success', 
    summary: 'Success', 
    detail: `Item ${isEditing.value ? 'updated' : 'created'} successfully` 
  })
  clearSelection()
}

const handleAdjustmentSaved = () => {
  showAdjustmentForm.value = false
  toast.add({ severity: 'success', summary: 'Success', detail: 'Stock adjustment saved successfully' })
}

const handlePurchaseOrderSaved = () => {
  showPurchaseOrderForm.value = false
  toast.add({ severity: 'success', summary: 'Success', detail: 'Purchase order saved successfully' })
}

const handleCycleCountSaved = () => {
  showCycleCountForm.value = false
  toast.add({ severity: 'success', summary: 'Success', detail: 'Cycle count saved successfully' })
}

// Helper methods
const getStatusSeverity = (status) => {
  const severities = {
    active: 'success',
    inactive: 'warning',
    discontinued: 'danger'
  }
  return severities[status] || 'info'
}

const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1)
}
</script>

<style scoped>
.inventory-management {
  padding: 1.5rem;
}

.field {
  margin-bottom: 1rem;
}

:deep(.p-tabview-nav) {
  background: var(--surface-50);
  border-bottom: 1px solid var(--surface-200);
}

:deep(.p-tabview-panels) {
  padding: 1.5rem 0;
}

:deep(.p-card-title) {
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--surface-200);
}
</style>