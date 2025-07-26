<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Collections Management</h1>
        
        <v-tabs v-model="activeTab">
          <v-tab value="workflow">Collections Workflow</v-tab>
          <v-tab value="dunning">Dunning Letters</v-tab>
          <v-tab value="reminders">Payment Reminders</v-tab>
          <v-tab value="aging">Aging Report</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="workflow">
            <collections-workflow @start="startWorkflow" />
          </v-window-item>
          
          <v-window-item value="dunning">
            <dunning-letter-management @send="sendDunningLetter" />
          </v-window-item>
          
          <v-window-item value="reminders">
            <payment-reminder-system @create="createReminder" />
          </v-window-item>
          
          <v-window-item value="aging">
            <aging-report-dashboard />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import CollectionsWorkflow from '../components/collections/CollectionsWorkflow.vue'
import DunningLetterManagement from '../components/collections/DunningLetterManagement.vue'
import PaymentReminderSystem from '../components/collections/PaymentReminderSystem.vue'
import AgingReportDashboard from '../components/collections/AgingReportDashboard.vue'
import { useCollectionsStore } from '../store/collections'

const collectionsStore = useCollectionsStore()
const activeTab = ref('workflow')

const startWorkflow = async (customerId, workflowData) => {
  await collectionsStore.startCollectionsWorkflow(customerId, workflowData)
}

const sendDunningLetter = async (letterData) => {
  await collectionsStore.sendDunningLetter(letterData)
}

const createReminder = async (reminderData) => {
  await collectionsStore.createPaymentReminder(reminderData)
}
</script>