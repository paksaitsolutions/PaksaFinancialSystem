<template>
  <AppLayout title="Financial Statements">
    <v-container>
      <v-card>
        <v-card-title>Financial Statements</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="4" v-for="statement in statements" :key="statement.name">
              <v-card hover>
                <v-card-text class="text-center">
                  <v-icon size="48" :color="statement.color">{{ statement.icon }}</v-icon>
                  <div class="text-h6 mt-2">{{ statement.name }}</div>
                  <div class="text-caption">{{ statement.description }}</div>
                </v-card-text>
                <v-card-actions>
                  <v-btn block color="primary" variant="outlined">
                    Generate Report
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-container>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'

const statements = [
  { name: 'Income Statement', icon: 'mdi-chart-line', color: 'green', description: 'Profit & Loss statement' },
  { name: 'Balance Sheet', icon: 'mdi-scale-balance', color: 'blue', description: 'Assets, liabilities & equity' },
  { name: 'Cash Flow Statement', icon: 'mdi-cash-flow', color: 'purple', description: 'Cash flow analysis' }
]
</script>