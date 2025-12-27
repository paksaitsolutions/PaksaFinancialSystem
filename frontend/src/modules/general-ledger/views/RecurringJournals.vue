<template>
  <div class="recurring-journals-container">
    <div class="recurring-journals">
      <div class="flex justify-content-between align-items-center mb-4">
        <div>
          <h1 class="page-title">Recurring Journal Entries</h1>
          <Breadcrumb :home="home" :model="breadcrumbItems" />
        </div>
        <Button 
          icon="pi pi-plus" 
          label="New Recurring Entry" 
          @click="showDialog = true"
        />
      </div>

    <!-- Filters -->
    <Card class="mb-4">
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-3">
            <span class="p-input-icon-left w-full">
              <i class="pi pi-search" />
              <InputText 
                v-model="filters.search" 
                placeholder="Search entries..." 
                class="w-full"
                @keyup.enter="loadData"
              />
            </span>
          </div>
          <div class="col-12 md:col-2">
            <Dropdown 
              v-model="filters.status" 
              :options="statusOptions" 
              optionLabel="label" 
              optionValue="value"
              placeholder="All Statuses" 
              class="w-full"
            />
          </div>
          <div class="col-12 md:col-2">
            <Dropdown 
              v-model="filters.frequency" 
              :options="frequencyOptions" 
              optionLabel="label" 
              optionValue="value"
              placeholder="All Frequencies" 
              class="w-full"
            />
          </div>
          <div class="col-12 md:col-2">
            <div class="field-checkbox">
              <Checkbox v-model="filters.includeInactive" :binary="true" />
              <label>Include Inactive</label>
            </div>
          </div>
          <div class="col-12 md:col-3 flex gap-2">
            <Button 
              icon="pi pi-filter" 
              label="Apply" 
              @click="loadData" 
              :loading="loading"
            />
            <Button 
              icon="pi pi-filter-slash" 
              label="Reset" 
              class="p-button-outlined" 
              @click="resetFilters"
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- Data Table -->
    <Card>
      <template #content>
        <DataTable 
          :value="recurringJournals" 
          :loading="loading"
          :paginator="true" 
          :rows="10"
          :totalRecords="totalRecords"
          :lazy="true"
          @page="onPage"
          @sort="onSort"
          class="p-datatable-sm"
          responsiveLayout="scroll"
        >
          <template #empty>No recurring journal entries found.</template>
          <Column field="name" header="Name" :sortable="true">
            <template #body="{ data }">
              <div>
                <div class="font-medium">{{ data.name }}</div>
                <div class="text-sm text-500">{{ data.description }}</div>
              </div>
            </template>
          </Column>
          <Column field="frequency" header="Frequency" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.frequency" :severity="getFrequencySeverity(data.frequency)" />
            </template>
          </Column>
          <Column field="nextRunDate" header="Next Run" :sortable="true">
            <template #body="{ data }">
              <div>
                <div>{{ formatDate(data.nextRunDate) }}</div>
                <div class="text-sm" :class="getNextRunClass(data.nextRunDate)">
                  {{ getNextRunText(data.nextRunDate) }}
                </div>
              </div>
            </template>
          </Column>
          <Column field="amount" header="Amount" :sortable="true">
            <template #body="{ data }">
              <div class="text-right font-medium">
                {{ formatCurrency(data.amount) }}
              </div>
            </template>
          </Column>
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column field="lastRun" header="Last Run" :sortable="true">
            <template #body="{ data }">
              {{ data.lastRun ? formatDate(data.lastRun) : 'Never' }}
            </template>
          </Column>
          <Column header="Actions" style="width: 12rem">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-text p-button-sm" 
                  @click="viewEntry(data)"
                  v-tooltip.top="'View'"
                />
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-sm p-button-warning" 
                  @click="editEntry(data)"
                  v-tooltip.top="'Edit'"
                />
                <Button 
                  icon="pi pi-play" 
                  class="p-button-text p-button-sm p-button-success" 
                  @click="runNow(data)"
                  v-tooltip.top="'Run Now'"
                  :disabled="data.status !== 'active'"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-danger" 
                  @click="confirmDelete(data)"
                  v-tooltip.top="'Delete'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Create/Edit Dialog -->
    <Dialog 
      v-model:visible="showDialog" 
      :style="{width: '800px'}" 
      :header="editing ? 'Edit Recurring Entry' : 'New Recurring Entry'" 
      :modal="true"
      class="p-fluid"
    >
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="name">Name <span class="text-red-500">*</span></label>
            <InputText 
              id="name" 
              v-model="entry.name" 
              :class="{'p-invalid': submitted && !entry.name}"
            />
            <small class="p-error" v-if="submitted && !entry.name">Name is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="frequency">Frequency <span class="text-red-500">*</span></label>
            <Dropdown 
              id="frequency" 
              v-model="entry.frequency" 
              :options="frequencyOptions" 
              optionLabel="label" 
              optionValue="value"
              :class="{'p-invalid': submitted && !entry.frequency}"
            />
            <small class="p-error" v-if="submitted && !entry.frequency">Frequency is required.</small>
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="description">Description</label>
            <Textarea id="description" v-model="entry.description" rows="2" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="startDate">Start Date <span class="text-red-500">*</span></label>
            <Calendar 
              id="startDate" 
              v-model="entry.startDate" 
              :showIcon="true"
              :class="{'p-invalid': submitted && !entry.startDate}"
            />
            <small class="p-error" v-if="submitted && !entry.startDate">Start date is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="endDate">End Date</label>
            <Calendar 
              id="endDate" 
              v-model="entry.endDate" 
              :showIcon="true"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Journal Entry Lines <span class="text-red-500">*</span></label>
            <DataTable :value="entry.lines" class="p-datatable-sm">
              <template #empty>No journal lines added.</template>
              <Column field="account" header="Account">
                <template #body="{ data, index }">
                  <Dropdown 
                    v-model="data.account" 
                    :options="accounts" 
                    optionLabel="name" 
                    optionValue="code"
                    placeholder="Select Account"
                    class="w-full"
                  />
                </template>
              </Column>
              <Column field="description" header="Description">
                <template #body="{ data }">
                  <InputText v-model="data.description" class="w-full" />
                </template>
              </Column>
              <Column field="debit" header="Debit">
                <template #body="{ data }">
                  <InputNumber 
                    v-model="data.debit" 
                    mode="currency" 
                    currency="USD" 
                    class="w-full"
                  />
                </template>
              </Column>
              <Column field="credit" header="Credit">
                <template #body="{ data }">
                  <InputNumber 
                    v-model="data.credit" 
                    mode="currency" 
                    currency="USD" 
                    class="w-full"
                  />
                </template>
              </Column>
              <Column header="Actions" style="width: 4rem">
                <template #body="{ index }">
                  <Button 
                    icon="pi pi-trash" 
                    class="p-button-text p-button-sm p-button-danger" 
                    @click="removeLine(index)"
                  />
                </template>
              </Column>
            </DataTable>
            <Button 
              icon="pi pi-plus" 
              label="Add Line" 
              class="p-button-outlined mt-2" 
              @click="addLine"
            />
            <small class="p-error" v-if="submitted && entry.lines.length === 0">At least one journal line is required.</small>
          </div>
        </div>
      </div>
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="hideDialog"
        />
        <Button 
          :label="editing ? 'Update' : 'Create'" 
          icon="pi pi-check" 
          @click="saveEntry" 
          :loading="saving"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation -->
    <Dialog 
      v-model:visible="showDeleteDialog" 
      :style="{width: '450px'}" 
      header="Confirm Delete" 
      :modal="true"
    >
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to delete <b>{{ selectedEntry?.name }}</b>?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="showDeleteDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="deleteEntry"
          :loading="deleting"
        />
      </template>
    </Dialog>

    <!-- Run Now Dialog -->
    <Dialog 
      v-model:visible="showRunDialog" 
      :style="{width: '500px'}" 
      header="Run Recurring Entry" 
      :modal="true"
    >
      <div class="mb-4">
        <p>Run recurring entry <strong>{{ selectedEntry?.name }}</strong> now?</p>
        <p class="text-600">This will create a journal entry for the current period.</p>
      </div>
      <div class="field-checkbox">
        <Checkbox v-model="previewBeforeRun" :binary="true" />
        <label>Preview before posting</label>
      </div>
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="showRunDialog = false"
        />
        <Button 
          label="Run Now" 
          icon="pi pi-play" 
          @click="executeRun" 
          :loading="running"
        />
      </template>
    </Dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

