<template>
  <v-container fluid>
    <v-row>
      <!-- Approval Queue -->
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-row align="center">
              <v-col cols="8">
                <h2>Budget Approval Queue</h2>
              </v-col>
              <v-col cols="4" class="text-right">
                <v-btn color="primary" @click="refreshQueue">
                  <v-icon left>mdi-refresh</v-icon>
                  Refresh Queue
                </v-btn>
              </v-col>
            </v-row>
          </v-card-title>

          <v-card-text>
            <!-- Filters -->
            <v-row class="mb-4">
              <v-col cols="12" sm="4">
                <v-text-field
                  v-model="filters.search"
                  label="Search"
                  prepend-icon="mdi-magnify"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="4">
                <v-select
                  v-model="filters.status"
                  :items="[BudgetStatus.DRAFT, BudgetStatus.REJECTED]"
                  label="Status"
                  clearable
                ></v-select>
              </v-col>
              <v-col cols="12" sm="4">
                <v-select
                  v-model="filters.type"
                  :items="Object.values(BudgetType)"
                  label="Type"
                  clearable
                ></v-select>
              </v-col>
            </v-row>

            <!-- Approval Table -->
            <v-data-table
              :headers="headers"
              :items="filteredQueue"
              :loading="loading"
              :items-per-page="10"
              class="elevation-1"
              @click:row="(item) => selectBudget(item)"
            >
              <template v-slot:item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  small
                >
                  {{ item.status }}
                </v-chip>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn icon @click="openApprovalDialog(item)">
                  <v-icon>mdi-check</v-icon>
                </v-btn>
                <v-btn
                  v-if="item.status === BudgetStatus.DRAFT"
                  icon
                  @click="openRejectDialog(item)"
                >
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Approval Dialog -->
    <v-dialog v-model="approvalDialog.visible" max-width="500" :persistent="approvalDialog.loading">
      <v-card :loading="approvalDialog.loading">
        <v-card-title>Approve Budget</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="approvalNotes"
            label="Approval Notes (Optional)"
            rows="3"
            :error-messages="approvalDialog.error"
            :disabled="approvalDialog.loading"
            @input="approvalDialog.error = ''"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn 
            text 
            @click="approvalDialog.visible = false"
            :disabled="approvalDialog.loading"
          >
            Cancel
          </v-btn>
          <v-btn 
            color="primary" 
            @click="handleApproval"
            :loading="approvalDialog.loading"
          >
            Approve
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Reject Dialog -->
    <v-dialog v-model="rejectDialog.visible" max-width="500" :persistent="rejectDialog.loading">
      <v-card :loading="rejectDialog.loading">
        <v-card-title>Reject Budget</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="rejectNotes"
            label="Rejection Notes (Required)"
            rows="3"
            :error-messages="rejectDialog.error"
            :rules="[v => !!v || 'Notes are required']"
            :disabled="rejectDialog.loading"
            @input="rejectDialog.error = ''"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn 
            text 
            @click="rejectDialog.visible = false"
            :disabled="rejectDialog.loading"
          >
            Cancel
          </v-btn>
          <v-btn 
            color="error" 
            @click="handleReject"
            :loading="rejectDialog.loading"
          >
            Reject
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Budget Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="900">
      <v-card>
        <v-card-title>Review Budget Details</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <h3 class="text-h6">Basic Information</h3>
              <v-list dense>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Name</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedBudget?.name }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Type</v-list-item-title>
                    <v-list-item-subtitle>{{ selectedBudget?.budget_type }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Total Amount</v-list-item-title>
                    <v-list-item-subtitle>${{ formatCurrency(selectedBudget?.total_amount) }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Period</v-list-item-title>
                    <v-list-item-subtitle>
                      {{ formatDate(selectedBudget?.start_date) }} - {{ formatDate(selectedBudget?.end_date) }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
            </v-col>

            <v-col cols="12">
              <h3 class="text-h6">Budget Lines</h3>
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th>Account</th>
                      <th>Department</th>
                      <th>Project</th>
                      <th>Amount</th>
                      <th>Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="line in selectedBudget?.lines" :key="line.id">
                      <td>{{ line.account_id }}</td>
                      <td>{{ line.department_id }}</td>
                      <td>{{ line.project_id }}</td>
                      <td>${{ formatCurrency(line.amount) }}</td>
                      <td>{{ line.description }}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-col>

            <v-col cols="12">
              <h3 class="text-h6">Allocations</h3>
              <v-simple-table>
                <template v-slot:default>
                  <thead>
                    <tr>
                      <th>Department</th>
                      <th>Project</th>
                      <th>Amount</th>
                      <th>Percentage</th>
                      <th>Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="alloc in selectedBudget?.allocations" :key="alloc.id">
                      <td>{{ alloc.department_id }}</td>
                      <td>{{ alloc.project_id }}</td>
                      <td>${{ formatCurrency(alloc.amount) }}</td>
                      <td>{{ alloc.percentage }}%</td>
                      <td>{{ alloc.description }}</td>
                    </tr>
                  </tbody>
                </template>
              </v-simple-table>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="detailsDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useBudgetStore } from '../../store/budget'
import { Budget, BudgetStatus, BudgetType } from '../types/budget'

const budgetStore = useBudgetStore()

// State
const toast = useToast()
const loading = ref(false)
const approvalDialog = ref({
  visible: false,
  loading: false,
  error: ''
})
const rejectDialog = ref({
  visible: false,
  loading: false,
  error: ''
})
const detailsDialog = ref(false)
const selectedBudget = ref<Budget | null>(null)
const approvalNotes = ref('')
const rejectNotes = ref('')

// Filters
const filters = ref({
  search: '',
  status: BudgetStatus.DRAFT,
  type: null
})

// Computed
const filteredQueue = computed(() => {
  let result = budgetStore.budgets

  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(b =>
      b.name.toLowerCase().includes(search) ||
      b.description?.toLowerCase().includes(search)
    )
  }

  if (filters.value.status) {
    result = result.filter(b => b.status === filters.value.status)
  }

  if (filters.value.type) {
    result = result.filter(b => b.budget_type === filters.value.type)
  }

  return result
})

// Headers
const headers = [
  { text: 'Name', value: 'name' },
  { text: 'Type', value: 'budget_type' },
  { text: 'Status', value: 'status' },
  { text: 'Total Amount', value: 'total_amount', align: 'right' },
  { text: 'Created At', value: 'created_at' },
  { text: 'Actions', value: 'actions', sortable: false, align: 'right' }
]

// Methods
const refreshQueue = () => {
  budgetStore.fetchBudgets()
}

const selectBudget = (budget: any) => {
  selectedBudget.value = budget
  detailsDialog.value = true
}

const openApprovalDialog = (budget: Budget) => {
  selectedBudget.value = budget
  approvalNotes.value = ''
  approvalDialog.value = {
    ...approvalDialog.value,
    visible: true,
    error: ''
  }
}

const openRejectDialog = (budget: Budget) => {
  selectedBudget.value = budget
  rejectNotes.value = ''
  rejectDialog.value = {
    ...rejectDialog.value,
    visible: true,
    error: ''
  }
}

const handleApproval = async () => {
  if (!selectedBudget.value) {
    toast.add({
      severity: 'warn',
      summary: 'No Budget Selected',
      detail: 'Please select a budget to approve',
      life: 5000
    })
    return
  }

  try {
    approvalDialog.value.loading = true
    await budgetStore.approveBudget(selectedBudget.value.id, { notes: approvalNotes.value })
    
    approvalDialog.value.visible = false
    approvalNotes.value = ''
    await refreshQueue()
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Budget approved successfully',
      life: 3000
    })
  } catch (error) {
    console.error('Error approving budget:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error instanceof Error ? error.message : 'Failed to approve budget',
      life: 5000
    })
  } finally {
    approvalDialog.value.loading = false
  }
}

