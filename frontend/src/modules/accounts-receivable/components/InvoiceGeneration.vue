<template>
  <ResponsiveContainer>
    <Card>
      <template #header>
        <div class="flex justify-content-between align-items-center p-4">
          <h2 class="m-0">Invoice Generation</h2>
          <Button label="New Invoice" icon="pi pi-plus" @click="openInvoiceDialog" data-shortcut="create" />
        </div>
      </template>
      
      <template #content>
        <DataTable
          :value="invoices"
          :loading="loading"
          :paginator="true"
          :rows="10"
          responsiveLayout="scroll"
        >
          <Column field="invoice_number" header="Invoice #" />
          <Column field="customer_name" header="Customer" />
          <Column field="invoice_date" header="Date" />
          <Column field="due_date" header="Due Date" />
          <Column field="status" header="Status">
            <template #body="{ data }">
              <Tag :severity="getStatusSeverity(data.status)" :value="data.status.toUpperCase()" />
            </template>
          </Column>
          <Column field="total_amount" header="Total">
            <template #body="{ data }">
              {{ formatCurrency(data.total_amount) }}
            </template>
          </Column>
          <Column field="balance" header="Balance">
            <template #body="{ data }">
              {{ formatCurrency(data.balance) }}
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text p-button-sm mr-2" @click="viewInvoice(data)" />
              <Button icon="pi pi-send" class="p-button-text p-button-sm" @click="sendInvoice(data)" :disabled="data.status === 'sent'" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Invoice Dialog -->
    <Dialog v-model:visible="invoiceDialog" :header="editMode ? 'View Invoice' : 'New Invoice'" :modal="true" :style="{ width: '800px' }">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="customer">Customer *</label>
            <Dropdown id="customer" v-model="editedInvoice.customer_id" :options="customers" optionLabel="name" optionValue="id" placeholder="Select Customer" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="invoice_date">Invoice Date *</label>
            <Calendar id="invoice_date" v-model="editedInvoice.invoice_date" dateFormat="yy-mm-dd" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="due_date">Due Date *</label>
            <Calendar id="due_date" v-model="editedInvoice.due_date" dateFormat="yy-mm-dd" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="reference">Reference</label>
            <InputText id="reference" v-model="editedInvoice.reference" class="w-full" />
          </div>
        </div>
      </div>

      <!-- Line Items -->
      <h3 class="mb-4">Line Items</h3>
      <div v-for="(item, index) in editedInvoice.line_items" :key="index" class="grid mb-3">
        <div class="col-12 md:col-4">
          <div class="field">
            <label>Description *</label>
            <InputText v-model="item.description" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-2">
          <div class="field">
            <label>Quantity</label>
            <InputNumber v-model="item.quantity" class="w-full" @input="calculateLineAmount(index)" />
          </div>
        </div>
        <div class="col-12 md:col-2">
          <div class="field">
            <label>Unit Price</label>
            <InputNumber v-model="item.unit_price" mode="currency" currency="USD" class="w-full" @input="calculateLineAmount(index)" />
          </div>
        </div>
        <div class="col-12 md:col-2">
          <div class="field">
            <label>Amount</label>
            <InputNumber v-model="item.amount" mode="currency" currency="USD" class="w-full" :disabled="true" />
          </div>
        </div>
        <div class="col-12 md:col-2">
          <div class="field">
            <label>&nbsp;</label>
            <Button icon="pi pi-trash" severity="danger" class="p-button-outlined" @click="removeLineItem(index)" />
          </div>
        </div>
      </div>
      
      <Button label="Add Line Item" icon="pi pi-plus" class="p-button-outlined mb-4" @click="addLineItem" />

      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label for="notes">Notes</label>
            <Textarea id="notes" v-model="editedInvoice.notes" rows="2" class="w-full" />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="invoiceDialog = false" data-shortcut="close" />
        <Button label="Save" icon="pi pi-check" @click="saveInvoice" :disabled="!editedInvoice.customer_id" data-shortcut="save" />
      </template>
    </Dialog>
  </ResponsiveContainer>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const loading = ref(false)
const invoiceDialog = ref(false)
const editMode = ref(false)

const invoices = ref([
  {
    id: '1',
    invoice_number: 'INV-1001',
    customer_name: 'ABC Corporation',
    invoice_date: '2024-01-15',
    due_date: '2024-02-14',
    status: 'sent',
    total_amount: 5000,
    balance: 5000
  }
])

const customers = ref([
  { id: '1', name: 'ABC Corporation' },
  { id: '2', name: 'XYZ Company' }
])

const editedInvoice = ref({
  customer_id: '',
  invoice_date: new Date(),
  due_date: new Date(),
  reference: '',
  notes: '',
  line_items: []
})

const openInvoiceDialog = () => {
  editMode.value = false
  editedInvoice.value = {
    customer_id: '',
    invoice_date: new Date(),
    due_date: new Date(),
    reference: '',
    notes: '',
    line_items: [{ description: '', quantity: 1, unit_price: 0, amount: 0 }]
  }
  invoiceDialog.value = true
}

const addLineItem = () => {
  editedInvoice.value.line_items.push({
    description: '',
    quantity: 1,
    unit_price: 0,
    amount: 0
  })
}

const removeLineItem = (index: number) => {
  editedInvoice.value.line_items.splice(index, 1)
}

const calculateLineAmount = (index: number) => {
  const item = editedInvoice.value.line_items[index]
  item.amount = (parseFloat(item.quantity) || 0) * (parseFloat(item.unit_price) || 0)
}

const saveInvoice = () => {
  const subtotal = editedInvoice.value.line_items.reduce((sum, item) => sum + item.amount, 0)
  const tax = subtotal * 0.08
  const total = subtotal + tax

  invoices.value.push({
    ...editedInvoice.value,
    id: Date.now().toString(),
    invoice_number: `INV-${1000 + invoices.value.length + 1}`,
    customer_name: customers.value.find(c => c.id === editedInvoice.value.customer_id)?.name,
    status: 'draft',
    total_amount: total,
    balance: total
  })
  invoiceDialog.value = false
}

const viewInvoice = (invoice: any) => {
  console.log('View invoice:', invoice)
}

const sendInvoice = (invoice: any) => {
  invoice.status = 'sent'
}

const getStatusSeverity = (status: string) => {
  const severities = {
    draft: 'info',
    sent: 'warning',
    paid: 'success',
    overdue: 'danger'
  }
  return severities[status] || 'info'
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}
</script>