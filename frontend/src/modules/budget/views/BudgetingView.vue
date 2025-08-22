<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Budget Management</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>Create Budget</v-card-title>
          <v-card-text>
            <v-form ref="form" @submit.prevent="createBudget">
              <v-text-field
                v-model="budgetForm.name"
                label="Budget Name"
                :rules="nameRules"
                density="comfortable"
              />
              <v-text-field
                v-model="budgetForm.amount"
                label="Amount"
                type="number"
                prefix="$"
                :rules="amountRules"
                density="comfortable"
              />
              <v-select
                v-model="budgetForm.category"
                :items="categories"
                label="Category"
                :rules="categoryRules"
                density="comfortable"
              />
              <v-btn type="submit" color="primary" :loading="loading" block>
                Create Budget
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" lg="6">
        <v-card>
          <v-card-title>Budget Summary</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="4">
                <div class="text-center">
                  <div class="text-h6">{{ formatCurrency(totalBudget) }}</div>
                  <div class="text-caption">Total Budget</div>
                </div>
              </v-col>
              <v-col cols="12" sm="4">
                <div class="text-center">
                  <div class="text-h6">{{ formatCurrency(totalSpent) }}</div>
                  <div class="text-caption">Total Spent</div>
                </div>
              </v-col>
              <v-col cols="12" sm="4">
                <div class="text-center">
                  <div class="text-h6">{{ formatCurrency(totalBudget - totalSpent) }}</div>
                  <div class="text-caption">Remaining</div>
                </div>
              </v-col>
            </v-row>
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
              :mobile="null"
              density="comfortable"
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
const form = ref(null)

const budgetForm = ref({
  name: '',
  amount: '',
  category: ''
})

const nameRules = [
  v => !!v || 'Budget name is required',
  v => v.length >= 3 || 'Budget name must be at least 3 characters'
]

const amountRules = [
  v => !!v || 'Amount is required',
  v => v > 0 || 'Amount must be greater than 0',
  v => v <= 10000000 || 'Amount cannot exceed $10,000,000'
]

const categoryRules = [
  v => !!v || 'Category is required'
]

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

const createBudget = async () => {
  const { valid } = await form.value.validate()
  
  if (!valid) return
  
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
    form.value.reset()
    loading.value = false
  }, 1000)
}

const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
</script>