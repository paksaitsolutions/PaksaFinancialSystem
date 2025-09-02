<template>
  <div class="p-4">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1 class="text-3xl font-bold m-0">Budget Planning</h1>
      <Button 
        label="Create Budget" 
        icon="pi pi-plus" 
        @click="showCreateBudget = true"
      />
    </div>
    
    <TabView v-model:activeIndex="activeTabIndex">
      <TabPanel header="Budgets">
        <budget-list @edit="editBudget" @submit="submitBudget" />
      </TabPanel>
      
      <TabPanel header="Approvals">
        <budget-approval-interface @approve="approveBudget" @reject="rejectBudget" />
      </TabPanel>
      
      <TabPanel header="Version Control">
        <budget-version-comparison @create-version="createVersion" />
      </TabPanel>
      
      <TabPanel header="Consolidation">
        <budget-consolidation-dashboard @consolidate="consolidateBudgets" />
      </TabPanel>
    </TabView>
    
    <budget-form-dialog 
      v-model="showCreateBudget" 
      :budget="selectedBudget"
      @save="saveBudget"
    />
  </div>
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
const activeTabIndex = ref(0)
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