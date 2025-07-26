<template>
  <AppLayout title="Accounts Payable - Vendors">
    <BaseDataTable
      title="Vendors"
      icon="mdi-domain"
      entity-name="Vendor"
      :headers="headers"
      :items="vendors"
      :loading="loading"
      :show-create="true"
      @create="createVendor"
      @edit="editVendor"
      @delete="deleteVendor"
    />
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import BaseDataTable from '@/components/common/BaseDataTable.vue'
import AppLayout from '@/layouts/AppLayout.vue'

const vendors = ref([])
const loading = ref(false)

const headers = [
  { title: 'Vendor ID', key: 'vendor_id', sortable: true },
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Email', key: 'email', sortable: true },
  { title: 'Phone', key: 'phone', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
]

const createVendor = () => {
  console.log('Create vendor')
}

const editVendor = (vendor: any) => {
  console.log('Edit vendor:', vendor)
}

const deleteVendor = (vendor: any) => {
  console.log('Delete vendor:', vendor)
}

onMounted(() => {
  vendors.value = []
})
</script>