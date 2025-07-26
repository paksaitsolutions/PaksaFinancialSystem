<template>
  <v-card>
    <v-card-title>Budget Variance Analysis</v-card-title>
    <v-card-text>
      <v-data-table
        :items="variances"
        :headers="headers"
        class="elevation-1"
      >
        <template #item.variance="{ item }">
          <v-chip :color="item.variance > 0 ? 'error' : 'success'" size="small">
            {{ formatCurrency(item.variance) }}
          </v-chip>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'

const headers = [
  { title: 'Category', key: 'category' },
  { title: 'Budget', key: 'budget' },
  { title: 'Actual', key: 'actual' },
  { title: 'Variance', key: 'variance' }
]

const variances = ref([
  { category: 'Marketing', budget: 10000, actual: 12000, variance: 2000 },
  { category: 'Operations', budget: 50000, actual: 48000, variance: -2000 }
])

const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
</script>