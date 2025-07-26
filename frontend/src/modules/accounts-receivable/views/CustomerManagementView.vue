<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <h1 class="text-h4">Customer Management</h1>
          <v-btn color="primary" @click="showAddCustomer = true">
            <v-icon left>mdi-plus</v-icon>
            Add Customer
          </v-btn>
        </div>
        
        <v-tabs v-model="activeTab">
          <v-tab value="customers">Customers</v-tab>
          <v-tab value="credit">Credit Management</v-tab>
          <v-tab value="aging">Aging Reports</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="customers">
            <customer-list @edit="editCustomer" @view-credit="viewCredit" />
          </v-window-item>
          
          <v-window-item value="credit">
            <customer-credit-dashboard @update-credit="updateCredit" />
          </v-window-item>
          
          <v-window-item value="aging">
            <customer-aging-reports />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
    
    <customer-form-dialog 
      v-model="showAddCustomer" 
      :customer="selectedCustomer"
      @save="saveCustomer"
    />
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import CustomerList from '../components/customer/CustomerList.vue'
import CustomerCreditDashboard from '../components/customer/CustomerCreditDashboard.vue'
import CustomerAgingReports from '../components/customer/CustomerAgingReports.vue'
import CustomerFormDialog from '../components/customer/CustomerFormDialog.vue'
import { useCustomerStore } from '../store/customers'

const customerStore = useCustomerStore()
const activeTab = ref('customers')
const showAddCustomer = ref(false)
const selectedCustomer = ref(null)

const editCustomer = (customer) => {
  selectedCustomer.value = customer
  showAddCustomer.value = true
}

const viewCredit = (customer) => {
  selectedCustomer.value = customer
  activeTab.value = 'credit'
}

const saveCustomer = async (customerData) => {
  if (selectedCustomer.value) {
    await customerStore.updateCustomer(selectedCustomer.value.id, customerData)
  } else {
    await customerStore.createCustomer(customerData)
  }
  showAddCustomer.value = false
  selectedCustomer.value = null
}

const updateCredit = async (customerId, creditData) => {
  await customerStore.updateCustomerCredit(customerId, creditData)
}
</script>