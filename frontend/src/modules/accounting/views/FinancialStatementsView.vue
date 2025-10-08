<template>
  <div class="financial-statements p-4">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Financial Statements</h1>
        <Breadcrumb :home="home" :model="breadcrumbItems" />
      </div>
    </div>
    <Card>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-4" v-for="statement in statements" :key="statement.name">
            <Card class="h-full hover:shadow-3 cursor-pointer transition-all transition-duration-200">
              <template #content>
                <div class="text-center">
                  <i :class="statement.icon" class="text-5xl mb-3" :style="{color: statement.color}"></i>
                  <div class="text-xl font-medium mb-2">{{ statement.name }}</div>
                  <div class="text-sm text-600 mb-3">{{ statement.description }}</div>
                  <Button label="Generate Report" class="w-full" outlined />
                </div>
              </template>
            </Card>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const home = ref({ icon: 'pi pi-home', to: '/' })
const breadcrumbItems = ref([
  { label: 'Accounting', to: '/accounting' },
  { label: 'Financial Statements' }
])

const statements = [
  { name: 'Income Statement', icon: 'pi pi-chart-line', color: '#22c55e', description: 'Profit & Loss statement' },
  { name: 'Balance Sheet', icon: 'pi pi-chart-bar', color: '#3b82f6', description: 'Assets, liabilities & equity' },
  { name: 'Cash Flow Statement', icon: 'pi pi-money-bill', color: '#8b5cf6', description: 'Cash flow analysis' }
]
</script>