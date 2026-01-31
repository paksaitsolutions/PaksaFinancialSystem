<template>
  <AppLayout title="Reports">
    <v-container>
      <v-card>
        <v-card-title>Financial Reports</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="4" v-for="report in reports" :key="report.name">
              <v-card hover>
                <v-card-text class="text-center">
                  <v-icon size="48" :color="report.color">{{ report.icon }}</v-icon>
                  <div class="text-h6 mt-2">{{ report.name }}</div>
                  <div class="text-caption">{{ report.description }}</div>
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

const reports = [
  { name: 'Income Statement', icon: 'mdi-chart-line', color: 'green', description: 'Profit & Loss report' },
  { name: 'Balance Sheet', icon: 'mdi-scale-balance', color: 'blue', description: 'Financial position' },
  { name: 'Cash Flow', icon: 'mdi-cash-flow', color: 'purple', description: 'Cash flow analysis' },
  { name: 'Trial Balance', icon: 'mdi-format-list-checks', color: 'orange', description: 'Account balances' },
  { name: 'AP Aging', icon: 'mdi-clock-outline', color: 'red', description: 'Accounts payable aging' },
  { name: 'AR Aging', icon: 'mdi-clock-check', color: 'teal', description: 'Accounts receivable aging' }
]
</script>