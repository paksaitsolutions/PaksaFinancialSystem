<template>
  <v-dialog v-model="dialog" max-width="500px" persistent>
    <v-card>
      <v-card-title>Select Company</v-card-title>
      
      <v-card-text>
        <v-list v-if="!loading">
          <v-list-item
            v-for="company in availableCompanies"
            :key="company.id"
            @click="selectCompany(company.id)"
          >
            <template v-slot:prepend>
              <v-avatar v-if="company.logo">
                <v-img :src="company.logo"></v-img>
              </v-avatar>
              <v-avatar v-else color="primary">
                {{ company.name.charAt(0) }}
              </v-avatar>
            </template>
            
            <v-list-item-title>{{ company.name }}</v-list-item-title>
            <v-list-item-subtitle>{{ company.email }}</v-list-item-subtitle>
            
            <template v-slot:append>
              <v-chip :color="company.status === 'active' ? 'success' : 'warning'" small>
                {{ company.status }}
              </v-chip>
            </template>
          </v-list-item>
        </v-list>
        
        <div v-else class="text-center py-4">
          <v-progress-circular indeterminate></v-progress-circular>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { useTenantStore } from '@/stores/tenant'

export default {
  name: 'CompanySelector',
  
  props: {
    modelValue: Boolean
  },
  
  emits: ['update:modelValue', 'company-selected'],
  
  data: () => ({
    loading: false
  }),
  
  computed: {
    dialog: {
      get() { return this.modelValue },
      set(value) { this.$emit('update:modelValue', value) }
    },
    availableCompanies() {
      return this.tenantStore.availableCompanies
    }
  },
  
  async mounted() {
    this.tenantStore = useTenantStore()
    await this.loadCompanies()
  },
  
  methods: {
    async loadCompanies() {
      this.loading = true
      try {
        await this.tenantStore.fetchAvailableCompanies()
      } finally {
        this.loading = false
      }
    },
    
    async selectCompany(companyId) {
      await this.tenantStore.selectCompany(companyId)
      this.$emit('company-selected')
      this.dialog = false
    }
  }
}
</script>