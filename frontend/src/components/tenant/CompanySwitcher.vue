<template>
  <v-menu>
    <template v-slot:activator="{ props }">
      <v-btn v-bind="props" variant="text" class="company-switcher">
        <v-avatar size="32" class="mr-2">
          <v-img v-if="currentCompany?.logo" :src="currentCompany.logo"></v-img>
          <span v-else>{{ currentCompany?.name?.charAt(0) }}</span>
        </v-avatar>
        {{ currentCompany?.name }}
        <v-icon right>mdi-chevron-down</v-icon>
      </v-btn>
    </template>
    
    <v-list>
      <v-list-item
        v-for="company in availableCompanies"
        :key="company.id"
        @click="switchCompany(company.id)"
        :disabled="company.id === currentCompany?.id"
      >
        <template v-slot:prepend>
          <v-avatar size="24">
            <v-img v-if="company.logo" :src="company.logo"></v-img>
            <span v-else>{{ company.name.charAt(0) }}</span>
          </v-avatar>
        </template>
        
        <v-list-item-title>{{ company.name }}</v-list-item-title>
        
        <template v-slot:append v-if="company.id === currentCompany?.id">
          <v-icon color="success">mdi-check</v-icon>
        </template>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script>
import { useTenantStore } from '@/stores/tenant'

export default {
  name: 'CompanySwitcher',
  
  computed: {
    currentCompany() {
      return this.tenantStore.currentCompany
    },
    availableCompanies() {
      return this.tenantStore.availableCompanies
    }
  },
  
  mounted() {
    this.tenantStore = useTenantStore()
  },
  
  methods: {
    async switchCompany(companyId) {
      if (companyId !== this.currentCompany?.id) {
        await this.tenantStore.switchCompany(companyId)
      }
    }
  }
}
</script>