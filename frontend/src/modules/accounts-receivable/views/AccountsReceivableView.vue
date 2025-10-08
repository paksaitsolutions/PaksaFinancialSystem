<template>
  <div class="ar-dashboard">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Accounts Receivable</h1>
        <p class="text-color-secondary">Manage customer invoices and payments</p>
      </div>
      <Button label="Create Invoice" icon="pi pi-plus" @click="openInvoiceDialog" />
    </div>

    <div class="grid">
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-receipt text-4xl text-green-500 mb-3"></i>
              <div class="text-2xl font-bold">${{ stats.totalReceivable }}</div>
              <div class="text-color-secondary">Total Receivable</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-clock text-4xl text-orange-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.overdueInvoices }}</div>
              <div class="text-color-secondary">Overdue Invoices</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-users text-4xl text-blue-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.activeCustomers }}</div>
              <div class="text-color-secondary">Active Customers</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-money-bill text-4xl text-purple-500 mb-3"></i>
              <div class="text-2xl font-bold">${{ stats.monthlyRevenue }}</div>
              <div class="text-color-secondary">Monthly Revenue</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <div class="grid">
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>Recent Invoices</template>
          <template #content>
            <DataTable :value="recentInvoices" :rows="5">
              <Column field="customer" header="Customer" />
              <Column field="invoiceNumber" header="Invoice #" />
              <Column field="dueDate" header="Due Date" />
              <Column field="amount" header="Amount" />
              <Column field="status" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-4">
        <Card>
          <template #title>Quick Actions</template>
          <template #content>
            <div class="quick-actions">
              <Button label="Add Customer" icon="pi pi-user-plus" class="w-full mb-2" @click="$router.push('/ar/customers')" />
              <Button label="Record Payment" icon="pi pi-money-bill" class="w-full mb-2 p-button-secondary" @click="recordPayment" />
              <Button label="Send Reminders" icon="pi pi-send" class="w-full mb-2 p-button-success" @click="sendReminders" />
              <Button label="View Reports" icon="pi pi-chart-bar" class="w-full p-button-info" @click="$router.push('/ar/reports')" />
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Dialog v-model:visible="invoiceDialog" header="Create Invoice" :modal="true" :style="{width: '600px'}">
      <div class="field">
        <label>Customer</label>
        <Dropdown v-model="invoice.customerId" :options="customers" optionLabel="name" optionValue="id" placeholder="Select Customer" class="w-full" />
      </div>
      <div class="field">
        <label>Invoice Date</label>
        <Calendar v-model="invoice.invoiceDate" class="w-full" />
      </div>
      <div class="field">
        <label>Due Date</label>
        <Calendar v-model="invoice.dueDate" class="w-full" />
      </div>
      <div class="field">
        <label>Amount</label>
        <InputNumber v-model="invoice.amount" mode="currency" currency="USD" class="w-full" />
      </div>
      <div class="field">
        <label>Description</label>
        <Textarea v-model="invoice.description" rows="3" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="invoiceDialog = false" />
        <Button label="Create" @click="createInvoice" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { analyticsService, customerService, invoiceService } from '@/api/arService'

const toast = useToast()
const invoiceDialog = ref(false)
const loading = ref(false)
const dashboardData = ref(null)
const recentInvoicesData = ref([])
const customersData = ref([])

const stats = computed(() => {
  if (!dashboardData.value) {
    return {
      totalReceivable: '0',
      overdueInvoices: 0,
      activeCustomers: 0,
      monthlyRevenue: '0'
    }
  }
  
  const kpis = dashboardData.value.kpis
  return {
    totalReceivable: formatCurrency(kpis.total_outstanding),
    overdueInvoices: Math.floor(kpis.overdue_amount / 10000), // Estimate count
    activeCustomers: kpis.active_customers,
    monthlyRevenue: formatCurrency(kpis.current_month_collections)
  }
})

const recentInvoices = computed(() => {
  return recentInvoicesData.value.map(invoice => ({
    customer: invoice.customer?.name || 'Unknown',
    invoiceNumber: invoice.invoice_number,
    dueDate: formatDate(invoice.due_date),
    amount: formatCurrency(invoice.total_amount),
    status: invoice.status
  }))
})

const customers = computed(() => {
  return customersData.value.map(customer => ({
    id: customer.id,
    name: customer.name
  }))
})

const invoice = ref({
  customerId: null,
  invoiceDate: new Date(),
  dueDate: new Date(),
  amount: 0,
  description: ''
})

const openInvoiceDialog = () => {
  invoice.value = {
    customerId: null,
    invoiceDate: new Date(),
    dueDate: new Date(),
    amount: 0,
    description: ''
  }
  invoiceDialog.value = true
}

const createInvoice = async () => {
  try {
    await invoiceService.createInvoice({
      customer_id: invoice.value.customerId,
      invoice_date: invoice.value.invoiceDate.toISOString().split('T')[0],
      due_date: invoice.value.dueDate.toISOString().split('T')[0],
      total_amount: invoice.value.amount,
      description: invoice.value.description
    })
    
    invoiceDialog.value = false
    toast.add({ severity: 'success', summary: 'Success', detail: 'Invoice created successfully', life: 3000 })
    await loadData() // Refresh data
  } catch (error) {
    console.error('Error creating invoice:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create invoice', life: 5000 })
  }
}

const recordPayment = () => {
  toast.add({ severity: 'info', summary: 'Info', detail: 'Payment recording feature coming soon', life: 3000 })
}

const sendReminders = () => {
  toast.add({ severity: 'info', summary: 'Info', detail: 'Reminders sent to overdue customers', life: 3000 })
}

const loadData = async () => {
  loading.value = true
  try {
    // Load dashboard analytics
    dashboardData.value = await analyticsService.getDashboardAnalytics()
    
    // Load recent invoices
    const invoicesResponse = await invoiceService.getInvoices({ limit: 5 })
    recentInvoicesData.value = invoicesResponse.invoices || []
    
    // Load customers
    const customersResponse = await customerService.getCustomers({ limit: 100 })
    customersData.value = customersResponse.customers || []
    
  } catch (error) {
    console.error('Error loading data:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load data', life: 5000 })
  } finally {
    loading.value = false
  }
}

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount || 0).replace('$', '')
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'paid': return 'success'
    case 'overdue': return 'danger'
    case 'pending': return 'warning'
    default: return 'info'
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.ar-dashboard {
  padding: 0;
}

.metric-card {
  text-align: center;
}

.quick-actions {
  display: flex;
  flex-direction: column;
}

.field {
  margin-bottom: 1rem;
}
</style>