<template>
  <div class="fixed-assets">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Fixed Assets</h1>
        <p class="text-color-secondary">Manage your fixed assets and depreciation</p>
      </div>
      <Button label="Add Asset" icon="pi pi-plus" @click="openNew" />
    </div>

    <div class="grid">
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-building text-4xl text-blue-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.totalAssets }}</div>
              <div class="text-color-secondary">Total Assets</div>
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
              <i class="pi pi-calculator text-4xl text-orange-500 mb-3"></i>
              <div class="text-2xl font-bold">${{ stats.monthlyDepreciation }}</div>
              <div class="text-color-secondary">Monthly Depreciation</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-wrench text-4xl text-purple-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.maintenanceDue }}</div>
              <div class="text-color-secondary">Maintenance Due</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Card>
      <template #title>Fixed Assets</template>
      <template #content>
        <DataTable :value="assets" :loading="loading" paginator :rows="10">
          <Column field="assetId" header="Asset ID" sortable />
          <Column field="name" header="Asset Name" sortable />
          <Column field="category" header="Category" sortable />
          <Column field="purchaseDate" header="Purchase Date" sortable />
          <Column field="purchasePrice" header="Purchase Price" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.purchasePrice) }}
            </template>
          </Column>
          <Column field="currentValue" header="Current Value" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.currentValue) }}
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning mr-2" @click="editAsset(data)" />
              <Button icon="pi pi-eye" class="p-button-text mr-2" @click="viewAsset(data)" />
              <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="confirmDeleteAsset(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="assetDialog" header="Fixed Asset" :modal="true" :style="{width: '600px'}">
      <div class="field">
        <label>Asset ID</label>
        <InputText v-model="asset.assetId" class="w-full" :class="{'p-invalid': submitted && !asset.assetId}" />
        <small class="p-error" v-if="submitted && !asset.assetId">Asset ID is required.</small>
      </div>
      <div class="field">
        <label>Asset Name</label>
        <InputText v-model="asset.name" class="w-full" :class="{'p-invalid': submitted && !asset.name}" />
        <small class="p-error" v-if="submitted && !asset.name">Name is required.</small>
      </div>
      <div class="field">
        <label>Category</label>
        <Dropdown v-model="asset.category" :options="categories" placeholder="Select Category" class="w-full" />
      </div>
      <div class="grid">
        <div class="col-6">
          <div class="field">
            <label>Purchase Date</label>
            <Calendar v-model="asset.purchaseDate" class="w-full" />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label>Purchase Price</label>
            <InputNumber v-model="asset.purchasePrice" mode="currency" currency="USD" class="w-full" :min="0" />
          </div>
        </div>
      </div>
      <div class="field">
        <label>Current Value</label>
        <InputNumber v-model="asset.currentValue" mode="currency" currency="USD" class="w-full" :min="0" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="hideDialog" />
        <Button label="Save" @click="saveAsset" />
      </template>
    </Dialog>

    <Dialog v-model:visible="deleteAssetDialog" header="Confirm" :modal="true" :style="{width: '450px'}">
      <div class="flex align-items-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="asset">Are you sure you want to delete <b>{{ asset.name }}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" class="p-button-text" @click="deleteAssetDialog = false" />
        <Button label="Yes" class="p-button-danger" @click="deleteAsset" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const loading = ref(false)

const stats = ref({
  totalAssets: 156,
  totalValue: '2,456,789',
  monthlyDepreciation: '12,450',
  maintenanceDue: 8
})

const assets = ref([
  { assetId: 'FA001', name: 'Office Building', category: 'Real Estate', purchaseDate: '2020-01-15', purchasePrice: 500000, currentValue: 475000, status: 'active' },
  { assetId: 'FA002', name: 'Company Vehicle', category: 'Vehicle', purchaseDate: '2022-03-10', purchasePrice: 35000, currentValue: 28000, status: 'active' },
  { assetId: 'FA003', name: 'Manufacturing Equipment', category: 'Equipment', purchaseDate: '2021-06-20', purchasePrice: 125000, currentValue: 95000, status: 'active' },
  { assetId: 'FA004', name: 'Computer Server', category: 'IT Equipment', purchaseDate: '2023-01-05', purchasePrice: 15000, currentValue: 13500, status: 'active' },
  { assetId: 'FA005', name: 'Furniture Set', category: 'Furniture', purchaseDate: '2022-08-15', purchasePrice: 8500, currentValue: 6800, status: 'active' }
])

const assetDialog = ref(false)
const deleteAssetDialog = ref(false)
const submitted = ref(false)

const asset = ref({
  assetId: '',
  name: '',
  category: '',
  purchaseDate: new Date(),
  purchasePrice: 0,
  currentValue: 0,
  status: 'active'
})

const categories = ref(['Real Estate', 'Vehicle', 'Equipment', 'IT Equipment', 'Furniture'])

const openNew = () => {
  asset.value = {
    assetId: `FA${String(Date.now()).slice(-3)}`,
    name: '',
    category: '',
    purchaseDate: new Date(),
    purchasePrice: 0,
    currentValue: 0,
    status: 'active'
  }
  submitted.value = false
  assetDialog.value = true
}

const editAsset = (assetData: any) => {
  asset.value = { ...assetData, purchaseDate: new Date(assetData.purchaseDate) }
  assetDialog.value = true
}

const viewAsset = (assetData: any) => {
  asset.value = { ...assetData, purchaseDate: new Date(assetData.purchaseDate) }
  assetDialog.value = true
}

const hideDialog = () => {
  assetDialog.value = false
  submitted.value = false
}

const saveAsset = () => {
  submitted.value = true
  if (asset.value.name && asset.value.category) {
    const existingIndex = assets.value.findIndex(a => a.assetId === asset.value.assetId)
    if (existingIndex !== -1) {
      assets.value[existingIndex] = { ...asset.value }
      toast.add({ severity: 'success', summary: 'Success', detail: 'Asset updated', life: 3000 })
    } else {
      assets.value.push({ ...asset.value })
      toast.add({ severity: 'success', summary: 'Success', detail: 'Asset created', life: 3000 })
    }
    assetDialog.value = false
  }
}

const confirmDeleteAsset = (assetData: any) => {
  asset.value = { ...assetData }
  deleteAssetDialog.value = true
}

const deleteAsset = () => {
  assets.value = assets.value.filter(a => a.assetId !== asset.value.assetId)
  deleteAssetDialog.value = false
  toast.add({ severity: 'success', summary: 'Success', detail: 'Asset deleted', life: 3000 })
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'maintenance': return 'warning'
    case 'disposed': return 'danger'
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
.fixed-assets {
  padding: 0;
}

.metric-card {
  text-align: center;
}
</style>