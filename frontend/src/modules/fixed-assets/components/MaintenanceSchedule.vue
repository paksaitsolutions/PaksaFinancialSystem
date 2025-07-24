<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title class="d-flex align-center">
        <h2>Maintenance Schedule</h2>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="openMaintenanceDialog">
          <v-icon left>mdi-plus</v-icon>
          Schedule Maintenance
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-row class="mb-4">
          <v-col cols="12" md="4">
            <v-select
              v-model="filterStatus"
              :items="maintenanceStatuses"
              label="Status Filter"
              clearable
            ></v-select>
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="filterType"
              :items="maintenanceTypes"
              label="Type Filter"
              clearable
            ></v-select>
          </v-col>
          <v-col cols="12" md="4">
            <v-btn @click="loadUpcomingMaintenance" variant="outlined" block>
              Show Upcoming (30 days)
            </v-btn>
          </v-col>
        </v-row>

        <v-data-table
          :headers="headers"
          :items="filteredMaintenanceRecords"
          :loading="loading"
          :items-per-page="10"
        >
          <template v-slot:item.asset_name="{ item }">
            {{ getAssetName(item.asset_id) }}
          </template>
          
          <template v-slot:item.scheduled_date="{ item }">
            {{ formatDate(item.scheduled_date) }}
          </template>
          
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" small>
              {{ item.status.replace('_', ' ').toUpperCase() }}
            </v-chip>
          </template>
          
          <template v-slot:item.estimated_cost="{ item }">
            {{ item.estimated_cost ? formatCurrency(item.estimated_cost) : '-' }}
          </template>
          
          <template v-slot:item.actual_cost="{ item }">
            {{ item.actual_cost ? formatCurrency(item.actual_cost) : '-' }}
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn icon small @click="openMaintenanceDialog(item)">
              <v-icon small>mdi-pencil</v-icon>
            </v-btn>
            <v-btn 
              v-if="item.status === 'scheduled'"
              icon 
              small 
              color="success"
              @click="markCompleted(item)"
            >
              <v-icon small>mdi-check</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <v-dialog v-model="maintenanceDialog" max-width="600px">
      <v-card>
        <v-card-title>{{ editMode ? 'Edit Maintenance' : 'Schedule Maintenance' }}</v-card-title>
        <v-card-text>
          <MaintenanceForm 
            :maintenance="selectedMaintenance"
            :assets="assets"
            :loading="formLoading"
            @submit="handleMaintenanceSave"
            @cancel="maintenanceDialog = false"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import MaintenanceForm from './MaintenanceForm.vue'
import { fixedAssetApiService } from '../services/fixedAssetApiService'

export default {
  name: 'MaintenanceSchedule',
  components: {
    ResponsiveContainer,
    MaintenanceForm
  },
  
  data: () => ({
    loading: false,
    formLoading: false,
    maintenanceDialog: false,
    editMode: false,
    selectedMaintenance: null,
    maintenanceRecords: [],
    assets: [],
    filterStatus: null,
    filterType: null,
    maintenanceStatuses: [
      'scheduled',
      'in_progress',
      'completed',
      'cancelled'
    ],
    maintenanceTypes: [
      'Preventive',
      'Corrective',
      'Emergency',
      'Routine'
    ],
    headers: [
      { title: 'Asset', key: 'asset_name' },
      { title: 'Type', key: 'maintenance_type' },
      { title: 'Description', key: 'description' },
      { title: 'Scheduled Date', key: 'scheduled_date' },
      { title: 'Status', key: 'status' },
      { title: 'Estimated Cost', key: 'estimated_cost' },
      { title: 'Actual Cost', key: 'actual_cost' },
      { title: 'Actions', key: 'actions', sortable: false }
    ]
  }),
  
  computed: {
    filteredMaintenanceRecords() {
      let filtered = this.maintenanceRecords
      
      if (this.filterStatus) {
        filtered = filtered.filter(record => record.status === this.filterStatus)
      }
      
      if (this.filterType) {
        filtered = filtered.filter(record => record.maintenance_type === this.filterType)
      }
      
      return filtered
    }
  },
  
  async mounted() {
    await this.loadMaintenanceRecords()
    await this.loadAssets()
  },
  
  methods: {
    async loadMaintenanceRecords() {
      try {
        this.loading = true
        this.maintenanceRecords = await fixedAssetApiService.getMaintenanceRecords()
      } catch (error) {
        console.error('Error loading maintenance records:', error)
      } finally {
        this.loading = false
      }
    },
    
    async loadAssets() {
      try {
        this.assets = await fixedAssetApiService.getAssets()
      } catch (error) {
        console.error('Error loading assets:', error)
      }
    },
    
    async loadUpcomingMaintenance() {
      try {
        this.loading = true
        this.maintenanceRecords = await fixedAssetApiService.getUpcomingMaintenance(30)
      } catch (error) {
        console.error('Error loading upcoming maintenance:', error)
      } finally {
        this.loading = false
      }
    },
    
    openMaintenanceDialog(maintenance = null) {
      this.editMode = !!maintenance
      this.selectedMaintenance = maintenance || {
        asset_id: null,
        maintenance_type: 'Preventive',
        description: '',
        scheduled_date: new Date().toISOString().substr(0, 10),
        estimated_cost: 0,
        vendor_name: '',
        notes: ''
      }
      this.maintenanceDialog = true
    },
    
    async handleMaintenanceSave(maintenanceData) {
      try {
        this.formLoading = true
        
        if (this.editMode) {
          await fixedAssetApiService.updateMaintenanceRecord(maintenanceData.id, maintenanceData)
        } else {
          await fixedAssetApiService.createMaintenanceRecord(maintenanceData)
        }
        
        this.maintenanceDialog = false
        await this.loadMaintenanceRecords()
      } catch (error) {
        console.error('Error saving maintenance:', error)
      } finally {
        this.formLoading = false
      }
    },
    
    async markCompleted(maintenance) {
      try {
        await fixedAssetApiService.updateMaintenanceRecord(maintenance.id, {
          status: 'completed',
          completed_date: new Date().toISOString().substr(0, 10)
        })
        await this.loadMaintenanceRecords()
      } catch (error) {
        console.error('Error marking maintenance completed:', error)
      }
    },
    
    getAssetName(assetId) {
      const asset = this.assets.find(a => a.id === assetId)
      return asset ? asset.name : 'Unknown Asset'
    },
    
    getStatusColor(status) {
      const colors = {
        scheduled: 'info',
        in_progress: 'warning',
        completed: 'success',
        cancelled: 'error'
      }
      return colors[status] || 'grey'
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>