<template>
  <UnifiedDashboard 
    title="Period Close" 
    subtitle="Manage period-end closing process and checklist"
  >
    <template #actions>
      <Button 
        icon="pi pi-refresh" 
        label="Refresh" 
        @click="loadData" 
        :loading="loading"
      />
    </template>
    
    <template #content>

    <!-- Current Period Status -->
    <Card class="mb-4">
      <template #header>
        <h3>Current Period Status</h3>
      </template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-6 lg:col-3">
            <div class="text-center p-3 border-round bg-blue-50">
              <i class="pi pi-calendar text-blue-600 text-3xl mb-2"></i>
              <div class="text-900 font-medium">Current Period</div>
              <div class="text-blue-600 font-bold text-xl">{{ currentPeriod }}</div>
            </div>
          </div>
          <div class="col-12 md:col-6 lg:col-3">
            <div class="text-center p-3 border-round bg-green-50">
              <i class="pi pi-check-circle text-green-600 text-3xl mb-2"></i>
              <div class="text-900 font-medium">Status</div>
              <div class="text-green-600 font-bold text-xl">{{ periodStatus }}</div>
            </div>
          </div>
          <div class="col-12 md:col-6 lg:col-3">
            <div class="text-center p-3 border-round bg-orange-50">
              <i class="pi pi-clock text-orange-600 text-3xl mb-2"></i>
              <div class="text-900 font-medium">Days Remaining</div>
              <div class="text-orange-600 font-bold text-xl">{{ daysRemaining }}</div>
            </div>
          </div>
          <div class="col-12 md:col-6 lg:col-3">
            <div class="text-center p-3 border-round bg-purple-50">
              <i class="pi pi-percentage text-purple-600 text-3xl mb-2"></i>
              <div class="text-900 font-medium">Completion</div>
              <div class="text-purple-600 font-bold text-xl">{{ completionPercentage }}%</div>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Content Grid -->
    <div class="content-grid">
      <Card>
        <template #header>
          <div class="flex justify-content-between align-items-center">
            <h3 class="card-title">Period Close Checklist</h3>
            <Dropdown 
              v-model="selectedPeriod" 
              :options="periods" 
              optionLabel="label" 
              optionValue="value" 
              placeholder="Select Period"
              @change="loadChecklist"
            />
          </div>
        </template>
        <template #content>
          <div class="checklist-items">
            <div 
              v-for="item in checklist" 
              :key="item.id"
              class="checklist-item"
              :class="getItemClass(item.status)"
            >
              <div class="flex justify-content-between align-items-start">
                <div class="flex-1">
                  <div class="flex align-items-center mb-2">
                    <Checkbox 
                      v-model="item.completed" 
                      :binary="true" 
                      @change="updateItemStatus(item)"
                      :disabled="item.status === 'locked'"
                    />
                    <span class="ml-2 font-medium" :class="item.completed ? 'line-through text-500' : ''">{{ item.title }}</span>
                    <Tag 
                      v-if="item.priority === 'high'" 
                      value="High Priority" 
                      severity="danger" 
                      class="ml-2"
                    />
                  </div>
                  <p class="text-600 text-sm mb-2">{{ item.description }}</p>
                  <div class="flex align-items-center text-sm text-500">
                    <i class="pi pi-user mr-1"></i>
                    <span class="mr-3">{{ item.assignee }}</span>
                    <i class="pi pi-calendar mr-1"></i>
                    <span>Due: {{ formatDate(item.dueDate) }}</span>
                  </div>
                </div>
                <div class="flex gap-2">
                  <Button 
                    icon="pi pi-eye" 
                    class="p-button-text p-button-sm" 
                    @click="viewItem(item)"
                  />
                  <Button 
                    v-if="!item.completed" 
                    icon="pi pi-play" 
                    class="p-button-text p-button-sm p-button-success" 
                    @click="startTask(item)"
                  />
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <div class="sidebar-cards">
        <Card class="summary-card">
          <template #header>
            <h3 class="card-title">Period Summary</h3>
          </template>
          <template #content>
            <div class="summary-items">
              <div class="flex justify-content-between">
                <span>Total Tasks:</span>
                <span class="font-bold">{{ checklist.length }}</span>
              </div>
              <div class="flex justify-content-between">
                <span>Completed:</span>
                <span class="font-bold text-green-600">{{ completedTasks }}</span>
              </div>
              <div class="flex justify-content-between">
                <span>Pending:</span>
                <span class="font-bold text-orange-600">{{ pendingTasks }}</span>
              </div>
              <div class="flex justify-content-between">
                <span>Overdue:</span>
                <span class="font-bold text-red-600">{{ overdueTasks }}</span>
              </div>
              <Divider />
              <ProgressBar :value="completionPercentage" class="mb-2" />
              <div class="text-center text-sm text-500">{{ completionPercentage }}% Complete</div>
            </div>
          </template>
        </Card>

        <Card>
          <template #header>
            <h3 class="card-title">Quick Actions</h3>
          </template>
          <template #content>
            <div class="actions-list">
              <Button 
                label="Run Trial Balance" 
                icon="pi pi-calculator" 
                class="action-btn" 
                @click="runTrialBalance"
              />
              <Button 
                label="Generate Reports" 
                icon="pi pi-file-pdf" 
                class="action-btn" 
                @click="generateReports"
              />
              <Button 
                label="Review Adjustments" 
                icon="pi pi-pencil" 
                class="action-btn" 
                @click="reviewAdjustments"
              />
              <Button 
                label="Close Period" 
                icon="pi pi-lock" 
                class="action-btn p-button-danger" 
                @click="confirmClosePeriod"
                :disabled="completionPercentage < 100"
              />
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Close Period Dialog -->
    <Dialog 
      v-model:visible="showCloseDialog" 
      :style="{width: '500px'}" 
      header="Close Period" 
      :modal="true"
    >
      <div class="mb-4">
        <p>Are you sure you want to close the period <strong>{{ selectedPeriod }}</strong>?</p>
        <p class="text-orange-600">This action cannot be undone and will prevent further modifications to this period.</p>
      </div>
      <div class="field">
        <label for="closeReason">Reason for Closing:</label>
        <Textarea 
          id="closeReason" 
          v-model="closeReason" 
          rows="3" 
          class="w-full"
        />
      </div>
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="showCloseDialog = false"
        />
        <Button 
          label="Close Period" 
          icon="pi pi-lock" 
          class="p-button-danger" 
          @click="closePeriod"
          :loading="closing"
        />
      </template>
    </Dialog>

    <!-- Task Details Dialog -->
    <Dialog 
      v-model:visible="showTaskDialog" 
      :style="{width: '600px'}" 
      :header="selectedTask?.title" 
      :modal="true"
    >
      <div v-if="selectedTask">
        <div class="grid">
          <div class="col-12">
            <div class="field">
              <label class="font-semibold">Description</label>
              <p>{{ selectedTask.description }}</p>
            </div>
          </div>
          <div class="col-6">
            <div class="field">
              <label class="font-semibold">Assignee</label>
              <p>{{ selectedTask.assignee }}</p>
            </div>
          </div>
          <div class="col-6">
            <div class="field">
              <label class="font-semibold">Due Date</label>
              <p>{{ formatDate(selectedTask.dueDate) }}</p>
            </div>
          </div>
          <div class="col-12" v-if="selectedTask.notes">
            <div class="field">
              <label class="font-semibold">Notes</label>
              <p>{{ selectedTask.notes }}</p>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <Button 
          label="Close" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="showTaskDialog = false"
        />
      </template>
    </Dialog>
    </template>
  </UnifiedDashboard>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'