interface JournalLine {
  account: string
  description: string
  debit: number
  credit: number
}

interface RecurringJournal {
  id: string
  name: string
  description: string
  frequency: string
  startDate: Date
  endDate?: Date
  nextRunDate: Date
  lastRun?: Date
  amount: number
  status: string
  lines: JournalLine[]
}

const toast = useToast()
const confirm = useConfirm()

const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const running = ref(false)
const showDialog = ref(false)
const showDeleteDialog = ref(false)
const showRunDialog = ref(false)
const editing = ref(false)
const submitted = ref(false)
const previewBeforeRun = ref(true)

const recurringJournals = ref<RecurringJournal[]>([])
const selectedEntry = ref<RecurringJournal | null>(null)
const totalRecords = ref(0)

const entry = ref<RecurringJournal>({
  id: '',
  name: '',
  description: '',
  frequency: '',
  startDate: new Date(),
  endDate: undefined,
  nextRunDate: new Date(),
  amount: 0,
  status: 'active',
  lines: []
})

const filters = ref({
  search: '',
  status: null,
  frequency: null,
  includeInactive: false
})

const accounts = ref([
  { name: '1000 - Cash', code: '1000' },
  { name: '1200 - Accounts Receivable', code: '1200' },
  { name: '2000 - Accounts Payable', code: '2000' },
  { name: '4000 - Revenue', code: '4000' },
  { name: '5000 - Expenses', code: '5000' }
])

