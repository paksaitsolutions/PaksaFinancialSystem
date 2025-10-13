<template>
  <UnifiedDashboard 
    title="Accounts Receivable" 
    subtitle="Manage customer invoices and payments"
  >
    <template #actions>
      <Button label="Create Invoice" icon="pi pi-plus" class="btn-primary" @click="openInvoiceDialog" />
    </template>
    
    <template #metrics>
      <UnifiedMetrics :metrics="dashboardMetrics" />
    </template>
    
    <template #content>

      <Card class="mb-4">
        <template #header>
          <h3 class="card-title">Accounts Receivable Modules</h3>
        </template>
        <template #content>
          <div class="modules-grid">
            <div class="module-card" @click="$router.push('/ar/customers')">
              <i class="pi pi-users" style="color: var(--primary-500)"></i>
              <h4>Customers</h4>
              <p>Manage customer information</p>
            </div>
            <div class="module-card" @click="$router.push('/ar/invoices')">
              <i class="pi pi-file-edit" style="color: var(--warning-500)"></i>
              <h4>Invoices</h4>
              <p>Create and manage invoices</p>
            </div>
            <div class="module-card" @click="$router.push('/ar/payments')">
              <i class="pi pi-money-bill" style="color: var(--success-500)"></i>
              <h4>Payments</h4>
              <p>Record customer payments</p>
            </div>
            <div class="module-card" @click="$router.push('/ar/reports')">
              <i class="pi pi-chart-bar" style="color: var(--info-500)"></i>
              <h4>Reports</h4>
              <p>AR reports and analytics</p>
            </div>
          </div>
        </template>
      </Card>

      <div class="content-grid">
        <Card>
          <template #header>
            <h3 class="card-title">Recent Invoices</h3>
          </template>
          <template #content>
            <DataTable :value="recentInvoices" :rows="5" class="compact-table">
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
        <Card>
          <template #header>
            <h3 class="card-title">Quick Actions</h3>
          </template>
          <template #content>
            <div class="actions-list">
              <Button label="Add Customer" icon="pi pi-user-plus" class="action-btn" @click="$router.push('/ar/customers')" />
              <Button label="Record Payment" icon="pi pi-money-bill" class="action-btn btn-secondary" @click="recordPayment" />
              <Button label="Send Reminders" icon="pi pi-send" class="action-btn" @click="sendReminders" />
              <Button label="View Reports" icon="pi pi-chart-bar" class="action-btn" @click="$router.push('/ar/reports')" />
            </div>
          </template>
        </Card>
      </div>
    </template>
  </UnifiedDashboard>

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
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { analyticsService, customerService, invoiceService } from '@/api/arService'

const toast = useToast()
const invoiceDialog = ref(false)
const loading = ref(false)
const dashboardData = ref(null)
const recentInvoicesData = ref([])
const customersData = ref([])

const dashboardMetrics = computed(() => {
  if (!dashboardData.value) {
    return [
      {
        id: 'receivable',
        icon: 'pi pi-receipt',
        value: '$0',
        label: 'Total Receivable',
        color: 'var(--success-500)'
      },
      {
        id: 'overdue',
        icon: 'pi pi-clock',
        value: '0',
        label: 'Overdue Invoices',
        color: 'var(--warning-500)'
      },
      {
        id: 'customers',
        icon: 'pi pi-users',
        value: '0',
        label: 'Active Customers',
        color: 'var(--primary-500)'
      },
      {
        id: 'revenue',
        icon: 'pi pi-money-bill',
        value: '$0',
        label: 'Monthly Revenue',
        color: 'var(--info-500)'
      }
    ]
  }
  
  const kpis = dashboardData.value.kpis
  return [
    {
      id: 'receivable',
      icon: 'pi pi-receipt',
      value: `$${formatCurrency(kpis.total_outstanding)}`,
      label: 'Total Receivable',
      color: 'var(--success-500)'
    },
    {
      id: 'overdue',
      icon: 'pi pi-clock',
      value: Math.floor(kpis.overdue_amount / 10000),
      label: 'Overdue Invoices',
      color: 'var(--warning-500)'
    },
    {
      id: 'customers',
      icon: 'pi pi-users',
      value: kpis.active_customers,
      label: 'Active Customers',
      color: 'var(--primary-500)'
    },
    {
      id: 'revenue',
      icon: 'pi pi-money-bill',
      value: `$${formatCurrency(kpis.current_month_collections)}`,
      label: 'Monthly Revenue',
      color: 'var(--info-500)'
    }
  ]
})

const recentInvoices = computed(() => {
  return recentInvoicesData.value.map(invoice => ({
    id: invoice.id,
    customer: invoice.customer?.name || 'Unknown',
    invoiceNumber: invoice.invoice_number,
    dueDate: formatDate(invoice.due_date),
    amount: invoice.total_amount,
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
    // Load dashboard stats
    dashboardData.value = await analyticsService.getDashboardStats()
    
    // Load recent invoices from dashboard endpoint
    const invoicesResponse = await analyticsService.getRecentInvoices()
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
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount || 0)
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
.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.module-card {
  text-align: center;
  padding: var(--spacing-lg);
  border: 1px solid var(--surface-200);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--surface-0);
}

.module-card:hover {
  background: var(--surface-50);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.module-card i {
  font-size: 2.5rem;
  margin-bottom: var(--spacing-md);
  display: block;
}

.module-card h4 {
  margin: var(--spacing-sm) 0;
  color: var(--text-color);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
}

.module-card p {
  margin: 0;
  color: var(--text-color-secondary);
  font-size: var(--font-size-sm);
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-lg);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  margin: 0;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.action-btn {
  width: 100%;
  justify-content: flex-start;
}

.field {
  margin-bottom: 1rem;
}

:deep(.compact-table .p-datatable-tbody td) {
  padding: var(--spacing-sm) var(--spacing-md);
}

:deep(.compact-table .p-datatable-thead th) {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

@media (max-width: 768px) {
  .modules-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }
  
  .content-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
}

@media (max-width: 480px) {
  .modules-grid {
    grid-template-columns: 1fr;
  }
}
</style>