<template>
  <div class="vendors-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Vendors</h1>
        <Breadcrumb :home="home" :model="breadcrumbItems" />
      </div>
    </div>
    <VendorList />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const home = ref({ icon: 'pi pi-home', to: '/' })
const breadcrumbItems = ref([
  { label: 'Accounts Payable', to: '/ap' },
  { label: 'Vendors' }
])
</script>

<style scoped>
.vendors-view {
  padding: 1.5rem;
}
</style>