const statusOptions = ref([
  { label: 'Active', value: 'active' },
  { label: 'Paused', value: 'paused' },
  { label: 'Completed', value: 'completed' },
  { label: 'Cancelled', value: 'cancelled' }
])

const frequencyOptions = ref([
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' },
  { label: 'Quarterly', value: 'quarterly' },
  { label: 'Annually', value: 'annually' }
])

const home = ref({ icon: 'pi pi-home', to: '/' })
const breadcrumbItems = ref([
  { label: 'General Ledger', to: '/gl' },
  { label: 'Recurring Journals' }
])

const loadData = async () => {
  loading.value = true
  try {
    // Mock data
    recurringJournals.value = [
      {
        id: '1',
        name: 'Monthly Rent',
        description: 'Office rent payment',
        frequency: 'monthly',
        startDate: new Date('2024-01-01'),
        nextRunDate: new Date('2024-12-01'),
        lastRun: new Date('2024-11-01'),
        amount: 2500,
        status: 'active',
        lines: [
          { account: '5000', description: 'Rent Expense', debit: 2500, credit: 0 },
          { account: '1000', description: 'Cash Payment', debit: 0, credit: 2500 }
        ]
      },
      {
        id: '2',
        name: 'Quarterly Insurance',
        description: 'Insurance premium payment',
        frequency: 'quarterly',
        startDate: new Date('2024-01-01'),
        nextRunDate: new Date('2025-01-01'),
        lastRun: new Date('2024-10-01'),
        amount: 1200,
        status: 'active',
        lines: [
          { account: '5000', description: 'Insurance Expense', debit: 1200, credit: 0 },
          { account: '1000', description: 'Cash Payment', debit: 0, credit: 1200 }
        ]
      }
    ]
    totalRecords.value = recurringJournals.value.length
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = {
    search: '',
    status: null,
    frequency: null,
    includeInactive: false
  }
  loadData()
}

const viewEntry = (data: RecurringJournal) => {
  entry.value = { ...data }
  editing.value = false
  showDialog.value = true
}

const editEntry = (data: RecurringJournal) => {
  entry.value = { ...data }
  editing.value = true
  showDialog.value = true
}

const hideDialog = () => {
  showDialog.value = false
  submitted.value = false
  editing.value = false
  entry.value = {
    id: '',
    name: '',
    description: '',
    frequency: '',
    startDate: new Date(),
    endDate: undefined,
    nextRunDate: new Date(),
    amount: 0,
    status: 'active',
    lines: []
  }
}

const addLine = () => {
  entry.value.lines.push({
    account: '',
    description: '',
    debit: 0,
    credit: 0
  })
}

const removeLine = (index: number) => {
  entry.value.lines.splice(index, 1)
}

const saveEntry = async () => {
  submitted.value = true
  if (!entry.value.name || !entry.value.frequency || !entry.value.startDate || entry.value.lines.length === 0) {
    return
  }

  saving.value = true
  try {
    if (editing.value) {
      toast.add({ severity: 'success', summary: 'Success', detail: 'Recurring entry updated' })
    } else {
      entry.value.id = Date.now().toString()
      recurringJournals.value.push({ ...entry.value })
      toast.add({ severity: 'success', summary: 'Success', detail: 'Recurring entry created' })
    }
    hideDialog()
    loadData()
  } finally {
    saving.value = false
  }
}

const confirmDelete = (data: RecurringJournal) => {
  selectedEntry.value = data
  showDeleteDialog.value = true
}

const deleteEntry = async () => {
  deleting.value = true
  try {
    recurringJournals.value = recurringJournals.value.filter(j => j.id !== selectedEntry.value?.id)
    showDeleteDialog.value = false
    toast.add({ severity: 'success', summary: 'Success', detail: 'Recurring entry deleted' })
  } finally {
    deleting.value = false
  }
}

const runNow = (data: RecurringJournal) => {
  selectedEntry.value = data
  showRunDialog.value = true
}

const executeRun = async () => {
  running.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 2000))
    showRunDialog.value = false
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: `Journal entry created for ${selectedEntry.value?.name}` 
    })
    loadData()
  } finally {
    running.value = false
  }
}

