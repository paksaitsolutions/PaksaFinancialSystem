<template>
  <div class="bank-reconciliation-interface">
    <Card>
      <template #title>Bank Reconciliation</template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="bankAccount">Bank Account</label>
              <Dropdown 
                id="bankAccount"
                v-model="reconciliationData.accountId"
                :options="bankAccounts"
                optionLabel="name"
                optionValue="id"
                placeholder="Select bank account"
                class="w-full"
              />
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="statementDate">Statement Date</label>
              <Calendar 
                id="statementDate"
                v-model="reconciliationData.statementDate"
                dateFormat="yy-mm-dd"
                :showIcon="true"
                class="w-full"
              />
            </div>
          </div>
        </div>
        
        <div class="field">
          <label for="statementBalance">Statement Balance</label>
          <InputNumber 
            id="statementBalance"
            v-model="reconciliationData.statementBalance"
            mode="currency"
            currency="USD"
            locale="en-US"
            class="w-full"
          />
        </div>
        
        <Button 
          label="Start Reconciliation" 
          icon="pi pi-check-circle"
          @click="startReconciliation"
          :loading="loading"
        />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const emit = defineEmits(['reconcile'])

const loading = ref(false)
const reconciliationData = reactive({
  accountId: null,
  statementDate: new Date(),
  statementBalance: 0
})

const bankAccounts = ref([
  { id: 1, name: 'Main Business Account - HBL' },
  { id: 2, name: 'Savings Account - Meezan Bank' },
  { id: 3, name: 'USD Account - HBL' }
])

const startReconciliation = async () => {
  loading.value = true
  try {
    emit('reconcile', reconciliationData)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
</style>