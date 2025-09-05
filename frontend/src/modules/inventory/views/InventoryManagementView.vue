<template>
  <div class="inventory-management">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Inventory Management</h1>
        <p class="text-color-secondary">Track and manage your inventory items</p>
      </div>
      <Button label="Add Item" icon="pi pi-plus" @click="openNew" />
    </div>

    <div class="grid">
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-box text-4xl text-blue-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.totalItems }}</div>
              <div class="text-color-secondary">Total Items</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-exclamation-triangle text-4xl text-orange-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.lowStock }}</div>
              <div class="text-color-secondary">Low Stock Items</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-dollar text-4xl text-green-500 mb-3"></i>
              <div class="text-2xl font-bold">${{ stats.totalValue }}</div>
              <div class="text-color-secondary">Total Value</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-building text-4xl text-purple-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.warehouses }}</div>
              <div class="text-color-secondary">Warehouses</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Card>
      <template #title>Inventory Items</template>
      <template #content>
        <DataTable :value="inventoryItems" :loading="loading" paginator :rows="10">
          <Column field="sku" header="SKU" sortable />
          <Column field="name" header="Item Name" sortable />
          <Column field="category" header="Category" sortable />
          <Column field="quantity" header="Quantity" sortable />
          <Column field="unitPrice" header="Unit Price" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.unitPrice) }}
            </template>
          </Column>
          <Column field="totalValue" header="Total Value" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.quantity * data.unitPrice) }}
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning mr-2" @click="editItem(data)" />
              <Button icon="pi pi-eye" class="p-button-text mr-2" @click="viewItem(data)" />
              <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="confirmDeleteItem(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="itemDialog" header="Inventory Item" :modal="true" :style="{width: '600px'}">
      <div class="field">
        <label>SKU</label>
        <InputText v-model="item.sku" class="w-full" :class="{'p-invalid': submitted && !item.sku}" />
        <small class="p-error" v-if="submitted && !item.sku">SKU is required.</small>
      </div>
      <div class="field">
        <label>Item Name</label>
        <InputText v-model="item.name" class="w-full" :class="{'p-invalid': submitted && !item.name}" />
        <small class="p-error" v-if="submitted && !item.name">Name is required.</small>
      </div>
      <div class="field">
        <label>Category</label>
        <Dropdown v-model="item.category" :options="categories" placeholder="Select Category" class="w-full" />
      </div>
      <div class="grid">
        <div class="col-6">
          <div class="field">
            <label>Quantity</label>
            <InputNumber v-model="item.quantity" class="w-full" :min="0" />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label>Unit Price</label>
            <InputNumber v-model="item.unitPrice" mode="currency" currency="USD" class="w-full" :min="0" />
          </div>
        </div>
      </div>
      <div class="field">
        <label>Description</label>
        <Textarea v-model="item.description" rows="3" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="hideDialog" />
        <Button label="Save" @click="saveItem" />
      </template>
    </Dialog>

    <Dialog v-model:visible="deleteItemDialog" header="Confirm" :modal="true" :style="{width: '450px'}">
      <div class="flex align-items-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="item">Are you sure you want to delete <b>{{ item.name }}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" class="p-button-text" @click="deleteItemDialog = false" />
        <Button label="Yes" class="p-button-danger" @click="deleteItem" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

interface InventoryItem {
  id?: number
  sku: string
  name: string
  category: string
  quantity: number
  unitPrice: number
  status: string
  description?: string
}

const toast = useToast()
const loading = ref(false)
const itemDialog = ref(false)
const deleteItemDialog = ref(false)
const submitted = ref(false)

const stats = ref({
  totalItems: 1247,
  lowStock: 23,
  totalValue: '456,789',
  warehouses: 3
})

const inventoryItems = ref<InventoryItem[]>([
  { id: 1, sku: 'ITM001', name: 'Office Chair', category: 'Furniture', quantity: 25, unitPrice: 150, status: 'in_stock' },
  { id: 2, sku: 'ITM002', name: 'Laptop Computer', category: 'Electronics', quantity: 8, unitPrice: 1200, status: 'low_stock' },
  { id: 3, sku: 'ITM003', name: 'Printer Paper', category: 'Supplies', quantity: 150, unitPrice: 12, status: 'in_stock' },
  { id: 4, sku: 'ITM004', name: 'Desk Lamp', category: 'Furniture', quantity: 2, unitPrice: 45, status: 'low_stock' },
  { id: 5, sku: 'ITM005', name: 'Wireless Mouse', category: 'Electronics', quantity: 45, unitPrice: 25, status: 'in_stock' },
  { id: 6, sku: 'ITM006', name: 'Filing Cabinet', category: 'Furniture', quantity: 0, unitPrice: 200, status: 'out_of_stock' },
  { id: 7, sku: 'ITM007', name: 'Whiteboard', category: 'Supplies', quantity: 12, unitPrice: 85, status: 'in_stock' },
  { id: 8, sku: 'ITM008', name: 'Conference Phone', category: 'Electronics', quantity: 3, unitPrice: 350, status: 'low_stock' }
])

const item = ref<InventoryItem>({
  sku: '',
  name: '',
  category: '',
  quantity: 0,
  unitPrice: 0,
  status: 'in_stock'
})

const categories = ref(['Electronics', 'Furniture', 'Supplies', 'Equipment', 'Software'])

const openNew = () => {
  item.value = {
    sku: `ITM${String(Date.now()).slice(-3)}`,
    name: '',
    category: '',
    quantity: 0,
    unitPrice: 0,
    status: 'in_stock'
  }
  submitted.value = false
  itemDialog.value = true
}

const editItem = (itemData: InventoryItem) => {
  item.value = { ...itemData }
  itemDialog.value = true
}

const viewItem = (itemData: InventoryItem) => {
  item.value = { ...itemData }
  itemDialog.value = true
}

const hideDialog = () => {
  itemDialog.value = false
  submitted.value = false
}

const saveItem = () => {
  submitted.value = true
  if (item.value.sku && item.value.name) {
    if (item.value.id) {
      const index = inventoryItems.value.findIndex(i => i.id === item.value.id)
      if (index !== -1) {
        inventoryItems.value[index] = { ...item.value }
      }
      toast.add({ severity: 'success', summary: 'Success', detail: 'Item updated', life: 3000 })
    } else {
      inventoryItems.value.push({ ...item.value, id: Date.now() })
      toast.add({ severity: 'success', summary: 'Success', detail: 'Item created', life: 3000 })
    }
    itemDialog.value = false
  }
}

const confirmDeleteItem = (itemData: InventoryItem) => {
  item.value = { ...itemData }
  deleteItemDialog.value = true
}

const deleteItem = () => {
  inventoryItems.value = inventoryItems.value.filter(i => i.id !== item.value.id)
  deleteItemDialog.value = false
  toast.add({ severity: 'success', summary: 'Success', detail: 'Item deleted', life: 3000 })
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'in_stock': return 'success'
    case 'low_stock': return 'warning'
    case 'out_of_stock': return 'danger'
    default: return 'info'
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

onMounted(async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.inventory-management {
  padding: 0;
}

.metric-card {
  text-align: center;
}
</style>