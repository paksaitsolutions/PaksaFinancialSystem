<template>
  <Dialog v-model:visible="dialog" :style="{ width: '500px' }" :modal="true" :closable="false">
    <template #header>
      <h3>Select Company</h3>
    </template>
    
    <div v-if="!loading">
      <div 
        v-for="company in availableCompanies"
        :key="company.id"
        class="flex align-items-center p-3 hover:surface-100 cursor-pointer border-round transition-colors transition-duration-150"
        @click="selectCompany(company.id)"
      >
        <Avatar 
          v-if="company.logo" 
          :image="company.logo" 
          size="large"
          shape="circle"
          class="mr-3"
        />
        <Avatar 
          v-else 
          :label="company.name.charAt(0)" 
          size="large"
          shape="circle"
          class="mr-3 bg-primary"
        />
        
        <div class="flex flex-column flex-1">
          <span class="font-medium">{{ company.name }}</span>
          <span class="text-color-secondary text-sm">{{ company.email }}</span>
        </div>
        
        <Tag 
          :value="company.status" 
          :severity="company.status === 'active' ? 'success' : 'warning'"
        />
      </div>
    </div>
    
    <div v-else class="text-center p-4">
      <ProgressSpinner />
    </div>
  </Dialog>
</template>

<script>
import { useTenantStore } from '@/stores/tenant'


/**
 * CompanySelector Component
 * 
 * @component
 */

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