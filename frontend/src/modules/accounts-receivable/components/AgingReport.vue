<template>
  <ResponsiveContainer>
    <Card>
      <template #header>
        <div class="flex justify-content-between align-items-center p-4">
          <h2 class="m-0">Accounts Receivable Aging Report</h2>
          <Button label="Refresh" icon="pi pi-refresh" @click="refreshReport" />
        </div>
      </template>
      
      <template #content>
        <!-- Summary Cards -->
        <div class="flex flex-wrap gap-3 mb-6">
          <div class="aging-card flex-1 min-w-12rem p-4 border-round bg-green-500 text-white text-center">
            <div class="text-2xl font-bold mb-2">{{ formatCurrency(summary.current) }}</div>
            <div class="text-sm opacity-90">Current (0-30 days)</div>
          </div>
          <div class="aging-card flex-1 min-w-12rem p-4 border-round bg-yellow-500 text-white text-center">
            <div class="text-2xl font-bold mb-2">{{ formatCurrency(summary.days31to60) }}</div>
            <div class="text-sm opacity-90">31-60 days</div>
          </div>
          <div class="aging-card flex-1 min-w-12rem p-4 border-round bg-orange-500 text-white text-center">
            <div class="text-2xl font-bold mb-2">{{ formatCurrency(summary.days61to90) }}</div>
            <div class="text-sm opacity-90">61-90 days</div>
          </div>
          <div class="aging-card flex-1 min-w-12rem p-4 border-round bg-red-500 text-white text-center">
            <div class="text-2xl font-bold mb-2">{{ formatCurrency(summary.over90) }}</div>
            <div class="text-sm opacity-90">Over 90 days</div>
          </div>
        </div>

        <!-- Aging Table -->
        <DataTable
          :value="agingData"
          :loading="loading"
          :paginator="true"
          :rows="10"
          responsiveLayout="scroll"
        >
          <Column field="customer_name" header="Customer">
            <template #body="{ data }">
              <strong>{{ data.customer_name }}</strong>
            </template>
          </Column>
          <Column field="current" header="Current">
            <template #body="{ data }">
              <span :class="data.current > 0 ? 'text-green-600' : ''">
                {{ formatCurrency(data.current) }}
              </span>
            </template>
          </Column>
          <Column field="days31to60" header="31-60 Days">
            <template #body="{ data }">
              <span :class="data.days31to60 > 0 ? 'text-yellow-600' : ''">
                {{ formatCurrency(data.days31to60) }}
              </span>
            </template>
          </Column>
          <Column field="days61to90" header="61-90 Days">
            <template #body="{ data }">
              <span :class="data.days61to90 > 0 ? 'text-orange-600' : ''">
                {{ formatCurrency(data.days61to90) }}
              </span>
            </template>
          </Column>
          <Column field="over90" header="Over 90 Days">
            <template #body="{ data }">
              <span :class="data.over90 > 0 ? 'text-red-600' : ''">
                {{ formatCurrency(data.over90) }}
              </span>
            </template>
          </Column>
          <Column field="total" header="Total">
            <template #body="{ data }">
              <strong>{{ formatCurrency(data.total) }}</strong>
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text p-button-sm mr-2" @click="viewCustomerDetail(data)" />
              <Button icon="pi pi-envelope" class="p-button-text p-button-sm" @click="contactCustomer(data)" :disabled="data.total <= 0" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Customer Detail Dialog -->
    <Dialog v-model:visible="detailDialog" :header="`${selectedCustomer?.customer_name} - Invoice Details`" :modal="true" :style="{ width: '800px' }">
      <DataTable
        :value="customerInvoices"
        :paginator="true"
        :rows="5"
        responsiveLayout="scroll"
      >
        <Column field="invoice_number" header="Invoice #" />
        <Column field="invoice_date" header="Invoice Date" />
        <Column field="due_date" header="Due Date" />
        <Column field="balance" header="Balance">
          <template #body="{ data }">
            {{ formatCurrency(data.balance) }}
          </template>
        </Column>
        <Column field="days_overdue" header="Days Overdue">
          <template #body="{ data }">
            <Tag :severity="getOverdueSeverity(data.days_overdue)" :value="data.days_overdue > 0 ? `${data.days_overdue} days` : 'Current'" />
          </template>
        </Column>
      </DataTable>
      
      <template #footer>
        <Button label="Close" icon="pi pi-times" class="p-button-text" @click="detailDialog = false" />
      </template>
    </Dialog>
  </ResponsiveContainer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Tag from 'primevue/tag'

const loading = ref(false)
const detailDialog = ref(false)
const selectedCustomer = ref(null)

const agingData = ref([
  {
    customer_id: '1',
    customer_name: 'ABC Corporation',
    current: 5000,
    days31to60: 2000,
    days61to90: 0,
    over90: 1000,
    total: 8000
  },
  {
    customer_id: '2',
    customer_name: 'XYZ Company',
    current: 3000,
    days31to60: 0,
    days61to90: 1500,
    over90: 0,
    total: 4500
  }
])

const customerInvoices = ref([
  {
    invoice_number: 'INV-1001',
    invoice_date: '2024-01-15',
    due_date: '2024-02-14',
    balance: 5000,
    days_overdue: 0
  },
  {
    invoice_number: 'INV-1002',
    invoice_date: '2023-12-15',
    due_date: '2024-01-14',
    balance: 2000,
    days_overdue: 45
  }
])

const summary = computed(() => {
  return agingData.value.reduce((sum, item) => ({
    current: sum.current + item.current,
    days31to60: sum.days31to60 + item.days31to60,
    days61to90: sum.days61to90 + item.days61to90,
    over90: sum.over90 + item.over90
  }), { current: 0, days31to60: 0, days61to90: 0, over90: 0 })
})

const refreshReport = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
  }, 1000)
}

const viewCustomerDetail = (customer: any) => {
  selectedCustomer.value = customer
  detailDialog.value = true
}

const contactCustomer = (customer: any) => {
  console.log('Contact customer:', customer.customer_name)
}

const getOverdueSeverity = (days: number) => {
  if (days <= 0) return 'success'
  if (days <= 30) return 'warning'
  if (days <= 60) return 'info'
  return 'danger'
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}
</script>

<style scoped>
.aging-card {
  transition: all 0.2s ease;
}

.aging-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
</style>