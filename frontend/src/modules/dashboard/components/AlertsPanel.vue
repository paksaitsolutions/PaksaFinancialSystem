<template>
  <Card class="alerts-panel">
    <template #title>
      <div class="alerts-header">
        <h3>System Alerts</h3>
        <Badge :value="alerts.length" severity="warning" />
      </div>
    </template>
    <template #content>
      <div class="alerts-list">
        <div 
          v-for="alert in alerts" 
          :key="alert.id"
          class="alert-item"
          :class="alertClass(alert.severity)"
        >
          <div class="alert-icon">
            <i :class="alertIcon(alert.severity)"></i>
          </div>
          <div class="alert-content">
            <h4 class="alert-title">{{ alert.title }}</h4>
            <p class="alert-message">{{ alert.message }}</p>
            <small class="alert-time">{{ formatTime(alert.created_at) }}</small>
          </div>
          <div class="alert-actions">
            <Button 
              icon="pi pi-times" 
              class="p-button-text p-button-sm"
              @click="$emit('dismiss', alert.id)"
              v-tooltip="'Dismiss'"
            />
          </div>
        </div>
      </div>
      <div v-if="alerts.length === 0" class="no-alerts">
        <i class="pi pi-check-circle"></i>
        <p>No active alerts</p>
      </div>
    </template>
  </Card>
</template>

<script setup>

const props = defineProps({
  alerts: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['dismiss'])

const alertClass = (severity) => ({
  'alert-critical': severity === 'critical',
  'alert-high': severity === 'high',
  'alert-medium': severity === 'medium',
  'alert-low': severity === 'low',
  'alert-info': severity === 'info'
})

const alertIcon = (severity) => {
  switch (severity) {
    case 'critical': return 'pi pi-exclamation-triangle'
    case 'high': return 'pi pi-exclamation-circle'
    case 'medium': return 'pi pi-info-circle'
    case 'low': return 'pi pi-info'
    default: return 'pi pi-info-circle'
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}
</script>

<style scoped>
.alerts-panel {
  margin-bottom: var(--spacing-6);
}

.alerts-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-3);
}

.alerts-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  border-radius: var(--border-radius-md);
  border-left: 4px solid;
  background: var(--surface-section);
  transition: all 0.2s ease;
}

.alert-item:hover {
  background: var(--surface-hover);
  transform: translateX(4px);
}

.alert-critical {
  border-left-color: var(--red-500);
  background: rgba(239, 68, 68, 0.05);
}

.alert-high {
  border-left-color: #f97316;
  background: rgba(249, 115, 22, 0.05);
}

.alert-medium {
  border-left-color: var(--yellow-500);
  background: rgba(245, 158, 11, 0.05);
}

.alert-low {
  border-left-color: var(--blue-500);
  background: rgba(59, 130, 246, 0.05);
}

.alert-info {
  border-left-color: #6366f1;
  background: rgba(99, 102, 241, 0.05);
}

.alert-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
}

.alert-critical .alert-icon {
  background: rgba(239, 68, 68, 0.1);
  color: var(--red-500);
}

.alert-high .alert-icon {
  background: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

.alert-medium .alert-icon {
  background: rgba(245, 158, 11, 0.1);
  color: var(--yellow-500);
}

.alert-low .alert-icon {
  background: rgba(59, 130, 246, 0.1);
  color: var(--blue-500);
}

.alert-info .alert-icon {
  background: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 var(--spacing-1) 0;
}

.alert-message {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin: 0 0 var(--spacing-2) 0;
  line-height: 1.4;
}

.alert-time {
  font-size: 0.75rem;
  color: var(--text-color-muted);
}

.alert-actions {
  flex-shrink: 0;
}

.no-alerts {
  text-align: center;
  padding: var(--spacing-8) var(--spacing-4);
  color: var(--text-color-secondary);
}

.no-alerts i {
  font-size: 3rem;
  color: var(--green-500);
  margin-bottom: var(--spacing-3);
}

.no-alerts p {
  font-size: 1rem;
  margin: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .alert-item {
    padding: var(--spacing-3);
    gap: var(--spacing-2);
  }
  
  .alert-icon {
    width: 32px;
    height: 32px;
    font-size: 1rem;
  }
  
  .alert-title {
    font-size: 0.8125rem;
  }
  
  .alert-message {
    font-size: 0.8125rem;
  }
}

@media (max-width: 576px) {
  .alerts-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-2);
  }
  
  .alert-item {
    flex-direction: column;
    text-align: center;
  }
  
  .alert-actions {
    align-self: flex-end;
  }
}
</style>