interface ChecklistItem {
  id: string
  title: string
  description: string
  assignee: string
  dueDate: string
  completed: boolean
  priority: 'high' | 'medium' | 'low'
  status: 'open' | 'in-progress' | 'completed' | 'locked'
  notes?: string
}

const toast = useToast()
const confirm = useConfirm()

const loading = ref(false)
const closing = ref(false)
const showCloseDialog = ref(false)
const showTaskDialog = ref(false)
const closeReason = ref('')
const selectedTask = ref<ChecklistItem | null>(null)

const currentPeriod = ref('December 2024')
const periodStatus = ref('Open')
const daysRemaining = ref(15)
const selectedPeriod = ref('2024-12')

const periods = ref([
  { label: 'December 2024', value: '2024-12' },
  { label: 'November 2024', value: '2024-11' },
  { label: 'October 2024', value: '2024-10' }
])

const checklist = ref<ChecklistItem[]>([
  {
    id: '1',
    title: 'Review and Post All Journal Entries',
    description: 'Ensure all transactions for the period are recorded',
    assignee: 'John Smith',
    dueDate: '2024-12-28',
    completed: true,
    priority: 'high',
    status: 'completed'
  },
  {
    id: '2',
    title: 'Bank Reconciliation',
    description: 'Reconcile all bank accounts for the period',
    assignee: 'Jane Doe',
    dueDate: '2024-12-29',
    completed: true,
    priority: 'high',
    status: 'completed'
  },
  {
    id: '3',
    title: 'Accounts Receivable Aging',
    description: 'Review and update AR aging report',
    assignee: 'Mike Johnson',
    dueDate: '2024-12-30',
    completed: false,
    priority: 'high',
    status: 'in-progress'
  },
  {
    id: '4',
    title: 'Inventory Valuation',
    description: 'Perform inventory count and valuation',
    assignee: 'Sarah Wilson',
    dueDate: '2024-12-31',
    completed: false,
    priority: 'high',
    status: 'open'
  },
  {
    id: '5',
    title: 'Depreciation Calculation',
    description: 'Calculate and record monthly depreciation',
    assignee: 'Tom Brown',
    dueDate: '2024-12-31',
    completed: false,
    priority: 'medium',
    status: 'open'
  },
  {
    id: '6',
    title: 'Accruals and Prepayments',
    description: 'Record accrued expenses and prepaid items',
    assignee: 'Lisa Davis',
    dueDate: '2024-12-31',
    completed: false,
    priority: 'medium',
    status: 'open'
  }
])

