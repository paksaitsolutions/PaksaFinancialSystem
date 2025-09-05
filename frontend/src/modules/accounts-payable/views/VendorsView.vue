<template>
  <AppLayout title="Accounts Payable - Vendors">
    <VendorList />
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'
import VendorList from '@/modules/accounts-payable/components/vendor/VendorList.vue'
</script>