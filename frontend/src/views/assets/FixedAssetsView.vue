<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Fixed Assets Management</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Total Assets</v-card-title>
          <v-card-text>
            <div class="text-h3 text-primary">{{ assets.length }}</div>
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
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Depreciation</v-card-title>
          <v-card-text>
            <div class="text-h3 text-warning">{{ formatCurrency(totalDepreciation) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Net Value</v-card-title>
          <v-card-text>
            <div class="text-h3 text-info">{{ formatCurrency(netValue) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between">
            Fixed Assets
            <v-btn color="primary" @click="showAddDialog = true">
              <v-icon start>mdi-plus</v-icon>
              Add Asset
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :items="assets"
              :headers="headers"
              class="elevation-1"
            >
              <template #item.purchaseDate="{ item }">
                {{ formatDate(item.purchaseDate) }}
              </template>
              <template #item.cost="{ item }">
                {{ formatCurrency(item.cost) }}
              </template>
              <template #item.depreciation="{ item }">
                {{ formatCurrency(item.depreciation) }}
              </template>
              <template #item.netValue="{ item }">
                {{ formatCurrency(item.cost - item.depreciation) }}
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Add Asset Dialog -->
    <v-dialog v-model="showAddDialog" max-width="600px">
      <v-card>
        <v-card-title>Add Fixed Asset</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="addAsset">
            <v-text-field v-model="newAsset.name" label="Asset Name" required />
            <v-select v-model="newAsset.category" :items="categories" label="Category" required />
            <v-text-field v-model="newAsset.cost" label="Purchase Cost" type="number" prefix="$" required />
            <v-text-field v-model="newAsset.purchaseDate" label="Purchase Date" type="date" required />
            <v-text-field v-model="newAsset.usefulLife" label="Useful Life (years)" type="number" required />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showAddDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="addAsset">Add Asset</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'

const showAddDialog = ref(false)

const assets = ref([
  { id: 1, name: 'Office Building', category: 'Building', cost: 500000, depreciation: 50000, purchaseDate: '2020-01-01', usefulLife: 25 },
  { id: 2, name: 'Company Vehicle', category: 'Vehicle', cost: 35000, depreciation: 14000, purchaseDate: '2022-06-15', usefulLife: 5 },
  { id: 3, name: 'Computer Equipment', category: 'Equipment', cost: 15000, depreciation: 7500, purchaseDate: '2023-03-10', usefulLife: 3 }
])

const categories = ['Building', 'Equipment', 'Vehicle', 'Furniture', 'Technology']

const newAsset = ref({
  name: '',
  category: '',
  cost: '',
  purchaseDate: '',
  usefulLife: ''
})

const headers = [
  { title: 'Asset Name', key: 'name' },
  { title: 'Category', key: 'category' },
  { title: 'Purchase Date', key: 'purchaseDate' },
  { title: 'Cost', key: 'cost' },
  { title: 'Depreciation', key: 'depreciation' },
  { title: 'Net Value', key: 'netValue' }
]

const totalValue = computed(() => assets.value.reduce((sum, asset) => sum + asset.cost, 0))
const totalDepreciation = computed(() => assets.value.reduce((sum, asset) => sum + asset.depreciation, 0))
const netValue = computed(() => totalValue.value - totalDepreciation.value)

const addAsset = () => {
  assets.value.push({
    id: Date.now(),
    name: newAsset.value.name,
    category: newAsset.value.category,
    cost: parseFloat(newAsset.value.cost),
    depreciation: 0,
    purchaseDate: newAsset.value.purchaseDate,
    usefulLife: parseInt(newAsset.value.usefulLife)
  })
  newAsset.value = { name: '', category: '', cost: '', purchaseDate: '', usefulLife: '' }
  showAddDialog.value = false
}

const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
const formatDate = (date) => new Date(date).toLocaleDateString()
</script>