const home = ref({ icon: 'pi pi-home', to: '/' })
const breadcrumbItems = ref([
  { label: 'General Ledger', to: '/gl' },
  { label: 'Period Close' }
])

const completedTasks = computed(() => checklist.value.filter(item => item.completed).length)
const pendingTasks = computed(() => checklist.value.filter(item => !item.completed).length)
const overdueTasks = computed(() => {
  const today = new Date()
  return checklist.value.filter(item => !item.completed && new Date(item.dueDate) < today).length
})
const completionPercentage = computed(() => 
  Math.round((completedTasks.value / checklist.value.length) * 100)
)

const loadData = async () => {
  loading.value = true
  try {
    const [statusResponse, checklistResponse] = await Promise.all([
      fetch('http://localhost:8000/api/v1/gl/period-close/status'),
      fetch('http://localhost:8000/api/v1/gl/period-close/checklist')
    ])
    
    if (statusResponse.ok) {
      const statusData = await statusResponse.json()
      currentPeriod.value = statusData.currentPeriod || 'December 2024'
      periodStatus.value = statusData.status || 'Open'
      daysRemaining.value = statusData.daysRemaining || 15
    }
    
    if (checklistResponse.ok) {
      const checklistData = await checklistResponse.json()
      checklist.value = checklistData || checklist.value
    }
  } catch (error) {
    console.error('Error loading period close data:', error)
    // Keep using mock data on error
  } finally {
    loading.value = false
  }
}

const loadChecklist = () => {
  // Load checklist for selected period
  console.log('Loading checklist for:', selectedPeriod.value)
}

const updateItemStatus = async (item: ChecklistItem) => {
  try {
    await fetch(`http://localhost:8000/api/v1/gl/period-close/checklist/${item.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed: item.completed })
    })
    
    item.status = item.completed ? 'completed' : 'open'
    toast.add({
      severity: 'success',
      summary: 'Updated',
      detail: `Task "${item.title}" ${item.completed ? 'completed' : 'reopened'}`,
      life: 3000
    })
  } catch (error) {
    console.error('Error updating task:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to update task status',
      life: 3000
    })
  }
}

const viewItem = (item: ChecklistItem) => {
  selectedTask.value = item
  showTaskDialog.value = true
}

const startTask = (item: ChecklistItem) => {
  item.status = 'in-progress'
  toast.add({
    severity: 'info',
    summary: 'Task Started',
    detail: `Started working on "${item.title}"`,
    life: 3000
  })
}

const getItemClass = (status: string) => {
  switch (status) {
    case 'completed': return 'bg-green-50 border-green-200'
    case 'in-progress': return 'bg-blue-50 border-blue-200'
    case 'locked': return 'bg-gray-50 border-gray-200'
    default: return 'bg-white'
  }
}

const runTrialBalance = () => {
  toast.add({
    severity: 'info',
    summary: 'Running Trial Balance',
    detail: 'Trial balance report is being generated...',
    life: 3000
  })
}

const generateReports = () => {
  toast.add({
    severity: 'info',
    summary: 'Generating Reports',
    detail: 'Period-end reports are being generated...',
    life: 3000
  })
}

const reviewAdjustments = () => {
  toast.add({
    severity: 'info',
    summary: 'Review Adjustments',
    detail: 'Opening adjustment entries review...',
    life: 3000
  })
}

const confirmClosePeriod = () => {
  showCloseDialog.value = true
}

const closePeriod = async () => {
  closing.value = true
  try {
    await fetch('http://localhost:8000/api/v1/gl/period-close/close', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        period: selectedPeriod.value,
        reason: closeReason.value 
      })
    })
    
    periodStatus.value = 'Closed'
    showCloseDialog.value = false
    toast.add({
      severity: 'success',
      summary: 'Period Closed',
      detail: `Period ${selectedPeriod.value} has been successfully closed`,
      life: 5000
    })
  } catch (error) {
    console.error('Error closing period:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to close period',
      life: 3000
    })
  } finally {
    closing.value = false
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-lg, 1.5rem);
}

.sidebar-cards {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md, 1rem);
}

.card-title {
  font-size: var(--font-size-lg, 1.125rem);
  font-weight: var(--font-weight-semibold, 600);
  color: var(--text-color, #1e293b);
  margin: 0;
}

.checklist-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.checklist-item {
  border: 1px solid var(--surface-200, #e2e8f0);
  border-radius: 6px;
  padding: 0.75rem;
}

.checklist-item.bg-green-50 {
  background-color: #f0fdf4;
  border-color: #bbf7d0;
}

.checklist-item.bg-blue-50 {
  background-color: #eff6ff;
  border-color: #bfdbfe;
}

.checklist-item.bg-gray-50 {
  background-color: #f9fafb;
  border-color: #e5e7eb;
}

.summary-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm, 0.5rem);
}

.action-btn {
  width: 100%;
  justify-content: flex-start;
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md, 1rem);
  }
}
</style>