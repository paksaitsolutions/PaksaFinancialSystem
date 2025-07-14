<template>
  <v-container fluid>
    <v-row>
      <!-- Budget List -->
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-row align="center">
              <v-col cols="8">
                <h2>Budgets</h2>
              </v-col>
              <v-col cols="4" class="text-right">
                <v-btn color="primary" @click="openCreateDialog">
                  <v-icon left>mdi-plus</v-icon>
                  New Budget
                </v-btn>
              </v-col>
            </v-row>
          </v-card-title>

          <v-card-text>
            <!-- Filters -->
            <v-row class="mb-4">
              <v-col cols="12" sm="3">
                <v-select
                  v-model="filters.status"
                  :items="Object.values(BudgetStatus)"
                  label="Status"
                  clearable
                ></v-select>
              </v-col>
              <v-col cols="12" sm="3">
                <v-select
                  v-model="filters.type"
                  :items="Object.values(BudgetType)"
                  label="Type"
                  clearable
                ></v-select>
              </v-col>
              <v-col cols="12" sm="3">
                <v-text-field
                  v-model="filters.startDate"
                  label="Start Date"
                  type="date"
                  clearable
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="3">
                <v-text-field
                  v-model="filters.endDate"
                  label="End Date"
                  type="date"
                  clearable
                ></v-text-field>
              </v-col>
            </v-row>

            <!-- Budget Table -->
            <v-data-table
              :headers="headers"
              :items="filteredBudgets"
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
                <v-btn icon @click="openEditDialog(item)">
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
                <v-btn
                  v-if="item.status === BudgetStatus.DRAFT"
                  icon
                  @click="openApprovalDialog(item)"
                >
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

    <!-- Create/Edit Dialog -->
    <v-dialog v-model="dialog" max-width="800">
      <v-card>
        <v-card-title>
          {{ selectedBudget ? 'Edit Budget' : 'Create Budget' }}
        </v-card-title>
        <v-card-text>
          <BudgetForm
            v-if="dialog"
            :budget="selectedBudget"
            @save="handleSave"
            @cancel="dialog = false"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Approval Dialog -->
    <v-dialog v-model="approvalDialog" max-width="500">
      <v-card>
        <v-card-title>Approve Budget</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="approvalNotes"
            label="Approval Notes (Optional)"
            rows="3"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="approvalDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="handleApproval">Approve</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Reject Dialog -->
    <v-dialog v-model="rejectDialog" max-width="500">
      <v-card>
        <v-card-title>Reject Budget</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="rejectNotes"
            label="Rejection Notes (Required)"
            rows="3"
            :rules="[v => !!v || 'Notes are required']"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="rejectDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="handleReject">Reject</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useBudgetStore } from '@/stores/budget'
import { BudgetStatus, BudgetType } from '@/types/budget'
import BudgetForm from './BudgetForm.vue'

const budgetStore = useBudgetStore()

// State
const dialog = ref(false)
const approvalDialog = ref(false)
const rejectDialog = ref(false)
const selectedBudget = ref<any>(null)
const approvalNotes = ref('')
const rejectNotes = ref('')

// Computed
const loading = computed(() => budgetStore.loading)
const error = computed(() => budgetStore.error)
const filteredBudgets = computed(() => budgetStore.filteredBudgets)

// Headers for the data table
const headers = [
  { text: 'Name', value: 'name' },
  { text: 'Type', value: 'budget_type' },
  { text: 'Status', value: 'status' },
  { text: 'Start Date', value: 'start_date' },
  { text: 'End Date', value: 'end_date' },
  { text: 'Total Amount', value: 'total_amount', align: 'right' },
  { text: 'Actions', value: 'actions', sortable: false, align: 'right' }
]

// Methods
const openCreateDialog = () => {
  selectedBudget.value = null
  dialog.value = true
}

const openEditDialog = (budget: any) => {
  selectedBudget.value = budget
  dialog.value = true
}

const openApprovalDialog = (budget: any) => {
  selectedBudget.value = budget
  approvalDialog.value = true
}

const openRejectDialog = (budget: any) => {
  selectedBudget.value = budget
  rejectDialog.value = true
}

const selectBudget = (budget: any) => {
  // Handle budget selection
  console.log('Selected budget:', budget)
}

const handleSave = async (budgetData: any) => {
  try {
    if (selectedBudget.value) {
      await budgetStore.updateBudget(selectedBudget.value.id, budgetData)
    } else {
      await budgetStore.createBudget(budgetData)
    }
    dialog.value = false
  } catch (err) {
    console.error('Error saving budget:', err)
  }
}

const handleApproval = async () => {
  if (selectedBudget.value) {
    try {
      await budgetStore.approveBudget(selectedBudget.value.id, { notes: approvalNotes.value })
      approvalDialog.value = false
    } catch (err) {
      console.error('Error approving budget:', err)
    }
  }
}

const handleReject = async () => {
  if (selectedBudget.value && rejectNotes.value) {
    try {
      await budgetStore.rejectBudget(selectedBudget.value.id, rejectNotes.value)
      rejectDialog.value = false
    } catch (err) {
      console.error('Error rejecting budget:', err)
    }
  }
}

const getStatusColor = (status: BudgetStatus) => {
  switch (status) {
    case BudgetStatus.DRAFT:
      return 'blue'
    case BudgetStatus.APPROVED:
      return 'green'
    case BudgetStatus.REJECTED:
      return 'red'
    case BudgetStatus.ARCHIVED:
      return 'grey'
    default:
      return 'grey'
  }
}

// Fetch initial data
budgetStore.fetchBudgets()
</script>
