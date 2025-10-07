<template>
  <div class="collections-management">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Collections Management</h1>
        <Breadcrumb :home="home" :model="breadcrumbItems" class="mb-4" />
      </div>
      <div>
        <Button 
          label="New Collection" 
          icon="pi pi-plus" 
          class="p-button-success" 
          @click="showNewCollectionDialog" 
        />
      </div>
    </div>

    <!-- Collections List -->
    <div class="grid">
      <div class="col-12">
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3>Collections</h3>
              <div class="flex gap-2">
                <Dropdown 
                  v-model="selectedStatus" 
                  :options="statusOptions" 
                  optionLabel="label" 
                  optionValue="value" 
                  placeholder="Filter by Status"
                  @change="filterCollections"
                />
                <Button 
                  icon="pi pi-refresh" 
                  class="p-button-text" 
                  @click="loadCollections" 
                  :loading="loading"
                />
              </div>
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="collections" 
              :paginator="true" 
              :rows="10"
              :loading="loading"
              :rowsPerPageOptions="[5,10,25,50]"
              class="p-datatable-sm"
            >
              <template #empty>No collections found.</template>
              <Column field="customer_name" header="Customer" :sortable="true" />
              <Column field="invoice_number" header="Invoice" :sortable="true" />
              <Column field="amount_due" header="Amount Due" :sortable="true">
                <template #body="{ data }">
                  ${{ data.amount_due.toLocaleString() }}
                </template>
              </Column>
              <Column field="days_overdue" header="Days Overdue" :sortable="true" />
              <Column field="status" header="Status" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column field="priority" header="Priority" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.priority" :severity="getPrioritySeverity(data.priority)" />
                </template>
              </Column>
              <Column header="Actions" style="width: 12rem">
                <template #body="{ data }">
                  <div class="flex gap-2">
                    <Button 
                      icon="pi pi-eye" 
                      class="p-button-text p-button-sm" 
                      @click="viewCollection(data)" 
                      v-tooltip.top="'View Details'"
                    />
                    <Button 
                      icon="pi pi-pencil" 
                      class="p-button-text p-button-sm p-button-warning" 
                      @click="editCollection(data)" 
                      v-tooltip.top="'Edit Collection'"
                    />
                    <Button 
                      icon="pi pi-phone" 
                      class="p-button-text p-button-sm p-button-info" 
                      @click="addActivity(data, 'call')" 
                      v-tooltip.top="'Log Call'"
                    />
                    <Button 
                      icon="pi pi-envelope" 
                      class="p-button-text p-button-sm p-button-secondary" 
                      @click="addActivity(data, 'email')" 
                      v-tooltip.top="'Log Email'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- Collection Dialog -->
    <Dialog 
      v-model:visible="collectionDialog" 
      :style="{width: '650px'}" 
      :header="editing ? 'Edit Collection' : 'New Collection'" 
      :modal="true"
      class="p-fluid"
    >
      <div class="field">
        <label for="customer">Customer <span class="text-red-500">*</span></label>
        <Dropdown 
          id="customer" 
          v-model="collection.customer_id" 
          :options="customers" 
          optionLabel="name" 
          optionValue="id" 
          placeholder="Select Customer"
          :class="{'p-invalid': submitted && !collection.customer_id}"
        />
        <small class="p-error" v-if="submitted && !collection.customer_id">Customer is required.</small>
      </div>

      <div class="field">
        <label for="invoice">Invoice <span class="text-red-500">*</span></label>
        <Dropdown 
          id="invoice" 
          v-model="collection.invoice_id" 
          :options="invoices" 
          optionLabel="number" 
          optionValue="id" 
          placeholder="Select Invoice"
          :class="{'p-invalid': submitted && !collection.invoice_id}"
        />
        <small class="p-error" v-if="submitted && !collection.invoice_id">Invoice is required.</small>
      </div>

      <div class="field">
        <label for="amountDue">Amount Due <span class="text-red-500">*</span></label>
        <InputNumber 
          id="amountDue" 
          v-model="collection.amount_due" 
          mode="currency" 
          currency="USD" 
          :class="{'p-invalid': submitted && !collection.amount_due}"
        />
        <small class="p-error" v-if="submitted && !collection.amount_due">Amount due is required.</small>
      </div>

      <div class="field">
        <label for="priority">Priority</label>
        <Dropdown 
          id="priority" 
          v-model="collection.priority" 
          :options="priorityOptions" 
          optionLabel="label" 
          optionValue="value"
        />
      </div>

      <div class="field">
        <label for="notes">Notes</label>
        <Textarea id="notes" v-model="collection.notes" rows="3" />
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="hideDialog" 
        />
        <Button 
          :label="editing ? 'Update' : 'Save'" 
          icon="pi pi-check" 
          class="p-button-text" 
          @click="saveCollection" 
          :loading="submitting"
        />
      </template>
    </Dialog>

    <!-- Activity Dialog -->
    <Dialog 
      v-model:visible="activityDialog" 
      :style="{width: '500px'}" 
      header="Log Activity" 
      :modal="true"
      class="p-fluid"
    >
      <div class="field">
        <label for="activityType">Activity Type</label>
        <Dropdown 
          id="activityType" 
          v-model="activity.activity_type" 
          :options="activityTypes" 
          optionLabel="label" 
          optionValue="value"
        />
      </div>

      <div class="field">
        <label for="description">Description</label>
        <Textarea id="description" v-model="activity.description" rows="3" />
      </div>

      <div class="field" v-if="activity.activity_type === 'payment'">
        <label for="amount">Amount</label>
        <InputNumber 
          id="amount" 
          v-model="activity.amount" 
          mode="currency" 
          currency="USD" 
        />
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="activityDialog = false" 
        />
        <Button 
          label="Save" 
          icon="pi pi-check" 
          class="p-button-text" 
          @click="saveActivity" 
          :loading="submitting"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

