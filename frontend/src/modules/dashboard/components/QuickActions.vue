<template>
  <Card class="quick-actions-card">
    <template #title>
      <div class="actions-header">
        <h3>Quick Actions</h3>
        <i class="pi pi-bolt"></i>
      </div>
    </template>
    <template #content>
      <div class="actions-grid">
        <div 
          v-for="action in actions" 
          :key="action.id"
          class="action-item"
          @click="handleAction(action)"
        >
          <div class="action-icon" :style="{ backgroundColor: action.color + '20', color: action.color }">
            <i :class="action.icon"></i>
          </div>
          <div class="action-content">
            <h4 class="action-title">{{ action.title }}</h4>
            <p class="action-description">{{ action.description }}</p>
          </div>
          <div class="action-arrow">
            <i class="pi pi-chevron-right"></i>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  actions: {
    type: Array,
    default: () => []
  }
})

const router = useRouter()

const handleAction = (action) => {
  if (action.route) {
    router.push(action.route)
  } else if (action.action) {
    action.action()
  }
}
</script>

<style scoped>
.quick-actions-card {
  height: 100%;
}

.actions-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.actions-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
}

.actions-header i {
  font-size: 1.25rem;
  color: var(--primary-500);
}

.actions-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.action-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  border-radius: var(--border-radius-md);
  background: var(--surface-section);
  border: 1px solid var(--surface-border);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-item:hover {
  background: var(--surface-hover);
  transform: translateX(4px);
  box-shadow: var(--shadow-md);
}

.action-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  flex-shrink: 0;
}

.action-content {
  flex: 1;
  min-width: 0;
}

.action-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 var(--spacing-1) 0;
}

.action-description {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  margin: 0;
  line-height: 1.3;
}

.action-arrow {
  flex-shrink: 0;
  color: var(--text-color-muted);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.action-item:hover .action-arrow {
  color: var(--primary-500);
  transform: translateX(2px);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .action-item {
    padding: var(--spacing-2);
    gap: var(--spacing-2);
  }
  
  .action-icon {
    width: 32px;
    height: 32px;
    font-size: 1rem;
  }
  
  .action-title {
    font-size: 0.8125rem;
  }
  
  .action-description {
    font-size: 0.6875rem;
  }
}

@media (max-width: 576px) {
  .actions-grid {
    gap: var(--spacing-1);
  }
  
  .action-item {
    padding: var(--spacing-2);
  }
  
  .action-description {
    display: none;
  }
}
</style>