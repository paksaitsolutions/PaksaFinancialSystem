<template>
  <div class="unified-dashboard">
    <div class="dashboard-header">
      <div class="header-content">
        <h1 class="dashboard-title">{{ title }}</h1>
        <p v-if="subtitle" class="dashboard-subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="header-actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <div v-if="$slots.metrics" class="metrics-section">
      <slot name="metrics"></slot>
    </div>

    <div class="content-section">
      <slot name="content"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  subtitle?: string
}

defineProps<Props>()
</script>

<style scoped>
.unified-dashboard {
  max-width: 100%;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-lg);
  gap: var(--spacing-lg);
}

.header-content {
  flex: 1;
}

.dashboard-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-color);
  margin: 0 0 var(--spacing-xs) 0;
  line-height: var(--line-height-tight);
}

.dashboard-subtitle {
  font-size: var(--font-size-base);
  color: var(--text-color-secondary);
  margin: 0;
  line-height: var(--line-height-normal);
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.metrics-section {
  margin-bottom: var(--spacing-xl);
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-start;
  }
}
</style>