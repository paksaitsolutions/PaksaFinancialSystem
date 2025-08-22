<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Banking Integration</h1>
        
        <v-tabs v-model="activeTab">
          <v-tab value="import">Bank Statement Import</v-tab>
          <v-tab value="payments">Payment Processing</v-tab>
          <v-tab value="fees">Banking Fee Tracking</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="import">
            <bank-statement-import-interface @import="importStatement" />
          </v-window-item>
          
          <v-window-item value="payments">
            <payment-processing-dashboard @process="processPayment" />
          </v-window-item>
          
          <v-window-item value="fees">
            <banking-fee-tracking @create="createFee" />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import BankStatementImportInterface from '../components/BankStatementImportInterface.vue'
import PaymentProcessingDashboard from '../components/PaymentProcessingDashboard.vue'
import BankingFeeTracking from '../components/BankingFeeTracking.vue'
import { useCashManagementStore } from '../store/cash-management'

const cashStore = useCashManagementStore()
const activeTab = ref('import')

const importStatement = async (statementData) => {
  await cashStore.importBankStatement(statementData)
}

const processPayment = async (paymentData) => {
  await cashStore.processPayment(paymentData)
}

const createFee = async (feeData) => {
  await cashStore.createBankingFee(feeData)
}
</script>