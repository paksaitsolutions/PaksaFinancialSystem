<template>
  <div>
    <p>Asset Management Component Loaded</p>
    <Card>
      <template #header>
        <div class="flex justify-content-between align-items-center p-4">
          <h2 class="m-0">Fixed Assets Management</h2>
          <Button 
            label="New Asset" 
            icon="pi pi-plus" 
            @click="openAssetDialog"
          />
        </div>
      </template>
      
      <template #content>
        <DataTable
          :value="assets"
          :loading="loading"
          :paginator="true"
          :rows="10"
          responsiveLayout="scroll"
        >
          <Column field="asset_number" header="Asset Number">
            <template #body="{ data }">
              <a href="#" @click.prevent="openAssetDialog(data)" class="text-primary cursor-pointer">
                {{ data.asset_number }}
              </a>
            </template>
          </Column>
          
          <Column field="name" header="Name"></Column>
          <Column field="category" header="Category"></Column>
          
          <Column field="purchase_cost" header="Purchase Cost">
            <template #body="{ data }">
              {{ formatCurrency(data.purchase_cost) }}
            </template>
          </Column>
          
          <Column field="book_value" header="Book Value">
            <template #body="{ data }">
              {{ formatCurrency(data.purchase_cost - data.accumulated_depreciation) }}
            </template>
          </Column>
          
          <Column field="status" header="Status">
            <template #body="{ data }">
              <Tag :value="data.status.replace('_', ' ').toUpperCase()" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          
          <Column header="Actions">
            <template #body="{ data }">
              <Button 
                icon="pi pi-pencil" 
                class="p-button-text p-button-sm mr-2" 
                @click="openAssetDialog(data)"
              />
              <Button 
                icon="pi pi-wrench" 
                class="p-button-text p-button-sm mr-2" 
                @click="openMaintenanceDialog(data)"
              />
              <Button 
                v-if="data.status === 'active'"
                icon="pi pi-trash" 
                class="p-button-text p-button-sm p-button-danger" 
                @click="disposeAsset(data)"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog 
      v-model:visible="assetDialog" 
      :header="editMode ? 'Edit Asset' : 'New Asset'"
      :style="{ width: '800px' }"
      :modal="true"
    >
      <AssetForm 
        :asset="selectedAsset"
        :loading="formLoading"
        @submit="handleAssetSave"
        @cancel="assetDialog = false"
      />
    </Dialog>
  </div>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import AssetForm from './AssetForm.vue'

export default {
  name: 'AssetManagement',
  components: {
    ResponsiveContainer,
    AssetForm
  },
  
  data: () => ({
    loading: false,
    formLoading: false,
    assetDialog: false,
    editMode: false,
    selectedAsset: null,
    assets: [
      {
        id: 1,
        asset_number: 'FA-001',
        name: 'Office Computer',
        category: 'IT Equipment',
        purchase_cost: 1500,
        accumulated_depreciation: 300,
        status: 'active',
        purchase_date: '2023-01-15'
      }
    ],
    headers: [
      { title: 'Asset Number', key: 'asset_number' },
      { title: 'Name', key: 'name' },
      { title: 'Category', key: 'category' },
      { title: 'Purchase Cost', key: 'purchase_cost' },
      { title: 'Book Value', key: 'book_value' },
      { title: 'Status', key: 'status' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
  }),
  
  methods: {
    openAssetDialog(asset = null) {
      this.editMode = !!asset
      this.selectedAsset = asset || {
        asset_number: '',
        name: '',
        category: '',
        purchase_cost: 0,
        useful_life_years: 5,
        depreciation_method: 'straight_line'
      }
      this.assetDialog = true
    },
    
    openMaintenanceDialog(asset) {
      console.log('Open maintenance for:', asset.name)
    },
    
    async handleAssetSave(assetData) {
      try {
        this.formLoading = true
        if (this.editMode) {
          const index = this.assets.findIndex(a => a.id === assetData.id)
          this.assets[index] = { ...assetData }
        } else {
          this.assets.push({
            ...assetData,
            id: Date.now(),
            accumulated_depreciation: 0,
            status: 'active'
          })
        }
        this.assetDialog = false
      } finally {
        this.formLoading = false
      }
    },
    
    disposeAsset(asset) {
      if (confirm(`Are you sure you want to dispose ${asset.name}?`)) {
        asset.status = 'disposed'
      }
    },
    
    getStatusSeverity(status) {
      const severities = {
        active: 'success',
        disposed: 'danger',
        under_maintenance: 'warning',
        retired: 'secondary'
      }
      return severities[status] || 'info'
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }
  }
}
</script>