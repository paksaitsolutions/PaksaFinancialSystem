<template>
  <div class="inventory-list">
    <Card>
      <template #title>
        <div class="header-content">
          <div class="header-text">
            <h2 class="m-0">Inventory Items</h2>
            <p class="text-600 mt-1 mb-0">Manage your inventory items and stock levels</p>
          </div>
          <div class="header-actions">
            <Button icon="pi pi-qrcode" label="Scan" severity="info" @click="showBarcodeScanner = true" />
            <Button icon="pi pi-upload" label="Import" severity="secondary" @click="showImportDialog = true" />
            <Button icon="pi pi-plus" label="Add Item" @click="openCreateDialog" />
          </div>
        </div>
      </template>
      
      <template #content>
        <!-- Filters -->
        <div class="grid mb-4">
          <div class="col-12 md:col-3">
            <span class="p-input-icon-left w-full">
              <i class="pi pi-search" />
              <InputText v-model="filters.name" placeholder="Search by name" class="w-full" @input="debouncedFetchItems" />
            </span>
          </div>
          <div class="col-12 md:col-3">
            <span class="p-input-icon-left w-full">
              <i class="pi pi-barcode" />
              <InputText v-model="filters.sku" placeholder="Search by SKU" class="w-full" @input="debouncedFetchItems" />
            </span>
          </div>
          <div class="col-12 md:col-2">
            <Dropdown v-model="filters.status" :options="statusOptions" optionLabel="label" optionValue="value" placeholder="Status" class="w-full" showClear @change="fetchItems" />
          </div>
          <div class="col-12 md:col-2">
            <Dropdown v-model="filters.category" :options="categoryOptions" optionLabel="label" optionValue="value" placeholder="Category" class="w-full" showClear @change="fetchItems" />
          </div>
          <div class="col-12 md:col-2">
            <div class="flex flex-wrap gap-2">
              <Button icon="pi pi-filter-slash" label="Clear" severity="secondary" outlined @click="clearFilters" class="flex-shrink-0" />
              <Button icon="pi pi-download" severity="help" outlined @click="exportItems" class="flex-shrink-0" />
            </div>
          </div>
        </div>
        
        <!-- Data Table -->
        <DataTable
          v-model:selection="selectedItems"
          :value="items"
          :loading="loading"
          :paginator="true"
          :rows="pagination.itemsPerPage"
          :totalRecords="pagination.totalItems"
          :lazy="true"
          :rowsPerPageOptions="[10, 25, 50, 100]"
          dataKey="id"
          selectionMode="multiple"
          responsiveLayout="scroll"
          class="p-datatable-sm"
          :scrollable="true"
          scrollHeight="400px"
          @page="onPage"
          @sort="onSort"
        >
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <div class="flex align-items-center gap-2">
                <span class="text-900 font-semibold">{{ pagination.totalItems }} items total</span>
                <Button v-if="selectedItems.length > 0" icon="pi pi-trash" :label="`Delete ${selectedItems.length} items`" severity="danger" size="small" @click="confirmBulkDelete" />
              </div>
              <div class="flex gap-2">
                <Button icon="pi pi-refresh" size="small" @click="fetchItems" />
                <MultiSelect v-model="visibleColumns" :options="columns" optionLabel="header" placeholder="Columns" class="w-12rem" />
              </div>
            </div>
          </template>
          
          <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
          
          <Column v-for="col in visibleColumns" :key="col.field" :field="col.field" :header="col.header" :sortable="col.sortable">
            <template #body="{ data }" v-if="col.field === 'status'">
              <Tag :value="formatStatus(data.status)" :severity="getStatusSeverity(data.status)" />
            </template>
            
            <template #body="{ data }" v-else-if="col.field === 'quantity_on_hand'">
              <div class="flex align-items-center gap-2">
                <span>{{ formatQuantity(data.quantity_on_hand) }}</span>
                <Tag v-if="data.quantity_on_hand <= data.reorder_point" value="Low" severity="warning" />
                <Tag v-if="data.quantity_on_hand === 0" value="Out" severity="danger" />
              </div>
            </template>
            
            <template #body="{ data }" v-else-if="col.field === 'unit_cost'">
              {{ formatCurrency(data.unit_cost) }}
            </template>
            
            <template #body="{ data }" v-else-if="col.field === 'total_value'">
              {{ formatCurrency(data.unit_cost * data.quantity_on_hand) }}
            </template>
            
            <template #body="{ data }" v-else-if="col.field === 'actions'">
              <div class="flex gap-1">
                <Button icon="pi pi-eye" size="small" text @click="viewItem(data)" v-tooltip="'View Details'" />
                <Button icon="pi pi-pencil" size="small" text severity="warning" @click="editItem(data)" v-tooltip="'Edit Item'" />
                <Button icon="pi pi-plus" size="small" text severity="success" @click="adjustStock(data)" v-tooltip="'Adjust Stock'" />
                <Button icon="pi pi-trash" size="small" text severity="danger" @click="confirmDelete(data)" v-tooltip="'Delete Item'" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
    
    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:visible="deleteDialog.show" modal header="Delete Inventory Item" :style="{ width: '450px' }">
      <div class="flex align-items-center gap-3 mb-3">
        <i class="pi pi-exclamation-triangle text-red-500" style="font-size: 2rem"></i>
        <span>Are you sure you want to delete item <strong>"{{ deleteDialog.item?.name }}"</strong>?</span>
      </div>
      <p class="text-600">This action cannot be undone.</p>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="deleteDialog.show = false" />
        <Button label="Delete" severity="danger" @click="deleteItem" />
      </template>
    </Dialog>
    
    <!-- Bulk Delete Confirmation Dialog -->
    <Dialog v-model:visible="bulkDeleteDialog.show" modal header="Delete Multiple Items" :style="{ width: '450px' }">
      <div class="flex align-items-center gap-3 mb-3">
        <i class="pi pi-exclamation-triangle text-red-500" style="font-size: 2rem"></i>
        <span>Are you sure you want to delete <strong>{{ selectedItems.length }}</strong> selected items?</span>
      </div>
      <p class="text-600">This action cannot be undone.</p>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="bulkDeleteDialog.show = false" />
        <Button label="Delete All" severity="danger" @click="bulkDeleteItems" />
      </template>
    </Dialog>
    
    <!-- Import Dialog -->
    <Dialog v-model:visible="showImportDialog" modal header="Import Inventory Items" :style="{ width: '600px' }">
      <div class="mb-4">
        <p class="text-600 mb-3">Upload a CSV file to import inventory items. Download the template to see the required format.</p>
        <div class="flex gap-2 mb-3">
          <Button label="Download Template" icon="pi pi-download" severity="secondary" outlined @click="downloadTemplate" />
        </div>
        <FileUpload mode="basic" name="file" accept=".csv" :maxFileSize="1000000" @select="onFileSelect" chooseLabel="Choose CSV File" />
      </div>
      
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showImportDialog = false" />
        <Button label="Import" :disabled="!selectedFile" @click="importItems" />
      </template>
    </Dialog>
    
    <!-- Barcode Scanner Dialog -->
    <Dialog v-model:visible="showBarcodeScanner" modal header="Barcode Scanner" :style="{ width: '700px' }">
      <BarcodeScanner @close="showBarcodeScanner = false" @item-selected="handleItemSelected" />
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { debounce } from '@/utils/debounce'
import { formatCurrency } from '@/utils/formatters'
import { inventoryService, type InventoryItem } from '@/services/inventoryService'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import Dialog from 'primevue/dialog'
import Tag from 'primevue/tag'
import FileUpload from 'primevue/fileupload'
import BarcodeScanner from './BarcodeScanner.vue'

