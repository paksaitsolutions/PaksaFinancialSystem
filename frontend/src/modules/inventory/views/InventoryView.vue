<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Inventory Management</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Total Items</v-card-title>
          <v-card-text>
            <div class="text-h3 text-primary">{{ totalItems }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Low Stock</v-card-title>
          <v-card-text>
            <div class="text-h3 text-warning">{{ lowStockItems }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Out of Stock</v-card-title>
          <v-card-text>
            <div class="text-h3 text-error">{{ outOfStockItems }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Total Value</v-card-title>
          <v-card-text>
            <div class="text-h3 text-success">{{ formatCurrency(totalValue) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between">
            Inventory Items
            <v-btn color="primary" @click="showAddDialog = true">
              <v-icon start>mdi-plus</v-icon>
              Add Item
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :items="inventory"
              :headers="headers"
              class="elevation-1"
            >
              <template #item.quantity="{ item }">
                <v-chip :color="getStockColor(item.quantity)" size="small">
                  {{ item.quantity }}
                </v-chip>
              </template>
              <template #item.value="{ item }">
                {{ formatCurrency(item.price * item.quantity) }}
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Add Item Dialog -->
    <v-dialog v-model="showAddDialog" max-width="500px">
      <v-card>
        <v-card-title>Add Inventory Item</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="addItem">
            <v-text-field v-model="newItem.name" label="Item Name" required />
            <v-text-field v-model="newItem.sku" label="SKU" required />
            <v-text-field v-model="newItem.quantity" label="Quantity" type="number" required />
            <v-text-field v-model="newItem.price" label="Unit Price" type="number" prefix="$" required />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showAddDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="addItem">Add Item</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'

const showAddDialog = ref(false)

const inventory = ref([
  { id: 1, name: 'Widget A', sku: 'WA001', quantity: 100, price: 25.00 },
  { id: 2, name: 'Widget B', sku: 'WB001', quantity: 5, price: 50.00 },
  { id: 3, name: 'Widget C', sku: 'WC001', quantity: 0, price: 75.00 }
])

const newItem = ref({
  name: '',
  sku: '',
  quantity: '',
  price: ''
})

const headers = [
  { title: 'Name', key: 'name' },
  { title: 'SKU', key: 'sku' },
  { title: 'Quantity', key: 'quantity' },
  { title: 'Unit Price', key: 'price' },
  { title: 'Total Value', key: 'value' }
]

const totalItems = computed(() => inventory.value.length)
const lowStockItems = computed(() => inventory.value.filter(item => item.quantity > 0 && item.quantity <= 10).length)
const outOfStockItems = computed(() => inventory.value.filter(item => item.quantity === 0).length)
const totalValue = computed(() => inventory.value.reduce((sum, item) => sum + (item.price * item.quantity), 0))

const getStockColor = (quantity) => {
  if (quantity === 0) return 'error'
  if (quantity <= 10) return 'warning'
  return 'success'
}

const addItem = () => {
  inventory.value.push({
    id: Date.now(),
    name: newItem.value.name,
    sku: newItem.value.sku,
    quantity: parseInt(newItem.value.quantity),
    price: parseFloat(newItem.value.price)
  })
  newItem.value = { name: '', sku: '', quantity: '', price: '' }
  showAddDialog.value = false
}

const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
</script>