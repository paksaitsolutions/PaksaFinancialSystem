<template>
  <AppLayout title="General Ledger">
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title>General Ledger Dashboard</v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="3" v-for="module in glModules" :key="module.name">
                  <v-card hover @click="$router.push(module.route)">
                    <v-card-text class="text-center">
                      <v-icon size="48" :color="module.color">{{ module.icon }}</v-icon>
                      <div class="text-h6 mt-2">{{ module.name }}</div>
                      <div class="text-caption">{{ module.description }}</div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'

const glModules = [
  { name: 'Chart of Accounts', route: '/gl/chart-of-accounts', icon: 'mdi-format-list-numbered', color: 'blue', description: 'Manage account structure' },
  { name: 'Journal Entries', route: '/gl/journal-entries', icon: 'mdi-book-edit', color: 'green', description: 'Record transactions' },
  { name: 'Trial Balance', route: '/gl/trial-balance', icon: 'mdi-scale-balance', color: 'purple', description: 'View trial balance' },
  { name: 'Financial Statements', route: '/gl/financial-statements', icon: 'mdi-file-chart', color: 'orange', description: 'Generate reports' }
]
</script>