<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Budget Management</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Create Budget</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="createBudget">
              <v-text-field
                v-model="budgetForm.name"
                label="Budget Name"
                required
              />
              <v-text-field
                v-model="budgetForm.amount"
                label="Amount"
                type="number"
                prefix="$"
                required
              />
              <v-select
                v-model="budgetForm.category"
                :items="categories"
                label="Category"
                required
              />
              <v-btn type="submit" color="primary" :loading="loading">
                Create Budget
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Budget Summary</v-card-title>
          <v-card-text>
            <div class="mb-2">
              <strong>Total Budget:</strong> {{ formatCurrency(totalBudget) }}
            </div>
            <div class="mb-2">
              <strong>Total Spent:</strong> {{ formatCurrency(totalSpent) }}
            </div>
            <div>
              <strong>Remaining:</strong> {{ formatCurrency(totalBudget - totalSpent) }}
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title>Budget List</v-card-title>
          <v-card-text>
            <v-data-table
              :items="budgets"
              :headers="headers"
              class="elevation-1"
            >
              <template #item.amount="{ item }">
                {{ formatCurrency(item.amount) }}
              </template>
              <template #item.spent="{ item }">
                {{ formatCurrency(item.spent) }}
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'

const loading = ref(false)

const budgetForm = ref({
  name: '',
  amount: '',
  category: ''
})

const categories = ['Marketing', 'Operations', 'IT', 'HR', 'Finance']

const budgets = ref([
  { id: 1, name: 'Marketing Q1', category: 'Marketing', amount: 50000, spent: 35000 },
  { id: 2, name: 'IT Infrastructure', category: 'IT', amount: 100000, spent: 75000 }
])

const headers = [
  { title: 'Name', key: 'name' },
  { title: 'Category', key: 'category' },
  { title: 'Amount', key: 'amount' },
  { title: 'Spent', key: 'spent' }
]

const totalBudget = computed(() => budgets.value.reduce((sum, b) => sum + b.amount, 0))
const totalSpent = computed(() => budgets.value.reduce((sum, b) => sum + b.spent, 0))

const createBudget = () => {
  loading.value = true
  setTimeout(() => {
    budgets.value.push({
      id: Date.now(),
      name: budgetForm.value.name,
      category: budgetForm.value.category,
      amount: parseFloat(budgetForm.value.amount),
      spent: 0
    })
    budgetForm.value = { name: '', amount: '', category: '' }
    loading.value = false
  }, 1000)
}

const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
</script>