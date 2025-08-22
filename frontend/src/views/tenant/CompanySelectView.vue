<template>
  <div class="flex align-items-center justify-content-center min-h-screen bg-gray-100 p-3">
    <div class="w-full md:w-6 lg:w-4">
      <Card>
        <template #title>
          <h2 class="text-center">Select Your Company</h2>
        </template>
        
        <template #content>
          <div v-if="loading" class="flex justify-content-center p-8">
            <ProgressSpinner />
          </div>
          
          <div v-else class="grid">
            <div 
              v-for="company in availableCompanies"
              :key="company.id"
              class="col-12 p-0"
            >
              <div 
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
                  class="mr-3"
                />
                
                <div class="flex flex-column">
                  <span class="font-medium">{{ company.name }}</span>
                  <span class="text-color-secondary text-sm">{{ company.email }}</span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useTenantStore } from '@/stores/tenant';
import Card from 'primevue/card';
import Avatar from 'primevue/avatar';
import ProgressSpinner from 'primevue/progressspinner';

const loading = ref(false);
const router = useRouter();
const tenantStore = useTenantStore();

const availableCompanies = computed(() => {
  return tenantStore.availableCompanies;
});

onMounted(() => {
  loading.value = true;
  // Load companies if not already loaded
  tenantStore.loadCompanies().finally(() => {
    loading.value = false;
  });
});

function selectCompany(companyId) {
  router.push({ name: 'dashboard' });
}
</script>