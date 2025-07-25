<template>
  <AppLayout title="Accounts Receivable - Customers">
    <BaseDataTable
      title="Customers"
      icon="mdi-account-group"
      entity-name="Customer"
      :headers="headers"
      :items="customers"
      :loading="loading"
      :show-create="true"
      @create="createCustomer"
      @edit="editCustomer"
      @delete="deleteCustomer"
    />
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import BaseDataTable from '@/components/common/BaseDataTable.vue'
import AppLayout from '@/layouts/AppLayout.vue'

const customers = ref([])
const loading = ref(false)

const headers = [
  { title: 'Customer ID', key: 'customer_id', sortable: true },
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Email', key: 'email', sortable: true },
  { title: 'Phone', key: 'phone', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
]

const createCustomer = () => {
  console.log('Create customer')
}

const editCustomer = (customer: any) => {
  console.log('Edit customer:', customer)
}

const deleteCustomer = (customer: any) => {
  console.log('Delete customer:', customer)
}

onMounted(() => {
  customers.value = []
})
</script>