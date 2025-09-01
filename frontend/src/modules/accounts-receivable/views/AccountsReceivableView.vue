<template>
  <ResponsiveContainer>
    <TabView v-model:activeIndex="activeTabIndex" class="mb-4">
      <TabPanel header="Customers">
        <CustomerManagement />
      </TabPanel>
      
      <TabPanel header="Invoices">
        <InvoiceGeneration />
      </TabPanel>
      
      <TabPanel header="Payments">
        <PaymentProcessing />
      </TabPanel>
      
      <TabPanel header="Aging Report">
        <AgingReport />
      </TabPanel>
    </TabView>
  </ResponsiveContainer>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import CustomerManagement from '../components/CustomerManagement.vue'
import InvoiceGeneration from '../components/InvoiceGeneration.vue'
import PaymentProcessing from '../components/PaymentProcessing.vue'
import AgingReport from '../components/AgingReport.vue'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'

const activeTabIndex = ref(0)
</script>