const handleReject = async () => {
  if (!selectedBudget.value) {
    toast.add({
      severity: 'warn',
      summary: 'No Budget Selected',
      detail: 'Please select a budget to reject',
      life: 5000
    })
    return
  }
  
  if (!rejectNotes.value?.trim()) {
    rejectDialog.value.error = 'Please provide a reason for rejection'
    return
  }
  
  try {
    rejectDialog.value.loading = true
    await budgetStore.rejectBudget(selectedBudget.value.id, rejectNotes.value)
    
    rejectNotes.value = ''
    rejectDialog.value.visible = false
    await refreshQueue()
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Budget rejected successfully',
      life: 3000
    })
  } catch (error) {
    console.error('Error in handleReject:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error instanceof Error ? error.message : 'Failed to reject budget',
      life: 5000
    })
  } finally {
    rejectDialog.value.loading = false
  }
}

const getStatusColor = (status: BudgetStatus) => {
  switch (status) {
    case BudgetStatus.DRAFT:
      return 'primary'
    case BudgetStatus.APPROVED:
      return 'success'
    case BudgetStatus.REJECTED:
      return 'error'
    case BudgetStatus.ARCHIVED:
      return 'grey'
    default:
      return 'grey'
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString()
}

// Lifecycle
onMounted(() => {
  refreshQueue()
})
</script>