// Emits
const emit = defineEmits(['view', 'create'])

// Composables
const router = useRouter()
const toast = useToast()

// Data
const items = ref([])
const selectedItems = ref([])
const loading = ref(false)
const showBarcodeScanner = ref(false)
const showImportDialog = ref(false)
const selectedFile = ref(null)

// Pagination
const pagination = reactive({
  page: 1,
  itemsPerPage: 10,
  totalItems: 0,
  sortBy: 'name',
  sortDesc: false
})

// Filters
const filters = reactive({
  name: '',
  sku: '',
  status: null,
  category: null
})

// Dialogs
const deleteDialog = reactive({
  show: false,
  item: null
})

const bulkDeleteDialog = reactive({
  show: false
})

// Table columns
const columns = [
  { field: 'sku', header: 'SKU', sortable: true },
  { field: 'barcode', header: 'Barcode', sortable: true },
  { field: 'name', header: 'Name', sortable: true },
  { field: 'status', header: 'Status', sortable: true },
  { field: 'quantity_on_hand', header: 'On Hand', sortable: true },
  { field: 'unit_cost', header: 'Unit Cost', sortable: true },
  { field: 'total_value', header: 'Total Value', sortable: false },
  { field: 'unit_of_measure', header: 'UOM', sortable: false },
  { field: 'actions', header: 'Actions', sortable: false }
]

