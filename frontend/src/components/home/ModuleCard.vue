<template>
  <v-card 
    class="module-card h-100" 
    :color="getModuleColor(module.id) + '-lighten-5'" 
    elevation="2" 
    rounded="lg"
    :to="module.route"
    link
  >
    <v-card-item class="h-100 d-flex flex-column">
      <div class="d-flex align-center mb-4">
        <v-avatar :color="getModuleColor(module.id)" size="large" class="elevation-1 mr-4">
          <v-icon :icon="module.icon" size="large" color="white"></v-icon>
        </v-avatar>
        <div>
          <v-card-title class="font-weight-bold px-0">{{ module.title }}</v-card-title>
          <v-card-subtitle class="px-0">{{ getModuleDescription(module.id) }}</v-card-subtitle>
        </div>
      </div>

      <v-spacer></v-spacer>

      <div class="mt-auto">
        <v-divider class="mb-3"></v-divider>
        <div class="d-flex justify-space-between align-center">
          <v-btn
            variant="text"
            :color="getModuleColor(module.id)"
            class="text-none px-0"
            :to="module.route"
          >
            Open Module
            <v-icon end icon="mdi-arrow-right"></v-icon>
          </v-btn>
          
          <v-chip
            v-if="module.children && module.children.length > 0"
            size="small"
            :color="getModuleColor(module.id)"
            variant="outlined"
            class="ml-auto"
          >
            {{ module.children.length }} sections
          </v-chip>
        </div>
      </div>
    </v-card-item>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { MenuModule } from '@/store/menu';

const props = defineProps<{
  module: MenuModule;
}>();

// Module color mapping
const getModuleColor = (moduleId: string): string => {
  const colors: Record<string, string> = {
    'dashboard': 'blue',
    'general-ledger': 'indigo',
    'accounts-payable': 'teal',
    'accounts-receivable': 'green',
    'payroll': 'orange',
    'cash': 'cyan',
    'tax': 'purple',
    'reports': 'pink',
    'settings': 'grey',
  };
  
  return colors[moduleId] || 'primary';
};

// Module description mapping
const getModuleDescription = (moduleId: string): string => {
  const descriptions: Record<string, string> = {
    'dashboard': 'Overview of your financial data',
    'general-ledger': 'Manage chart of accounts and journal entries',
    'accounts-payable': 'Track and manage payables',
    'accounts-receivable': 'Manage customer invoices and payments',
    'payroll': 'Process payroll and manage employees',
    'cash': 'Track cash flow and bank accounts',
    'tax': 'Tax calculations and filings',
    'reports': 'Generate financial reports',
    'settings': 'Configure system settings',
  };
  
  return descriptions[moduleId] || 'Financial management module';
};
</script>

<style scoped>
.module-card {
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
}

.module-card :deep(.v-card-item) {
  height: 100%;
  padding: 1.5rem;
}

.module-card :deep(.v-card-title) {
  font-size: 1.125rem;
  line-height: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.module-card :deep(.v-card-subtitle) {
  opacity: 0.8;
  font-size: 0.875rem;
  line-height: 1.25rem;
  margin-top: 0;
}

.module-card :deep(.v-avatar) {
  transition: transform 0.2s;
}

.module-card:hover :deep(.v-avatar) {
  transform: scale(1.1);
}
</style>