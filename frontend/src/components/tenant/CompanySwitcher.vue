<template>
  <div class="relative">
    <Button 
      @click="toggle" 
      class="p-button-text company-switcher flex align-items-center"
      :aria-haspopup="true" 
      :aria-expanded="overlayVisible"
    >
      <Avatar 
        v-if="currentCompany?.logo" 
        :image="currentCompany.logo" 
        size="normal"
        shape="circle"
        class="mr-2"
      />
      <Avatar 
        v-else 
        :label="currentCompany?.name?.charAt(0)" 
        size="normal"
        shape="circle"
        class="mr-2"
      />
      {{ currentCompany?.name }}
      <i class="pi pi-chevron-down ml-2"></i>
    </Button>
    
    <OverlayPanel ref="op" :showCloseIcon="false">
      <div class="flex flex-column gap-2" style="min-width: 200px;">
        <div 
          v-for="company in availableCompanies"
          :key="company.id"
          class="flex align-items-center p-2 hover:surface-100 cursor-pointer border-round transition-colors transition-duration-150"
          :class="{ 'surface-200': company.id === currentCompany?.id }"
          @click="switchCompany(company.id)"
        >
          <Avatar 
            v-if="company.logo" 
            :image="company.logo" 
            size="small"
            shape="circle"
            class="mr-2"
          />
          <Avatar 
            v-else 
            :label="company.name.charAt(0)" 
            size="small"
            shape="circle"
            class="mr-2"
          />
          
          <span class="flex-1">{{ company.name }}</span>
          
          <i v-if="company.id === currentCompany?.id" class="pi pi-check text-green-500"></i>
        </div>
      </div>
    </OverlayPanel>
  </div>
</template>

<script>
import { useTenantStore } from '@/stores/tenant'

import { ref, computed, onMounted } from 'vue'
import { useTenantStore } from '@/stores/tenant'

export default {
  name: 'CompanySwitcher',
  
  setup() {
    const op = ref()
    const overlayVisible = ref(false)
    const tenantStore = useTenantStore()
    
    const currentCompany = computed(() => tenantStore.currentCompany)
    const availableCompanies = computed(() => tenantStore.availableCompanies)
    
    const toggle = (event) => {
      op.value.toggle(event)
      overlayVisible.value = !overlayVisible.value
    }
    
    const switchCompany = async (companyId) => {
      if (companyId !== currentCompany.value?.id) {
        await tenantStore.switchCompany(companyId)
      }
      op.value.hide()
      overlayVisible.value = false
    }
    
    return {
      op,
      overlayVisible,
      currentCompany,
      availableCompanies,
      toggle,
      switchCompany
    }
  }
}
</script>