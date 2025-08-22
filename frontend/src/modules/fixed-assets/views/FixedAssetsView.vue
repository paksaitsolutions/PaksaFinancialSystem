<template>
  <ResponsiveContainer>
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab value="assets">Assets</v-tab>
      <v-tab value="maintenance">Maintenance</v-tab>
      <v-tab value="depreciation">Depreciation</v-tab>
      <v-tab value="reports">Reports</v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <v-window-item value="assets">
        <AssetManagement />
      </v-window-item>
      
      <v-window-item value="maintenance">
        <MaintenanceSchedule />
      </v-window-item>
      
      <v-window-item value="depreciation">
        <DepreciationSchedule />
      </v-window-item>
      
      <v-window-item value="reports">
        <AssetReports />
      </v-window-item>
    </v-window>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import AssetManagement from '../components/AssetManagement.vue'
import MaintenanceSchedule from '../components/MaintenanceSchedule.vue'
import DepreciationSchedule from '../components/DepreciationSchedule.vue'
import AssetReports from '../components/AssetReports.vue'

export default {
  name: 'FixedAssetsView',
  components: {
    ResponsiveContainer,
    AssetManagement,
    MaintenanceSchedule,
    DepreciationSchedule,
    AssetReports
  },
  
  data: () => ({
    activeTab: 'assets'
  })
}
</script>