<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <h1 class="text-h4">Budget Planning</h1>
          <v-btn color="primary" @click="showCreateBudget = true">
            <v-icon left>mdi-plus</v-icon>
            Create Budget
          </v-btn>
        </div>
        
        <v-tabs v-model="activeTab">
          <v-tab value="budgets">Budgets</v-tab>
          <v-tab value="approvals">Approvals</v-tab>
          <v-tab value="versions">Version Control</v-tab>
          <v-tab value="consolidation">Consolidation</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="budgets">
            <budget-list @edit="editBudget" @submit="submitBudget" />
          </v-window-item>
          
          <v-window-item value="approvals">
            <budget-approval-interface @approve="approveBudget" @reject="rejectBudget" />
          </v-window-item>
          
          <v-window-item value="versions">
            <budget-version-comparison @create-version="createVersion" />
          </v-window-item>
          
          <v-window-item value="consolidation">
            <budget-consolidation-dashboard @consolidate="consolidateBudgets" />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
    
    <budget-form-dialog 
      v-model="showCreateBudget" 
      :budget="selectedBudget"
      @save="saveBudget"
    />
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import BudgetList from '../components/BudgetList.vue'
import BudgetApprovalInterface from '../components/BudgetApprovalInterface.vue'
import BudgetVersionComparison from '../components/BudgetVersionComparison.vue'
import BudgetConsolidationDashboard from '../components/BudgetConsolidationDashboard.vue'
import BudgetFormDialog from '../components/BudgetFormDialog.vue'
import { useBudgetStore } from '../store/budget'

const budgetStore = useBudgetStore()
const activeTab = ref('budgets')
const showCreateBudget = ref(false)
const selectedBudget = ref(null)

const editBudget = (budget) => {
  selectedBudget.value = budget
  showCreateBudget.value = true
}

const saveBudget = async (budgetData) => {
  if (selectedBudget.value) {
    await budgetStore.updateBudget(selectedBudget.value.id, budgetData)
  } else {
    await budgetStore.createBudget(budgetData)
  }
  showCreateBudget.value = false
  selectedBudget.value = null
}

const submitBudget = async (budgetId) => {
  await budgetStore.submitBudget(budgetId)
}

const approveBudget = async (budgetId, notes) => {
  await budgetStore.approveBudget(budgetId, notes)
}

const rejectBudget = async (budgetId, reason) => {
  await budgetStore.rejectBudget(budgetId, reason)
}

const createVersion = async (budgetId, versionData) => {
  await budgetStore.createBudgetVersion(budgetId, versionData)
}

const consolidateBudgets = async (budgetIds, consolidationData) => {
  await budgetStore.consolidateBudgets(budgetIds, consolidationData)
}
</script>