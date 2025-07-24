<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Fixed Assets Management</h2>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="openAssetDialog">
          <v-icon left>mdi-plus</v-icon>
          New Asset
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="assets"
          :loading="loading"
          :items-per-page="10"
        >
          <template v-slot:item.asset_number="{ item }">
            <a href="#" @click.prevent="openAssetDialog(item)" class="text-primary">
              {{ item.asset_number }}
            </a>
          </template>
          
          <template v-slot:item.purchase_cost="{ item }">
            {{ formatCurrency(item.purchase_cost) }}
          </template>
          
          <template v-slot:item.book_value="{ item }">
            {{ formatCurrency(item.purchase_cost - item.accumulated_depreciation) }}
          </template>
          
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" small>
              {{ item.status.replace('_', ' ').toUpperCase() }}
            </v-chip>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn icon small @click="openAssetDialog(item)">
              <v-icon small>mdi-pencil</v-icon>
            </v-btn>
            <v-btn icon small @click="openMaintenanceDialog(item)">
              <v-icon small>mdi-wrench</v-icon>
            </v-btn>
            <v-btn 
              v-if="item.status === 'active'"
              icon 
              small 
              color="warning"
              @click="disposeAsset(item)"
            >
              <v-icon small>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="assetDialog" max-width="800px">
      <v-card>
        <v-card-title>{{ editMode ? 'Edit Asset' : 'New Asset' }}</v-card-title>
        <v-card-text>
          <AssetForm 
            :asset="selectedAsset"
            :loading="formLoading"
            @submit="handleAssetSave"
            @cancel="assetDialog = false"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
  </ResponsiveContainer>
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
    
    getStatusColor(status) {
      const colors = {
        active: 'success',
        disposed: 'error',
        under_maintenance: 'warning',
        retired: 'secondary'
      }
      return colors[status] || 'grey'
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