// State
const loading = ref(false)
const submitting = ref(false)
const collectionDialog = ref(false)
const activityDialog = ref(false)
const editing = ref(false)
const submitted = ref(false)
const selectedStatus = ref(null)

const collections = ref([])
const customers = ref([])
const invoices = ref([])

const collection = ref({
  id: null,
  customer_id: null,
  invoice_id: null,
  amount_due: 0,
  priority: 'medium',
  notes: ''
})

const activity = ref({
  collection_id: null,
  activity_type: 'call',
  description: '',
  amount: null
})

const statusOptions = ref([
  { label: 'All', value: null },
  { label: 'Pending', value: 'pending' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Collected', value: 'collected' },
  { label: 'Written Off', value: 'written_off' }
])

const priorityOptions = ref([
  { label: 'Low', value: 'low' },
  { label: 'Medium', value: 'medium' },
  { label: 'High', value: 'high' },
  { label: 'Urgent', value: 'urgent' }
])

const activityTypes = ref([
  { label: 'Phone Call', value: 'call' },
  { label: 'Email', value: 'email' },
  { label: 'Letter', value: 'letter' },
  { label: 'Payment', value: 'payment' },
  { label: 'Note', value: 'note' }
])

const home = ref({ icon: 'pi pi-home', to: '/' })
const breadcrumbItems = ref([
  { label: 'Accounts Receivable', to: '/ar' },
  { label: 'Collections', to: '/ar/collections' }
])

// Methods
const loadCollections = async () => {
  loading.value = true
  try {
    const response = await fetch('http://localhost:8000/api/v1/ar/collections/')
    if (response.ok) {
      collections.value = await response.json()
    }
  } catch (error) {
    console.error('Error loading collections:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load collections', life: 3000 })
  } finally {
    loading.value = false
  }
}

const filterCollections = async () => {
  loading.value = true
  try {
    const url = selectedStatus.value 
      ? `http://localhost:8000/api/v1/ar/collections/?status=${selectedStatus.value}`
      : 'http://localhost:8000/api/v1/ar/collections/'
    const response = await fetch(url)
    if (response.ok) {
      collections.value = await response.json()
    }
  } catch (error) {
    console.error('Error filtering collections:', error)
  } finally {
    loading.value = false
  }
}

const showNewCollectionDialog = () => {
  collection.value = {
    id: null,
    customer_id: null,
    invoice_id: null,
    amount_due: 0,
    priority: 'medium',
    notes: ''
  }
  editing.value = false
  submitted.value = false
  collectionDialog.value = true
}

const editCollection = (data) => {
  collection.value = { ...data }
  editing.value = true
  collectionDialog.value = true
}

const viewCollection = (data) => {
  // Navigate to collection details view
  console.log('View collection:', data)
}

const addActivity = (collectionData, activityType) => {
  activity.value = {
    collection_id: collectionData.id,
    activity_type: activityType,
    description: '',
    amount: null
  }
  activityDialog.value = true
}

const hideDialog = () => {
  collectionDialog.value = false
  submitted.value = false
}

const saveCollection = async () => {
  submitted.value = true
  
  if (!collection.value.customer_id || !collection.value.invoice_id || !collection.value.amount_due) {
    return
  }
  
  submitting.value = true
  try {
    const url = editing.value 
      ? `http://localhost:8000/api/v1/ar/collections/${collection.value.id}`
      : 'http://localhost:8000/api/v1/ar/collections/'
    
    const response = await fetch(url, {
      method: editing.value ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(collection.value)
    })
    
    if (response.ok) {
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: editing.value ? 'Collection updated' : 'Collection created', 
        life: 3000 
      })
      collectionDialog.value = false
      await loadCollections()
    }
  } catch (error) {
    console.error('Error saving collection:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save collection', life: 3000 })
  } finally {
    submitting.value = false
  }
}

const saveActivity = async () => {
  submitting.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/v1/ar/collections/${activity.value.collection_id}/activities`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(activity.value)
    })
    
    if (response.ok) {
      toast.add({ severity: 'success', summary: 'Success', detail: 'Activity logged', life: 3000 })
      activityDialog.value = false
      await loadCollections()
    }
  } catch (error) {
    console.error('Error saving activity:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to log activity', life: 3000 })
  } finally {
    submitting.value = false
  }
}

const getStatusSeverity = (status) => {
  switch (status) {
    case 'collected': return 'success'
    case 'in_progress': return 'info'
    case 'pending': return 'warning'
    case 'written_off': return 'danger'
    default: return 'info'
  }
}

const getPrioritySeverity = (priority) => {
  switch (priority) {
    case 'urgent': return 'danger'
    case 'high': return 'warning'
    case 'medium': return 'info'
    case 'low': return 'success'
    default: return 'info'
  }
}

onMounted(() => {
  loadCollections()
})
</script>

<style scoped>
.collections-management {
  padding: 1rem;
}

.field {
  margin-bottom: 1.5rem;
}
</style>