<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <h1 class="text-h4">Bill Processing</h1>
          <v-btn color="primary" @click="showAddBill = true">
            <v-icon left>mdi-plus</v-icon>
            Add Bill
          </v-btn>
        </div>
        
        <v-tabs v-model="activeTab">
          <v-tab value="bills">Bills</v-tab>
          <v-tab value="approvals">Approvals</v-tab>
          <v-tab value="matching">Three-Way Matching</v-tab>
          <v-tab value="scheduling">Payment Scheduling</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="bills">
            <bill-list @edit="editBill" @approve="approveBill" />
          </v-window-item>
          
          <v-window-item value="approvals">
            <bill-approvals @approve="approveBill" @reject="rejectBill" />
          </v-window-item>
          
          <v-window-item value="matching">
            <three-way-matching @match="performMatching" />
          </v-window-item>
          
          <v-window-item value="scheduling">
            <payment-scheduling @schedule="schedulePayment" />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
    
    <!-- Add/Edit Bill Dialog -->
    <bill-form-dialog 
      v-model="showAddBill" 
      :bill="selectedBill"
      @save="saveBill"
    />
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useBillStore } from '../store/bills'

const billStore = useBillStore()
const activeTab = ref('bills')
const showAddBill = ref(false)
const selectedBill = ref(null)

const editBill = (bill) => {
  selectedBill.value = bill
  showAddBill.value = true
}

const saveBill = async (billData) => {
  if (selectedBill.value) {
    await billStore.updateBill(selectedBill.value.id, billData)
  } else {
    await billStore.createBill(billData)
  }
  showAddBill.value = false
  selectedBill.value = null
}

const approveBill = async (billId, approvalData) => {
  await billStore.approveBill(billId, approvalData)
}

const rejectBill = async (billId, rejectionData) => {
  await billStore.rejectBill(billId, rejectionData)
}

const performMatching = async (billId, matchData) => {
  await billStore.performThreeWayMatch(billId, matchData)
}

const schedulePayment = async (billId, scheduleData) => {
  await billStore.schedulePayment(billId, scheduleData)
}
</script>