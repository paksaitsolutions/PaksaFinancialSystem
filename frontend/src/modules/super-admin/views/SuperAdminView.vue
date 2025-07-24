<template>
  <ResponsiveContainer>
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab value="analytics">Analytics</v-tab>
      <v-tab value="companies">Companies</v-tab>
      <v-tab value="config">Configuration</v-tab>
      <v-tab value="logs">Logs & Monitoring</v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <v-window-item value="analytics">
        <PlatformAnalytics />
      </v-window-item>
      
      <v-window-item value="companies">
        <CompanyManagement 
          @company-approved="handleCompanyApproved"
          @company-suspended="handleCompanySuspended"
        />
      </v-window-item>
      
      <v-window-item value="config">
        <GlobalConfiguration @configuration-saved="handleConfigSaved" />
      </v-window-item>
      
      <v-window-item value="logs">
        <SystemMonitoring />
      </v-window-item>
    </v-window>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import PlatformAnalytics from '../components/PlatformAnalytics.vue'
import CompanyManagement from '../components/CompanyManagement.vue'
import GlobalConfiguration from '../components/GlobalConfiguration.vue'
import SystemMonitoring from '../components/SystemMonitoring.vue'

export default {
  name: 'SuperAdminView',
  components: {
    ResponsiveContainer,
    PlatformAnalytics,
    CompanyManagement,
    GlobalConfiguration,
    SystemMonitoring
  },
  
  data: () => ({
    activeTab: 'analytics'
  }),

  methods: {
    handleCompanyApproved(company) {
      console.log('Company approved:', company.name)
    },

    handleCompanySuspended(company) {
      console.log('Company suspended:', company.name)
    },

    handleConfigSaved(config) {
      console.log('Configuration saved:', config)
    }
  }
}
</script>