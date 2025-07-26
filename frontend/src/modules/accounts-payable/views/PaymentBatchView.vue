<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <h1 class="text-h4">Payment Processing</h1>
          <v-btn color="primary" @click="showCreateBatch = true">
            <v-icon left>mdi-plus</v-icon>
            Create Payment Batch
          </v-btn>
        </div>
        
        <v-tabs v-model="activeTab">
          <v-tab value="batches">Payment Batches</v-tab>
          <v-tab value="individual">Individual Payments</v-tab>
          <v-tab value="methods">Payment Methods</v-tab>
          <v-tab value="approvals">Approvals</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="batches">
            <payment-batch-list @view="viewBatch" @approve="approveBatch" />
          </v-window-item>
          
          <v-window-item value="individual">
            <individual-payments @create="createPayment" />
          </v-window-item>
          
          <v-window-item value="methods">
            <payment-methods @create="createMethod" />
          </v-window-item>
          
          <v-window-item value="approvals">
            <payment-approvals @approve="approvePayment" />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
    
    <!-- Create Batch Dialog -->
    <payment-batch-dialog 
      v-model="showCreateBatch" 
      @save="createBatch"
    />
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import PaymentBatchList from '../components/payment/PaymentBatchList.vue'
import IndividualPayments from '../components/payment/IndividualPayments.vue'
import PaymentMethods from '../components/payment/PaymentMethods.vue'
import PaymentApprovals from '../components/payment/PaymentApprovals.vue'
import PaymentBatchDialog from '../components/payment/PaymentBatchDialog.vue'
import { usePaymentStore } from '../store/payments'

const paymentStore = usePaymentStore()
const activeTab = ref('batches')
const showCreateBatch = ref(false)

const createBatch = async (batchData) => {
  await paymentStore.createPaymentBatch(batchData)
  showCreateBatch.value = false
}

const viewBatch = (batch) => {
  console.log('View batch:', batch)
}

const approveBatch = async (batchId, approvalData) => {
  await paymentStore.approvePaymentBatch(batchId, approvalData)
}

const createPayment = async (paymentData) => {
  await paymentStore.createPayment(paymentData)
}

const createMethod = async (methodData) => {
  await paymentStore.createPaymentMethod(methodData)
}

const approvePayment = async (paymentId, approvalData) => {
  await paymentStore.approvePayment(paymentId, approvalData)
}
</script>