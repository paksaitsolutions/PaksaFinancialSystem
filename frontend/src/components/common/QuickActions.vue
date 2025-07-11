<template>
  <div class="quick-actions">
    <v-list>
      <v-list-item
        v-for="action in actions"
        :key="action.title"
        :to="action.route"
        class="action-item"
      >
        <template #prepend>
          <v-avatar :color="action.color" size="40">
            <v-icon color="white">{{ action.icon }}</v-icon>
          </v-avatar>
        </template>

        <v-list-item-title>{{ action.title }}</v-list-item-title>
        <v-list-item-subtitle>{{ action.description }}</v-list-item-subtitle>

        <template #append>
          <v-icon>mdi-chevron-right</v-icon>
        </template>
      </v-list-item>
    </v-list>
  </div>
</template>

<script setup lang="ts">
const actions = [
  {
    title: 'Create Journal Entry',
    description: 'Record a new transaction',
    icon: 'mdi-book-plus',
    color: 'blue',
    route: '/gl/journal-entries/create'
  },
  {
    title: 'Add New Account',
    description: 'Create chart of account',
    icon: 'mdi-account-plus',
    color: 'green',
    route: '/gl/accounts/create'
  },
  {
    title: 'Process Payroll',
    description: 'Run employee payroll',
    icon: 'mdi-cash-multiple',
    color: 'orange',
    route: '/payroll/process'
  },
  {
    title: 'Generate Report',
    description: 'Create financial report',
    icon: 'mdi-chart-line',
    color: 'purple',
    route: '/reports'
  },
  {
    title: 'Bank Reconciliation',
    description: 'Reconcile bank accounts',
    icon: 'mdi-bank',
    color: 'teal',
    route: '/cash/reconciliation'
  }
]
</script>

<style scoped>
.quick-actions {
  max-height: 400px;
  overflow-y: auto;
}

.action-item {
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.action-item:last-child {
  border-bottom: none;
}

.action-item:hover {
  background-color: #f5f5f5;
}
</style>