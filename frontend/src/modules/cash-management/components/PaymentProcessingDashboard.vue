<template>
  <div class="payment-processing-dashboard">
    <Card>
      <template #title>Payment Processing</template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-4">
            <Card class="h-full">
              <template #title>Pending Payments</template>
              <template #content>
                <div class="text-4xl font-bold text-orange-500 mb-2">
                  {{ pendingPayments }}
                </div>
                <div class="text-sm text-500">
                  Awaiting processing
                </div>
              </template>
            </Card>
          </div>
          
          <div class="col-12 md:col-4">
            <Card class="h-full">
              <template #title>Processed Today</template>
              <template #content>
                <div class="text-4xl font-bold text-green-500 mb-2">
                  {{ processedToday }}
                </div>
                <div class="text-sm text-500">
                  Successfully completed
                </div>
              </template>
            </Card>
          </div>
          
          <div class="col-12 md:col-4">
            <Card class="h-full">
              <template #title>Failed Payments</template>
              <template #content>
                <div class="text-4xl font-bold text-red-500 mb-2">
                  {{ failedPayments }}
                </div>
                <div class="text-sm text-500">
                  Require attention
                </div>
              </template>
            </Card>
          </div>
        </div>
        
        <div class="mt-4">
          <h3>Recent Payment Activity</h3>
          <DataTable :value="recentPayments" responsiveLayout="scroll">
            <Column field="id" header="Payment ID" :sortable="true" />
            <Column field="amount" header="Amount" :sortable="true">
              <template #body="{ data }">
                {{ formatCurrency(data.amount) }}
              </template>
            </Column>
            <Column field="recipient" header="Recipient" :sortable="true" />
            <Column field="status" header="Status" :sortable="true">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
            <Column field="date" header="Date" :sortable="true">
              <template #body="{ data }">
                {{ formatDate(data.date) }}
              </template>
            </Column>
          </DataTable>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const pendingPayments = ref(12)
const processedToday = ref(45)
const failedPayments = ref(3)

const recentPayments = ref([
  {
    id: 'PAY-001',
    amount: 5000,
    recipient: 'ABC Suppliers',
    status: 'Completed',
    date: new Date()
  },
  {
    id: 'PAY-002',
    amount: 2500,
    recipient: 'XYZ Services',
    status: 'Pending',
    date: new Date()
  },
  {
    id: 'PAY-003',
    amount: 1200,
    recipient: 'Office Supplies Co',
    status: 'Failed',
    date: new Date()
  }
])

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const formatDate = (date: Date) => {
  return date.toLocaleDateString()
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'Completed': return 'success'
    case 'Pending': return 'warning'
    case 'Failed': return 'danger'
    default: return 'info'
  }
}
</script>

<style scoped>
/* Component styles */
</style>