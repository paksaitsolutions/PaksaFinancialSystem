<template>
  <div class="transaction-history">
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <div>
            <h2 class="m-0">Transaction History</h2>
            <p class="text-600 mt-1 mb-0">Track all inventory movements and changes</p>
          </div>
          <Button icon="pi pi-download" label="Export" severity="secondary" @click="exportTransactions" />
        </div>
      </template>
      
      <template #content>
        <!-- Filters -->
        <div class="grid mb-4">
          <div class="col-12 md:col-3">
            <div class="field">
              <label class="font-semibold">Item</label>
              <Dropdown
                v-model="filters.item_id"
                :options="items"
                optionLabel="name"
                optionValue="id"
                placeholder="Filter by item"
                class="w-full"
                showClear
                @change="fetchTransactions"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-3">
            <div class="field">
              <label class="font-semibold">Location</label>
              <Dropdown
                v-model="filters.location_id"
                :options="locations"
                optionLabel="name"
                optionValue="id"
                placeholder="Filter by location"
                class="w-full"
                showClear
                @change="fetchTransactions"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-3">
            <div class="field">
              <label class="font-semibold">Transaction Type</label>
              <Dropdown
                v-model="filters.transaction_type"
                :options="transactionTypes"
                optionLabel="label"
                optionValue="value"
                placeholder="Filter by type"
                class="w-full"
                showClear
                @change="fetchTransactions"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-3">
            <div class="field">
              <label class="font-semibold">Actions</label>
              <div class="flex gap-2">
                <Button icon="pi pi-filter-slash" label="Clear" severity="secondary" outlined @click="clearFilters" />
                <Button icon="pi pi-refresh" severity="secondary" outlined @click="fetchTransactions" :loading="loading" />
              </div>
            </div>
          </div>
        </div>
        
        <div class="grid mb-4">
          <div class="col-12 md:col-4">
            <div class="field">
              <label class="font-semibold">From Date</label>
              <Calendar
                v-model="filters.from_date"
                placeholder="Select from date"
                class="w-full"
                showIcon
                @date-select="fetchTransactions"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-4">
            <div class="field">
              <label class="font-semibold">To Date</label>
              <Calendar
                v-model="filters.to_date"
                placeholder="Select to date"
                class="w-full"
                showIcon
                @date-select="fetchTransactions"
              />
            </div>
          </div>
        </div>
        
        <!-- Data table -->
        <DataTable
          :value="transactions"
          :loading="loading"
          :paginator="true"
          :rows="pagination.itemsPerPage"
          :totalRecords="pagination.totalItems"
          :lazy="true"
          :rowsPerPageOptions="[10, 20, 50]"
          responsiveLayout="scroll"
          class="p-datatable-sm"
          @page="onPage"
          @sort="onSort"
        >
          <Column field="transaction_date" header="Date" sortable>
            <template #body="{ data }">
              {{ formatDate(data.transaction_date) }}
            </template>
          </Column>
          
          <Column field="transaction_type" header="Type" sortable>
            <template #body="{ data }">
              <Tag :value="formatTransactionType(data.transaction_type)" :severity="getTransactionSeverity(data.transaction_type)" />
            </template>
          </Column>
          
          <Column field="item_name" header="Item" />
          <Column field="location_name" header="Location" />
          
          <Column field="quantity" header="Quantity" sortable>
            <template #body="{ data }">
              <span :class="getQuantityClass(data.quantity)">
                {{ formatQuantity(data.quantity) }}
              </span>
            </template>
          </Column>
          
          <Column field="unit_cost" header="Unit Cost" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.unit_cost) }}
            </template>
          </Column>
          
          <Column field="total_cost" header="Total Cost" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.total_cost) }}
            </template>
          </Column>
          
          <Column field="quantity_before" header="Before">
            <template #body="{ data }">
              {{ formatQuantity(data.quantity_before) }}
            </template>
          </Column>
          
          <Column field="quantity_after" header="After">
            <template #body="{ data }">
              {{ formatQuantity(data.quantity_after) }}
            </template>
          </Column>
          
          <Column field="reference" header="Reference" />
          
          <Column header="Actions" :exportable="false">
            <template #body="{ data }">
              <Button icon="pi pi-eye" size="small" text @click="viewTransaction(data)" v-tooltip="'View Details'" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
    
    <!-- Transaction Detail Dialog -->
    <Dialog v-model:visible="detailDialog.show" modal header="Transaction Details" :style="{ width: '600px' }">
      <div v-if="detailDialog.transaction">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label class="font-semibold text-900">Transaction Type</label>
              <div class="mt-1">
                <Tag
                  :value="formatTransactionType(detailDialog.transaction.transaction_type)"
                  :severity="getTransactionSeverity(detailDialog.transaction.transaction_type)"
                />
              </div>
            </div>
            
            <div class="field">
              <label class="font-semibold text-900">Date</label>
              <p class="mt-1 mb-0">{{ formatDate(detailDialog.transaction.transaction_date) }}</p>
            </div>
            
            <div class="field">
              <label class="font-semibold text-900">Reference</label>
              <p class="mt-1 mb-0">{{ detailDialog.transaction.reference || 'N/A' }}</p>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label class="font-semibold text-900">Item</label>
              <p class="mt-1 mb-0">{{ detailDialog.transaction.item_name }} ({{ detailDialog.transaction.item_sku }})</p>
            </div>
            
            <div class="field">
              <label class="font-semibold text-900">Location</label>
              <p class="mt-1 mb-0">{{ detailDialog.transaction.location_name }}</p>
            </div>
          </div>
        </div>
        
        <Divider />
        
        <div class="grid">
          <div class="col-12 md:col-4">
            <div class="text-center p-3 border-round bg-primary-50">
              <div class="text-2xl font-bold text-primary">{{ formatQuantity(detailDialog.transaction.quantity) }}</div>
              <div class="text-sm text-600">Quantity</div>
            </div>
          </div>
          
          <div class="col-12 md:col-4">
            <div class="text-center p-3 border-round bg-green-50">
              <div class="text-2xl font-bold text-green-600">{{ formatCurrency(detailDialog.transaction.unit_cost) }}</div>
              <div class="text-sm text-600">Unit Cost</div>
            </div>
          </div>
          
          <div class="col-12 md:col-4">
            <div class="text-center p-3 border-round bg-orange-50">
              <div class="text-2xl font-bold text-orange-600">{{ formatCurrency(detailDialog.transaction.total_cost) }}</div>
              <div class="text-sm text-600">Total Cost</div>
            </div>
          </div>
        </div>
        
        <Divider />
        
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="text-center p-3 border-round surface-100">
              <div class="text-xl font-bold text-900">{{ formatQuantity(detailDialog.transaction.quantity_before) }}</div>
              <div class="text-sm text-600">Quantity Before</div>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="text-center p-3 border-round surface-100">
              <div class="text-xl font-bold text-900">{{ formatQuantity(detailDialog.transaction.quantity_after) }}</div>
              <div class="text-sm text-600">Quantity After</div>
            </div>
          </div>
        </div>
        
        <div v-if="detailDialog.transaction.notes" class="mt-4">
          <div class="field">
            <label class="font-semibold text-900">Notes</label>
            <div class="mt-2 p-3 bg-surface-100 border-round">
              {{ detailDialog.transaction.notes }}
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Close" @click="detailDialog.show = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { formatCurrency, formatDate } from '@/utils/formatters'
import { apiClient } from '@/utils/apiClient'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import Calendar from 'primevue/calendar'
import Dialog from 'primevue/dialog'
import Tag from 'primevue/tag'
import Divider from 'primevue/divider'

