<template>
  <div class="p-4">
    <h1>Settings</h1>
    <TabView>
      <TabPanel header="General">
        <GeneralSettings />
      </TabPanel>
      
      <TabPanel header="Users">
        <UserManagement />
      </TabPanel>
      
      <TabPanel header="Tenant">
        <TenantManagement />
      </TabPanel>
      
      <TabPanel header="Security">
        <SecuritySettings />
      </TabPanel>
    </TabView>
  </div>
</template>

<script setup lang="ts">
import GeneralSettings from './GeneralSettings.vue'
import UserManagement from './UserManagement.vue'
import TenantManagement from '../../tenant/views/TenantManagement.vue'
import SecuritySettings from './SecuritySettings.vue'
</script>