<template>
  <div class="budget-approval">
    <div class="dashboard-header">
      <h1>Budget Approval</h1>
      <p>Review and approve budget submissions from different departments.</p>
    </div>

    <div class="approval-content">
      <!-- Pending Approvals -->
      <Card class="pending-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-clock"></i>
            <span>Pending Approvals ({{ pendingBudgets.length }})</span>
          </div>
        </template>
        <template #content>
          <DataTable :value="pendingBudgets" responsive-layout="scroll">
            <Column field="name" header="Budget Name" sortable />
            <Column field="type" header="Type">
              <template #body="{ data }">
                <Tag :value="data.type" :severity="getTypeSeverity(data.type)" />
              </template>
            </Column>
            <Column field="amount" header="Amount" sortable>
              <template #body="{ data }">
                <span class="font-medium">{{ formatCurrency(data.amount) }}</span>
              </template>
            </Column>
            <Column field="submitted_at" header="Submitted" sortable>
              <template #body="{ data }">
                {{ formatDate(data.submitted_at) }}
              </template>
            </Column>
            <Column field="submitted_by" header="Submitted By" />
            <Column header="Actions">
              <template #body="{ data }">
                <div class="flex gap-2">
                  <Button icon="pi pi-eye" size="small" outlined @click="reviewBudget(data)" v-tooltip="'Review'" />
                  <Button icon="pi pi-check" size="small" severity="success" @click="approveBudget(data.id)" v-tooltip="'Approve'" />
                  <Button icon="pi pi-times" size="small" severity="danger" @click="rejectBudget(data.id)" v-tooltip="'Reject'" />
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>

      <!-- Approval History -->
      <Card class="history-card">
        <template #title>
          <span>Recent Approval History</span>
        </template>
        <template #content>
          <DataTable :value="approvalHistory" responsive-layout="scroll">
            <Column field="name" header="Budget Name" />
            <Column field="action" header="Action">
              <template #body="{ data }">
                <Tag :value="data.action" :severity="data.action === 'APPROVED' ? 'success' : 'danger'" />
              </template>
            </Column>
            <Column field="amount" header="Amount">
              <template #body="{ data }">
                {{ formatCurrency(data.amount) }}
              </template>
            </Column>
            <Column field="approved_at" header="Date">
              <template #body="{ data }">
                {{ formatDate(data.approved_at) }}
              </template>
            </Column>
            <Column field="approved_by" header="Approved By" />
            <Column field="notes" header="Notes" />
          </DataTable>
        </template>
      </Card>
    </div>

    <!-- Review Dialog -->
    <Dialog v-model:visible="showReviewDialog" header="Budget Review" :style="{ width: '80vw' }" modal>
      <div v-if="selectedBudget" class="review-content">
        <div class="budget-details">
          <h3>{{ selectedBudget.name }}</h3>
          <div class="details-grid">
            <div class="detail-item">
              <label>Type:</label>
              <Tag :value="selectedBudget.type" :severity="getTypeSeverity(selectedBudget.type)" />
            </div>
            <div class="detail-item">
              <label>Amount:</label>
              <span class="amount">{{ formatCurrency(selectedBudget.amount) }}</span>
            </div>
            <div class="detail-item">
              <label>Period:</label>
              <span>{{ formatDate(selectedBudget.start_date) }} - {{ formatDate(selectedBudget.end_date) }}</span>
            </div>
            <div class="detail-item">
              <label>Submitted By:</label>
              <span>{{ selectedBudget.submitted_by }}</span>
            </div>
          </div>
          
          <div class="description-section">
            <label>Description:</label>
            <p>{{ selectedBudget.description }}</p>
          </div>

          <div class="line-items-section">
            <h4>Budget Line Items</h4>
            <DataTable :value="selectedBudget.line_items" responsive-layout="scroll">
              <Column field="category" header="Category" />
              <Column field="description" header="Description" />
              <Column field="amount" header="Amount">
                <template #body="{ data }">
                  {{ formatCurrency(data.amount) }}
                </template>
              </Column>
            </DataTable>
          </div>
        </div>

        <div class="approval-section">
          <div class="field">
            <label>Approval Notes</label>
            <Textarea v-model="approvalNotes" rows="3" placeholder="Enter approval notes..." />
          </div>
          
          <div class="approval-actions">
            <Button label="Approve" icon="pi pi-check" severity="success" @click="confirmApproval" />
            <Button label="Reject" icon="pi pi-times" severity="danger" @click="confirmRejection" />
            <Button label="Cancel" icon="pi pi-times" outlined @click="showReviewDialog = false" />
          </div>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useBudgetStore } from '../store/budgetStore'

// PrimeVue Components
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import Textarea from 'primevue/textarea'

const toast = useToast()
const budgetStore = useBudgetStore()