// Composables
const toast = useToast()

// Data
const transactions = ref([
  {
    id: 1,
    transaction_date: new Date('2024-01-15'),
    transaction_type: 'receipt',
    item_name: 'Widget Pro Max',
    item_sku: 'WDG-001',
    location_name: 'Main Warehouse',
    quantity: 50,
    unit_cost: 25.99,
    total_cost: 1299.50,
    quantity_before: 100,
    quantity_after: 150,
    reference: 'PO-2024-001',
    notes: 'Received from supplier ABC'
  },
  {
    id: 2,
    transaction_date: new Date('2024-01-14'),
    transaction_type: 'issue',
    item_name: 'Component X',
    item_sku: 'CMP-002',
    location_name: 'Production Floor',
    quantity: -25,
    unit_cost: 45.50,
    total_cost: -1137.50,
    quantity_before: 75,
    quantity_after: 50,
    reference: 'WO-2024-005',
    notes: 'Issued for production order'
  }
])

const items = ref([
  { id: 1, name: 'Widget Pro Max' },
  { id: 2, name: 'Component X' }
])

const locations = ref([
  { id: 1, name: 'Main Warehouse' },
  { id: 2, name: 'Production Floor' }
])

const loading = ref(false)

// Pagination
const pagination = reactive({
  page: 1,
  itemsPerPage: 20,
  totalItems: 0,
  sortBy: 'transaction_date',
  sortDesc: true
})

