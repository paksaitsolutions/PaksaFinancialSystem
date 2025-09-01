<template>
  <ResponsiveContainer>
    <Card>
      <template #header>
        <div class="flex justify-content-between align-items-center p-4">
          <h2 class="m-0">Maintenance Schedule</h2>
          <Button 
            label="Schedule Maintenance" 
            icon="pi pi-plus" 
            @click="openMaintenanceDialog"
          />
        </div>
      </template>
      
      <template #content>
        <div class="grid mb-4">
          <div class="col-12 md:col-4">
            <Dropdown
              v-model="filterStatus"
              :options="maintenanceStatuses"
              placeholder="Status Filter"
              :showClear="true"
            />
          </div>
          <div class="col-12 md:col-4">
            <Dropdown
              v-model="filterType"
              :options="maintenanceTypes"
              placeholder="Type Filter"
              :showClear="true"
            />
          </div>
          <div class="col-12 md:col-4">
            <Button 
              label="Show Upcoming (30 days)" 
              @click="loadUpcomingMaintenance" 
              outlined 
              class="w-full"
            />
          </div>
        </div>

        <DataTable
          :value="filteredMaintenanceRecords"
          :loading="loading"
          :paginator="true"
          :rows="10"
          responsiveLayout="scroll"
        >
          <Column field="asset_name" header="Asset">
            <template #body="{ data }">
              {{ getAssetName(data.asset_id) }}
            </template>
          </Column>
          
          <Column field="maintenance_type" header="Type"></Column>
          <Column field="description" header="Description"></Column>
          
          <Column field="scheduled_date" header="Scheduled Date">
            <template #body="{ data }">
              {{ formatDate(data.scheduled_date) }}
            </template>
          </Column>
          
          <Column field="status" header="Status">
            <template #body="{ data }">
              <Tag :value="data.status.replace('_', ' ').toUpperCase()" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          
          <Column field="estimated_cost" header="Estimated Cost">
            <template #body="{ data }">
              {{ data.estimated_cost ? formatCurrency(data.estimated_cost) : '-' }}
            </template>
          </Column>
          
          <Column field="actual_cost" header="Actual Cost">
            <template #body="{ data }">
              {{ data.actual_cost ? formatCurrency(data.actual_cost) : '-' }}
            </template>
          </Column>
          
          <Column header="Actions">
            <template #body="{ data }">
              <Button 
                icon="pi pi-pencil" 
                class="p-button-text p-button-sm mr-2" 
                @click="openMaintenanceDialog(data)"
              />
              <Button 
                v-if="data.status === 'scheduled'"
                icon="pi pi-check" 
                class="p-button-text p-button-sm p-button-success" 
                @click="markCompleted(data)"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog 
      v-model:visible="maintenanceDialog" 
      :header="editMode ? 'Edit Maintenance' : 'Schedule Maintenance'"
      :style="{ width: '600px' }"
      :modal="true"
    >
      <MaintenanceForm 
        :maintenance="selectedMaintenance"
        :assets="assets"
        :loading="formLoading"
        @submit="handleMaintenanceSave"
        @cancel="maintenanceDialog = false"
      />
    </Dialog>
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
  
  data() {
    return {
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
    }
  },
  
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
  
  mounted() {
    console.log('MaintenanceSchedule mounted')
    this.loadMaintenanceRecords()
    this.loadAssets()
  },
  
  methods: {
    loadMockData() {
      this.assets = [
        { id: 1, name: 'Office Computer' },
        { id: 2, name: 'Printer' },
        { id: 3, name: 'Company Vehicle' }
      ]
      
      this.maintenanceRecords = [
        {
          id: 1,
          asset_id: 1,
          maintenance_type: 'Preventive',
          description: 'Regular system maintenance',
          scheduled_date: '2024-02-15',
          status: 'scheduled',
          estimated_cost: 150,
          actual_cost: null
        },
        {
          id: 2,
          asset_id: 3,
          maintenance_type: 'Corrective',
          description: 'Oil change and inspection',
          scheduled_date: '2024-01-20',
          status: 'completed',
          estimated_cost: 200,
          actual_cost: 185
        }
      ]
    },
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
    
    getStatusSeverity(status) {
      const severities = {
        scheduled: 'info',
        in_progress: 'warning',
        completed: 'success',
        cancelled: 'danger'
      }
      return severities[status] || 'secondary'
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