const showReviewDialog = ref(false)
const selectedBudget = ref(null)
const approvalNotes = ref('')

const pendingBudgets = ref([
  {
    id: 1,
    name: 'Marketing Q2 Campaign',
    type: 'OPERATIONAL',
    amount: 75000,
    submitted_at: '2024-01-15',
    submitted_by: 'John Smith',
    start_date: '2024-04-01',
    end_date: '2024-06-30',
    description: 'Budget for Q2 marketing campaigns including digital advertising and events.',
    line_items: [
      { category: 'Digital Ads', description: 'Google & Facebook Ads', amount: 40000 },
      { category: 'Events', description: 'Trade shows and conferences', amount: 25000 },
      { category: 'Content', description: 'Content creation and design', amount: 10000 }
    ]
  },
  {
    id: 2,
    name: 'IT Security Upgrade',
    type: 'CAPITAL',
    amount: 120000,
    submitted_at: '2024-01-14',
    submitted_by: 'Sarah Johnson',
    start_date: '2024-02-01',
    end_date: '2024-12-31',
    description: 'Upgrade security infrastructure and implement new security tools.',
    line_items: [
      { category: 'Hardware', description: 'Firewalls and security appliances', amount: 80000 },
      { category: 'Software', description: 'Security software licenses', amount: 30000 },
      { category: 'Training', description: 'Security training for staff', amount: 10000 }
    ]
  }
])

const approvalHistory = ref([
  {
    id: 3,
    name: 'HR Training Program',
    action: 'APPROVED',
    amount: 25000,
    approved_at: '2024-01-10',
    approved_by: 'Admin User',
    notes: 'Approved with minor adjustments'
  },
  {
    id: 4,
    name: 'Office Renovation',
    action: 'REJECTED',
    amount: 50000,
    approved_at: '2024-01-08',
    approved_by: 'Admin User',
    notes: 'Budget exceeds allocated funds for facilities'
  }
])

const getTypeSeverity = (type) => {
  switch (type) {
    case 'OPERATIONAL': return 'info'
    case 'CAPITAL': return 'warning'
    case 'PROJECT': return 'success'
    case 'DEPARTMENT': return 'secondary'
    default: return 'info'
  }
}

const formatCurrency = (amount) => 
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

const formatDate = (dateString) => 
  new Date(dateString).toLocaleDateString()

const reviewBudget = (budget) => {
  selectedBudget.value = budget
  showReviewDialog.value = true
  approvalNotes.value = ''
}

const approveBudget = async (id) => {
  try {
    await budgetStore.approveBudget(id, 'Quick approval')
    toast.add({ severity: 'success', summary: 'Success', detail: 'Budget approved successfully' })
    // Remove from pending list
    const index = pendingBudgets.value.findIndex(b => b.id === id)
    if (index > -1) pendingBudgets.value.splice(index, 1)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to approve budget' })
  }
}

const rejectBudget = async (id) => {
  try {
    await budgetStore.rejectBudget(id, 'Budget rejected')
    toast.add({ severity: 'warn', summary: 'Rejected', detail: 'Budget rejected successfully' })
    // Remove from pending list
    const index = pendingBudgets.value.findIndex(b => b.id === id)
    if (index > -1) pendingBudgets.value.splice(index, 1)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to reject budget' })
  }
}

const confirmApproval = async () => {
  try {
    await budgetStore.approveBudget(selectedBudget.value.id, approvalNotes.value)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Budget approved successfully' })
    showReviewDialog.value = false
    // Remove from pending list
    const index = pendingBudgets.value.findIndex(b => b.id === selectedBudget.value.id)
    if (index > -1) pendingBudgets.value.splice(index, 1)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to approve budget' })
  }
}

const confirmRejection = async () => {
  try {
    await budgetStore.rejectBudget(selectedBudget.value.id, approvalNotes.value || 'Budget rejected')
    toast.add({ severity: 'warn', summary: 'Rejected', detail: 'Budget rejected successfully' })
    showReviewDialog.value = false
    // Remove from pending list
    const index = pendingBudgets.value.findIndex(b => b.id === selectedBudget.value.id)
    if (index > -1) pendingBudgets.value.splice(index, 1)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to reject budget' })
  }
}

onMounted(() => {
  // Load pending approvals
})
</script>

<style scoped>
.budget-approval {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.pending-card {
  margin-bottom: 2rem;
}

.review-content {
  display: grid;
  gap: 2rem;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-weight: 600;
  color: #6b7280;
  font-size: 0.875rem;
}

.amount {
  font-weight: 600;
  color: #3b82f6;
  font-size: 1.125rem;
}

.description-section,
.line-items-section {
  margin: 1rem 0;
}

.description-section label,
.line-items-section h4 {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.approval-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.approval-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
</style>