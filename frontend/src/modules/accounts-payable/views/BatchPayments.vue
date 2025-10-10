<template>
  <div class="batch-payments">
    <h2>Batch Payments</h2>
    <Card>
      <template #content>
        <DataTable :value="selectedBills" selectionMode="multiple" v-model:selection="selectedForPayment">
          <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
          <Column field="vendor" header="Vendor"></Column>
          <Column field="amount" header="Amount"></Column>
          <Column field="dueDate" header="Due Date"></Column>
        </DataTable>
        <div class="mt-4">
          <Button label="Process Batch Payment" icon="pi pi-credit-card" @click="processBatchPayment" :loading="processing" />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const processing = ref(false)
const selectedBills = ref([])
const selectedForPayment = ref([])

const processBatchPayment = async () => {
  processing.value = true
  try {
    // Batch payment logic here
    toast.add({ severity: 'success', summary: 'Success', detail: 'Batch payment processed' })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to process payments' })
  } finally {
    processing.value = false
  }
}
</script>