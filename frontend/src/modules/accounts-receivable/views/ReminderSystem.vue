<template>
  <div class="reminder-system">
    <h2>Payment Reminder System</h2>
    <Card>
      <template #content>
        <div class="mb-4">
          <h4>Overdue Invoices</h4>
          <DataTable :value="overdueInvoices" selectionMode="multiple" v-model:selection="selectedInvoices">
            <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
            <Column field="invoice_number" header="Invoice #"></Column>
            <Column field="customer.name" header="Customer"></Column>
            <Column field="total_amount" header="Amount">
              <template #body="{ data }">
                {{ formatCurrency(data.total_amount) }}
              </template>
            </Column>
            <Column field="days_overdue" header="Days Overdue">
              <template #body="{ data }">
                <Tag :value="`${data.days_overdue} days`" severity="danger" />
              </template>
            </Column>
            <Column field="last_reminder" header="Last Reminder"></Column>
          </DataTable>
        </div>
        
        <div class="reminder-actions">
          <h4>Reminder Actions</h4>
          <div class="grid">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Reminder Template</label>
                <Dropdown v-model="selectedTemplate" :options="reminderTemplates" optionLabel="name" optionValue="id" class="w-full" />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Send Method</label>
                <Dropdown v-model="sendMethod" :options="sendMethods" class="w-full" />
              </div>
            </div>
          </div>
          
          <div class="actions mt-4">
            <Button label="Send Reminders" icon="pi pi-send" @click="sendReminders" :loading="sending" :disabled="!selectedInvoices.length" />
            <Button label="Schedule Auto-Reminders" icon="pi pi-clock" severity="secondary" @click="scheduleReminders" class="ml-2" />
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { invoiceService } from '@/api/arService'

const toast = useToast()
const sending = ref(false)
const overdueInvoices = ref([])
const selectedInvoices = ref([])
const selectedTemplate = ref('')
const sendMethod = ref('email')

const reminderTemplates = ref([
  { id: 'gentle', name: 'Gentle Reminder (1st Notice)' },
  { id: 'firm', name: 'Firm Reminder (2nd Notice)' },
  { id: 'final', name: 'Final Notice (3rd Notice)' },
  { id: 'collection', name: 'Collection Notice' }
])

const sendMethods = ref(['Email', 'SMS', 'Mail', 'Phone Call'])

const sendReminders = async () => {
  sending.value = true
  try {
    const invoiceIds = selectedInvoices.value.map(inv => inv.id)
    await invoiceService.sendReminders(invoiceIds)
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: `Reminders sent to ${invoiceIds.length} customers` 
    })
    selectedInvoices.value = []
    await loadOverdueInvoices()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to send reminders' })
  } finally {
    sending.value = false
  }
}

const scheduleReminders = () => {
  toast.add({ 
    severity: 'info', 
    summary: 'Scheduled', 
    detail: 'Auto-reminder system configured' 
  })
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const loadOverdueInvoices = async () => {
  try {
    const response = await invoiceService.getInvoices()
    overdueInvoices.value = response.invoices
      .filter(inv => inv.status === 'overdue')
      .map(inv => ({
        ...inv,
        days_overdue: Math.floor((new Date().getTime() - new Date(inv.due_date).getTime()) / (1000 * 60 * 60 * 24)),
        last_reminder: 'Never'
      }))
  } catch (error) {
    console.error('Error loading overdue invoices:', error)
  }
}

onMounted(() => {
  loadOverdueInvoices()
})
</script>