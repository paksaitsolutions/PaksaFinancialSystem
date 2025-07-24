<template>
  <ResponsiveContainer>
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab value="customers">Customers</v-tab>
      <v-tab value="invoices">Invoices</v-tab>
      <v-tab value="payments">Payments</v-tab>
      <v-tab value="aging">Aging Report</v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <v-window-item value="customers">
        <CustomerManagement />
      </v-window-item>
      
      <v-window-item value="invoices">
        <InvoiceGeneration />
      </v-window-item>
      
      <v-window-item value="payments">
        <PaymentProcessing />
      </v-window-item>
      
      <v-window-item value="aging">
        <AgingReport />
      </v-window-item>
    </v-window>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import CustomerManagement from '../components/CustomerManagement.vue'
import InvoiceGeneration from '../components/InvoiceGeneration.vue'
import PaymentProcessing from '../components/PaymentProcessing.vue'
import AgingReport from '../components/AgingReport.vue'

export default {
  name: 'AccountsReceivableView',
  components: {
    ResponsiveContainer,
    CustomerManagement,
    InvoiceGeneration,
    PaymentProcessing,
    AgingReport
  },
  
  data: () => ({
    activeTab: 'customers'
  })
}
</script>