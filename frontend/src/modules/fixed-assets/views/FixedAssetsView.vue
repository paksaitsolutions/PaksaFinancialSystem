<template>
  <ResponsiveContainer>
    <div class="p-4">
      <h1>Fixed Assets Module</h1>
      <TabView v-model:activeIndex="activeTabIndex" class="mb-4">
        <TabPanel header="Assets">
          <div class="p-4">
            <h2>Assets Tab Content</h2>
            <AssetManagement />
          </div>
        </TabPanel>
        
        <TabPanel header="Maintenance">
          <div class="p-4">
            <h2>Maintenance Tab Content</h2>
            <MaintenanceSchedule />
          </div>
        </TabPanel>
        
        <TabPanel header="Depreciation">
          <div class="p-4">
            <h2>Depreciation Tab Content</h2>
            <DepreciationSchedule />
          </div>
        </TabPanel>
        
        <TabPanel header="Reports">
          <div class="p-4">
            <h2>Reports Tab Content</h2>
            <AssetReports />
          </div>
        </TabPanel>
      </TabView>
    </div>
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
    activeTabIndex: 0
  }),
  
  mounted() {
    console.log('FixedAssetsView mounted successfully')
  }
}
</script>