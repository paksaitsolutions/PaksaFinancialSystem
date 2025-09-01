<template>
  <div class="budget-approval-interface">
    <Card>
      <template #title>Budget Approval</template>
      <template #content>
        <div v-if="budget" class="budget-approval-content">
          <div class="grid">
            <div class="col-12 md:col-8">
              <div class="budget-details">
                <h3>{{ budget.name }}</h3>
                <p class="text-500">{{ budget.description }}</p>
                
                <div class="grid mt-4">
                  <div class="col-6">
                    <div class="field">
                      <label>Budget Period</label>
                      <div class="font-medium">
                        {{ formatPeriod(budget.startDate, budget.endDate) }}
                      </div>
                    </div>
                  </div>
                  <div class="col-6">
                    <div class="field">
                      <label>Total Amount</label>
                      <div class="font-medium text-2xl">
                        {{ formatCurrency(budget.totalAmount) }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="field">
                  <label>Budget Categories</label>
                  <DataTable :value="budget.categories" class="p-datatable-sm">
                    <Column field="name" header="Category" />
                    <Column field="amount" header="Amount">
                      <template #body="{ data }">
                        {{ formatCurrency(data.amount) }}
                      </template>
                    </Column>
                    <Column field="percentage" header="% of Total">
                      <template #body="{ data }">
                        {{ ((data.amount / budget.totalAmount) * 100).toFixed(1) }}%
                      </template>
                    </Column>
                  </DataTable>
                </div>
              </div>
            </div>
            
            <div class="col-12 md:col-4">
              <div class="approval-panel">
                <div class="field">
                  <label>Current Status</label>
                  <Tag :value="budget.status" :severity="getStatusSeverity(budget.status)" />
                </div>
                
                <div class="field">
                  <label>Approval Action</label>
                  <div class="flex flex-column gap-2">
                    <Button 
                      label="Approve" 
                      icon="pi pi-check"
                      class="p-button-success"
                      @click="handleApproval('approved')"
                      :disabled="budget.status !== 'Pending'"
                      :loading="processing"
                    />
                    <Button 
                      label="Reject" 
                      icon="pi pi-times"
                      class="p-button-danger p-button-outlined"
                      @click="handleApproval('rejected')"
                      :disabled="budget.status !== 'Pending'"
                      :loading="processing"
                    />
                    <Button 
                      label="Request Changes" 
                      icon="pi pi-pencil"
                      class="p-button-warning p-button-outlined"
                      @click="handleApproval('changes_requested')"
                      :disabled="budget.status !== 'Pending'"
                      :loading="processing"
                    />
                  </div>
                </div>
                
                <div class="field">
                  <label for="comments">Comments</label>
                  <Textarea 
                    id="comments"
                    v-model="approvalComments"
                    rows="4"
                    class="w-full"
                    placeholder="Add your comments..."
                  />
                </div>
              </div>
            </div>
          </div>
          
          <div class="approval-history mt-4">
            <h4>Approval History</h4>
            <div v-if="budget.approvalHistory && budget.approvalHistory.length > 0">
              <div 
                v-for="entry in budget.approvalHistory" 
                :key="entry.id"
                class="approval-entry p-3 mb-2 border-1 surface-border border-round"
              >
                <div class="flex justify-content-between align-items-start">
                  <div>
                    <div class="font-medium">{{ entry.approver }}</div>
                    <div class="text-sm text-500">{{ formatDate(entry.date) }}</div>
                  </div>
                  <Tag :value="entry.action" :severity="getActionSeverity(entry.action)" />
                </div>
                <div v-if="entry.comments" class="mt-2 text-sm">
                  {{ entry.comments }}
                </div>
              </div>
            </div>
            <div v-else class="text-500">
              No approval history available.
            </div>
          </div>
        </div>
        
        <div v-else class="text-center p-4">
          <i class="pi pi-info-circle text-4xl text-500 mb-3"></i>
          <p class="text-500">Select a budget to review for approval.</p>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface BudgetCategory {
  name: string
  amount: number
}

interface ApprovalHistoryEntry {
  id: number
  approver: string
  action: string
  date: string
  comments?: string
}

interface Budget {
  id: number
  name: string
  description: string
  startDate: string
  endDate: string
  totalAmount: number
  status: string
  categories: BudgetCategory[]
  approvalHistory?: ApprovalHistoryEntry[]
}

const props = defineProps<{
  budget?: Budget
}>()

const emit = defineEmits(['approval-action'])

const processing = ref(false)
const approvalComments = ref('')

const handleApproval = async (action: string) => {
  processing.value = true
  try {
    emit('approval-action', {
      budgetId: props.budget?.id,
      action,
      comments: approvalComments.value
    })
    approvalComments.value = ''
  } finally {
    processing.value = false
  }
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const formatPeriod = (startDate: string, endDate: string) => {
  const start = new Date(startDate).toLocaleDateString()
  const end = new Date(endDate).toLocaleDateString()
  return `${start} - ${end}`
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'Approved': return 'success'
    case 'Pending': return 'warning'
    case 'Rejected': return 'danger'
    case 'Changes Requested': return 'info'
    default: return 'info'
  }
}

const getActionSeverity = (action: string) => {
  switch (action) {
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    case 'changes_requested': return 'warning'
    default: return 'info'
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
  color: var(--text-color-secondary);
}

.approval-panel {
  background: var(--surface-50);
  padding: 1rem;
  border-radius: 6px;
}

.approval-entry {
  background: var(--surface-0);
}
</style>