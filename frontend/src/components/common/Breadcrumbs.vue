<template>
  <Breadcrumb :model="breadcrumbs" class="breadcrumb-container">
    <template #item="{ item }">
      <router-link v-if="item.route" :to="item.route" class="breadcrumb-link">
        <i v-if="item.icon" :class="item.icon" class="breadcrumb-icon"></i>
        <span class="breadcrumb-label">{{ item.label }}</span>
      </router-link>
      <span v-else class="breadcrumb-current">
        <i v-if="item.icon" :class="item.icon" class="breadcrumb-icon"></i>
        <span class="breadcrumb-label">{{ item.label }}</span>
      </span>
    </template>
  </Breadcrumb>
</template>

<script setup lang="ts">
import { useBreadcrumbs } from '@/composables/useBreadcrumbs'

const { breadcrumbs } = useBreadcrumbs()
</script>

<style scoped>
.breadcrumb-container {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #6b7280;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: #3b82f6;
}

.breadcrumb-current {
  display: flex;
  align-items: center;
  color: #1f2937;
  font-weight: 500;
}

.breadcrumb-icon {
  margin-right: 0.5rem;
  font-size: 0.875rem;
}

.breadcrumb-label {
  font-size: 0.875rem;
}

:deep(.p-breadcrumb) {
  background: transparent;
  border: none;
  padding: 0;
}

:deep(.p-breadcrumb-list) {
  margin: 0;
  padding: 0;
}

:deep(.p-breadcrumb-separator) {
  color: #9ca3af;
  margin: 0 0.5rem;
}
</style>