// Filters
const filters = reactive({
  item_id: null,
  location_id: null,
  transaction_type: null,
  from_date: null,
  to_date: null
})

// Dialog
const detailDialog = reactive({
  show: false,
  transaction: null
})

// Transaction types
const transactionTypes = [
  { label: 'Receipt', value: 'receipt' },
  { label: 'Issue', value: 'issue' },
  { label: 'Adjustment', value: 'adjustment' },
  { label: 'Transfer', value: 'transfer' }
]

// Methods
const fetchTransactions = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.itemsPerPage,
      sort_by: pagination.sortBy,
      sort_order: pagination.sortDesc ? 'desc' : 'asc'
    }
    
    // Add filters
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== '') {
        params[key] = filters[key]
      }
    })
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500))
    pagination.totalItems = 2
    // const response = await apiClient.get('/api/v1/inventory/transactions', { params })
    // transactions.value = response.data
    // pagination.totalItems = response.meta.pagination.total
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load transactions' })
    console.error('Error fetching transactions:', error)
  } finally {
    loading.value = false
  }
}

const onPage = (event) => {
  pagination.page = event.page + 1
  pagination.itemsPerPage = event.rows
  fetchTransactions()
}

const onSort = (event) => {
  pagination.sortBy = event.sortField
  pagination.sortDesc = event.sortOrder === -1
  fetchTransactions()
}

const clearFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = null
  })
  fetchTransactions()
}

const viewTransaction = (transaction) => {
  detailDialog.transaction = transaction
  detailDialog.show = true
}

const exportTransactions = () => {
  toast.add({ severity: 'info', summary: 'Export', detail: 'Export functionality coming soon' })
}

// Helper methods
const formatQuantity = (quantity) => {
  return Number(quantity || 0).toLocaleString()
}

const formatTransactionType = (type) => {
  const types = {
    receipt: 'Receipt',
    issue: 'Issue',
    adjustment: 'Adjustment',
    transfer: 'Transfer'
  }
  return types[type] || type
}

const getTransactionSeverity = (type) => {
  const severities = {
    receipt: 'success',
    issue: 'danger',
    adjustment: 'warning',
    transfer: 'info'
  }
  return severities[type] || 'info'
}

const getQuantityClass = (quantity) => {
  const num = Number(quantity || 0)
  if (num > 0) return 'text-green-600 font-semibold'
  if (num < 0) return 'text-red-600 font-semibold'
  return ''
}

// Lifecycle hooks
onMounted(() => {
  fetchTransactions()
})
</script>

<style scoped>
.transaction-history {
  padding: 1.5rem;
}

.field {
  margin-bottom: 1rem;
}
</style>