const onPage = (event: any) => {
  loadData()
}

const onSort = (event: any) => {
  loadData()
}

const formatDate = (date: Date | string) => {
  return new Date(date).toLocaleDateString()
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'paused': return 'warning'
    case 'completed': return 'info'
    case 'cancelled': return 'danger'
    default: return 'secondary'
  }
}

const getFrequencySeverity = (frequency: string) => {
  switch (frequency) {
    case 'daily': return 'info'
    case 'weekly': return 'success'
    case 'monthly': return 'warning'
    case 'quarterly': return 'help'
    case 'annually': return 'danger'
    default: return 'secondary'
  }
}

const getNextRunClass = (date: Date | string) => {
  const nextRun = new Date(date)
  const today = new Date()
  const diffDays = Math.ceil((nextRun.getTime() - today.getTime()) / (1000 * 3600 * 24))
  
  if (diffDays < 0) return 'text-red-600'
  if (diffDays <= 7) return 'text-orange-600'
  return 'text-green-600'
}

const getNextRunText = (date: Date | string) => {
  const nextRun = new Date(date)
  const today = new Date()
  const diffDays = Math.ceil((nextRun.getTime() - today.getTime()) / (1000 * 3600 * 24))
  
  if (diffDays < 0) return 'Overdue'
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Tomorrow'
  if (diffDays <= 7) return `In ${diffDays} days`
  return ''
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.recurring-journals-container {
  min-height: 100vh;
  width: 100%;
  background-color: var(--surface-50, #f8fafc);
  position: relative;
}

.recurring-journals {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-color, #1e293b);
  margin: 0 0 0.5rem 0;
  line-height: 1.2;
}

/* Ensure proper spacing and layout */
:deep(.p-card) {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--surface-200, #e2e8f0);
  margin-bottom: 1rem;
}

:deep(.p-datatable) {
  background: white;
  border-radius: 8px;
}

:deep(.p-datatable .p-datatable-wrapper) {
  border-radius: 8px;
}

/* Grid system fixes */
.grid {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -0.5rem;
  width: 100%;
}

.grid > [class*="col-"] {
  padding: 0 0.5rem;
  box-sizing: border-box;
}

/* Flex utilities */
.flex {
  display: flex;
}

.justify-content-between {
  justify-content: space-between;
}

.align-items-center {
  align-items: center;
}

.gap-2 {
  gap: 0.5rem;
}

.gap-1 {
  gap: 0.25rem;
}

.mb-4 {
  margin-bottom: 1.5rem;
}

.mb-3 {
  margin-bottom: 1rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.w-full {
  width: 100%;
}

/* Text utilities */
.font-medium {
  font-weight: 500;
}

.text-sm {
  font-size: 0.875rem;
}

.text-right {
  text-align: right;
}

/* Color utilities */
.text-500 {
  color: var(--text-color-secondary, #64748b);
}

.text-red-500 {
  color: #ef4444;
}

.text-red-600 {
  color: #dc2626;
}

.text-orange-600 {
  color: #ea580c;
}

.text-green-600 {
  color: #16a34a;
}

.text-600 {
  color: var(--text-color-secondary, #64748b);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .recurring-journals {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .flex.justify-content-between {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .grid > [class*="col-"] {
    flex: 0 0 100%;
    max-width: 100%;
  }
}

/* Large screens */
@media (min-width: 768px) {
  .col-12 { flex: 0 0 100%; max-width: 100%; }
  .col-6 { flex: 0 0 50%; max-width: 50%; }
  .col-4 { flex: 0 0 33.333%; max-width: 33.333%; }
  .col-3 { flex: 0 0 25%; max-width: 25%; }
  .col-2 { flex: 0 0 16.667%; max-width: 16.667%; }
  
  .md\:col-6 { flex: 0 0 50%; max-width: 50%; }
  .md\:col-4 { flex: 0 0 33.333%; max-width: 33.333%; }
  .md\:col-3 { flex: 0 0 25%; max-width: 25%; }
  .md\:col-2 { flex: 0 0 16.667%; max-width: 16.667%; }
}
</style>