const visibleColumns = ref([...columns])

// Options
const statusOptions = [
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'Discontinued', value: 'discontinued' }
]

const categoryOptions = ref([])

const loadCategories = async () => {
  try {
    const categories = await inventoryService.getCategories()
    categoryOptions.value = categories.map(cat => ({
      label: cat.name,
      value: cat.id
    }))
  } catch (error) {
    console.error('Error loading categories:', error)
  }
}

// Methods
const fetchItems = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.itemsPerPage,
      limit: pagination.itemsPerPage
    }
    
    // Add filters
    if (filters.name) params.search = filters.name
    if (filters.sku) params.search = filters.sku
    if (filters.status) params.status = filters.status
    if (filters.category) params.category_id = filters.category
    
    const response = await inventoryService.getItems(params)
    items.value = response.map((item: InventoryItem) => ({
      id: item.id,
      sku: item.item_code,
      barcode: item.barcode,
      name: item.item_name,
      status: item.is_active ? 'active' : 'inactive',
      quantity_on_hand: item.quantity_on_hand || 0,
      unit_cost: item.cost_price || 0,
      reorder_point: item.reorder_level || 0,
      unit_of_measure: item.unit_of_measure || 'EA'
    }))
    pagination.totalItems = response.length
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load inventory items' })
    console.error('Error fetching inventory items:', error)
    // Fallback to empty array
    items.value = []
  } finally {
    loading.value = false
  }
}

const debouncedFetchItems = debounce(fetchItems, 300)

const onPage = (event) => {
  pagination.page = event.page + 1
  pagination.itemsPerPage = event.rows
  fetchItems()
}

const onSort = (event) => {
  pagination.sortBy = event.sortField
  pagination.sortDesc = event.sortOrder === -1
  fetchItems()
}

const clearFilters = () => {
  filters.name = ''
  filters.sku = ''
  filters.status = null
  filters.category = null
  fetchItems()
}

const openCreateDialog = () => {
  emit('create')
}

const viewItem = (item) => {
  emit('view', item)
}

const editItem = (item) => {
  router.push({ name: 'inventory-edit', params: { id: item.id } })
}

const adjustStock = (item) => {
  router.push({ name: 'inventory-adjust', params: { id: item.id } })
}

const confirmDelete = (item) => {
  deleteDialog.item = item
  deleteDialog.show = true
}

const confirmBulkDelete = () => {
  bulkDeleteDialog.show = true
}

const deleteItem = async () => {
  if (!deleteDialog.item) return
  
  try {
    await inventoryService.deleteItem(deleteDialog.item.id)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Inventory item deleted successfully' })
    fetchItems()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete inventory item' })
    console.error('Error deleting inventory item:', error)
  } finally {
    deleteDialog.show = false
    deleteDialog.item = null
  }
}

const bulkDeleteItems = async () => {
  try {
    await Promise.all(selectedItems.value.map(item => inventoryService.deleteItem(item.id)))
    toast.add({ severity: 'success', summary: 'Success', detail: `${selectedItems.value.length} items deleted successfully` })
    selectedItems.value = []
    fetchItems()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete items' })
    console.error('Error deleting items:', error)
  } finally {
    bulkDeleteDialog.show = false
  }
}

const exportItems = () => {
  // Implement export functionality
  toast.add({ severity: 'info', summary: 'Export', detail: 'Export functionality will be implemented' })
}

const downloadTemplate = () => {
  // Implement template download
  toast.add({ severity: 'info', summary: 'Download', detail: 'Template download will be implemented' })
}

const onFileSelect = (event) => {
  selectedFile.value = event.files[0]
}

const importItems = () => {
  if (!selectedFile.value) return
  
  // Implement import functionality
  toast.add({ severity: 'success', summary: 'Import', detail: 'Items imported successfully' })
  showImportDialog.value = false
  selectedFile.value = null
  fetchItems()
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

const formatQuantity = (quantity) => {
  return Number(quantity).toLocaleString()
}

const handleItemSelected = (item) => {
  toast.add({ severity: 'success', summary: 'Item Found', detail: `Item found: ${item.name}` })
  viewItem(item)
}

// Lifecycle hooks
onMounted(() => {
  fetchItems()
  loadCategories()
})
</script>

<style scoped>
.inventory-list {
  padding: 1.5rem;
}

:deep(.p-datatable-header) {
  background: var(--surface-50);
  border-bottom: 1px solid var(--surface-200);
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.75rem;
}

:deep(.p-tag) {
  font-size: 0.75rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

@media screen and (max-width: 960px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>