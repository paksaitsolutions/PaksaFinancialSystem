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
              <div class="text-2xl font-bold">{{ stats.total_assets }}</div>
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
              <div class="text-2xl font-bold">{{ formatCurrency(stats.total_current_value) }}</div>
              <div class="text-color-secondary">Current Value</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-calculator text-4xl text-orange-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ formatCurrency(stats.monthly_depreciation) }}</div>
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
              <div class="text-2xl font-bold">{{ stats.maintenance_due }}</div>
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
          <Column field="asset_number" header="Asset ID" sortable />
          <Column field="asset_name" header="Asset Name" sortable />
          <Column field="asset_category" header="Category" sortable />
          <Column field="purchase_date" header="Purchase Date" sortable>
            <template #body="{ data }">
              {{ formatDate(data.purchase_date) }}
            </template>
          </Column>
          <Column field="purchase_cost" header="Purchase Price" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.purchase_cost) }}
            </template>
          </Column>
          <Column field="current_value" header="Current Value" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.current_value || 0) }}
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
        <label>Asset Number</label>
        <InputText v-model="asset.asset_number" class="w-full" :class="{'p-invalid': submitted && !asset.asset_number}" />
        <small class="p-error" v-if="submitted && !asset.asset_number">Asset number is required.</small>
      </div>
      <div class="field">
        <label>Asset Name</label>
        <InputText v-model="asset.asset_name" class="w-full" :class="{'p-invalid': submitted && !asset.asset_name}" />
        <small class="p-error" v-if="submitted && !asset.asset_name">Name is required.</small>
      </div>
      <div class="field">
        <label>Category</label>
        <Dropdown v-model="asset.asset_category" :options="categories" optionLabel="name" optionValue="value" placeholder="Select Category" class="w-full" />
      </div>
      <div class="grid">
        <div class="col-6">
          <div class="field">
            <label>Purchase Date</label>
            <InputText v-model="asset.purchase_date" type="date" class="w-full" />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label>Purchase Cost</label>
            <InputNumber v-model="asset.purchase_cost" mode="currency" currency="USD" class="w-full" :min="0" />
          </div>
        </div>
      </div>
      <div class="grid">
        <div class="col-6">
          <div class="field">
            <label>Useful Life (Years)</label>
            <InputNumber v-model="asset.useful_life_years" class="w-full" :min="1" />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label>Salvage Value</label>
            <InputNumber v-model="asset.salvage_value" mode="currency" currency="USD" class="w-full" :min="0" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="hideDialog" />
        <Button label="Save" @click="saveAsset" />
      </template>
    </Dialog>

    <Dialog v-model:visible="deleteAssetDialog" header="Confirm" :modal="true" :style="{width: '450px'}">
      <div class="flex align-items-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="asset">Are you sure you want to delete <b>{{ asset.asset_name }}</b>?</span>
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
import { fixedAssetsService, type FixedAsset, type AssetStats } from '@/services/fixedAssetsService'

const toast = useToast()
const loading = ref(false)

const stats = ref<AssetStats>({
  total_assets: 0,
  total_cost: 0,
  total_accumulated_depreciation: 0,
  total_current_value: 0,
  monthly_depreciation: 0,
  maintenance_due: 0
})

const assets = ref<FixedAsset[]>([])

const assetDialog = ref(false)
const deleteAssetDialog = ref(false)
const submitted = ref(false)

const asset = ref<Partial<FixedAsset>>({
  asset_number: '',
  asset_name: '',
  asset_category: '',
  purchase_date: '',
  purchase_cost: 0,
  status: 'active'
})

const categories = ref<{name: string, value: string}[]>([])

const loadCategories = async () => {
  try {
    categories.value = await fixedAssetsService.getCategories()
  } catch (error) {
    console.error('Error loading categories:', error)
    // Fallback categories
    categories.value = [
      { name: 'Real Estate', value: 'Real Estate' },
      { name: 'Vehicle', value: 'Vehicle' },
      { name: 'Equipment', value: 'Equipment' },
      { name: 'IT Equipment', value: 'IT Equipment' },
      { name: 'Furniture', value: 'Furniture' }
    ]
  }
}

const openNew = () => {
  asset.value = {
    asset_number: `FA${String(Date.now()).slice(-3)}`,
    asset_name: '',
    asset_category: '',
    purchase_date: new Date().toISOString().split('T')[0],
    purchase_cost: 0,
    status: 'active'
  }
  submitted.value = false
  assetDialog.value = true
}

const editAsset = (assetData: FixedAsset) => {
  asset.value = { ...assetData }
  assetDialog.value = true
}

const viewAsset = (assetData: FixedAsset) => {
  asset.value = { ...assetData }
  assetDialog.value = true
}

const hideDialog = () => {
  assetDialog.value = false
  submitted.value = false
}

const saveAsset = async () => {
  submitted.value = true
  if (asset.value.asset_name && asset.value.asset_category) {
    try {
      if (asset.value.id) {
        await fixedAssetsService.updateAsset(asset.value.id, asset.value)
        toast.add({ severity: 'success', summary: 'Success', detail: 'Asset updated', life: 3000 })
      } else {
        await fixedAssetsService.createAsset(asset.value)
        toast.add({ severity: 'success', summary: 'Success', detail: 'Asset created', life: 3000 })
      }
      assetDialog.value = false
      await loadAssets()
      await loadStats()
    } catch (error) {
      toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save asset', life: 3000 })
      console.error('Error saving asset:', error)
    }
  }
}

const confirmDeleteAsset = (assetData: FixedAsset) => {
  asset.value = { ...assetData }
  deleteAssetDialog.value = true
}

const deleteAsset = async () => {
  if (!asset.value.id) return
  
  try {
    await fixedAssetsService.deleteAsset(asset.value.id)
    deleteAssetDialog.value = false
    toast.add({ severity: 'success', summary: 'Success', detail: 'Asset deleted', life: 3000 })
    await loadAssets()
    await loadStats()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete asset', life: 3000 })
    console.error('Error deleting asset:', error)
  }
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

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const loadAssets = async () => {
  loading.value = true
  try {
    const response = await fixedAssetsService.getAssets()
    assets.value = response.assets || response
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load assets', life: 3000 })
    console.error('Error loading assets:', error)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    stats.value = await fixedAssetsService.getAssetStats()
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

onMounted(async () => {
  await Promise.all([
    loadAssets(),
    loadStats(),
    loadCategories()
  ])
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