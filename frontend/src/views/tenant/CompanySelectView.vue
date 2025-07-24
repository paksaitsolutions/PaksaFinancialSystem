<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card>
          <v-card-title class="text-center">
            <h2>Select Your Company</h2>
          </v-card-title>
          
          <v-card-text>
            <div v-if="loading" class="text-center py-8">
              <v-progress-circular indeterminate></v-progress-circular>
            </div>
            
            <v-list v-else>
              <v-list-item
                v-for="company in availableCompanies"
                :key="company.id"
                @click="selectCompany(company.id)"
              >
                <template v-slot:prepend>
                  <v-avatar>
                    <v-img v-if="company.logo" :src="company.logo"></v-img>
                    <span v-else>{{ company.name.charAt(0) }}</span>
                  </v-avatar>
                </template>
                
                <v-list-item-title>{{ company.name }}</v-list-item-title>
                <v-list-item-subtitle>{{ company.email }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useTenantStore } from '@/stores/tenant'

export default {
  name: 'CompanySelectView',
  
  data: () => ({
    loading: false
  }),
  
  computed: {
    availableCompanies() {
      return this.tenantStore.availableCompanies
    }
  },
  
  async mounted() {
    this.tenantStore = useTenantStore()
    this.loading = true
    await this.tenantStore.fetchAvailableCompanies()
    this.loading = false
  },
  
  methods: {
    async selectCompany(companyId) {
      await this.tenantStore.selectCompany(companyId)
      this.$router.push('/')
    }
  }
}
</script>