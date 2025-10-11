<template>
  <teleport to="body">
    <div class="notification-container">
      <transition-group name="notification" tag="div">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification"
          :class="[
            `notification-${notification.type}`,
            { 'notification-dismissible': notification.dismissible }
          ]"
        >
          <div class="notification-icon">
            <i :class="getIcon(notification.type)"></i>
          </div>
          
          <div class="notification-content">
            <h4 v-if="notification.title" class="notification-title">
              {{ notification.title }}
            </h4>
            <p class="notification-message">{{ notification.message }}</p>
          </div>
          
          <button
            v-if="notification.dismissible"
            class="notification-close"
            @click="dismiss(notification.id)"
          >
            <i class="pi pi-times"></i>
          </button>
        </div>
      </transition-group>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  duration?: number
  dismissible?: boolean
}

const notifications = ref<Notification[]>([])

const getIcon = (type: string) => {
  const icons = {
    success: 'pi pi-check-circle',
    error: 'pi pi-times-circle',
    warning: 'pi pi-exclamation-triangle',
    info: 'pi pi-info-circle'
  }
  return icons[type as keyof typeof icons] || icons.info
}

const add = (notification: Omit<Notification, 'id'>) => {
  const id = Date.now().toString()
  const newNotification: Notification = {
    id,
    dismissible: true,
    duration: 5000,
    ...notification
  }
  
  notifications.value.push(newNotification)
  
  if (newNotification.duration && newNotification.duration > 0) {
    setTimeout(() => {
      dismiss(id)
    }, newNotification.duration)
  }
}

const dismiss = (id: string) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index > -1) {
    notifications.value.splice(index, 1)
  }
}

const clear = () => {
  notifications.value = []
}

// Convenience methods
const success = (message: string, title?: string, options?: Partial<Notification>) => {
  add({ type: 'success', message, title, ...options })
}

const error = (message: string, title?: string, options?: Partial<Notification>) => {
  add({ type: 'error', message, title, duration: 0, ...options })
}

const warning = (message: string, title?: string, options?: Partial<Notification>) => {
  add({ type: 'warning', message, title, ...options })
}

const info = (message: string, title?: string, options?: Partial<Notification>) => {
  add({ type: 'info', message, title, ...options })
}

// Expose methods for external use
defineExpose({
  add,
  dismiss,
  clear,
  success,
  error,
  warning,
  info
})
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: var(--spacing-lg);
  right: var(--spacing-lg);
  z-index: 10000;
  max-width: 400px;
  width: 100%;
}

.notification {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
  background: var(--surface-0);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  border-left: 4px solid;
  min-height: 64px;
}

.notification-success {
  border-left-color: #10b981;
}

.notification-error {
  border-left-color: #ef4444;
}

.notification-warning {
  border-left-color: #f59e0b;
}

.notification-info {
  border-left-color: #3b82f6;
}

.notification-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-success .notification-icon {
  color: #10b981;
}

.notification-error .notification-icon {
  color: #ef4444;
}

.notification-warning .notification-icon {
  color: #f59e0b;
}

.notification-info .notification-icon {
  color: #3b82f6;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
}

.notification-message {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--text-color-secondary);
  line-height: 1.4;
}

.notification-close {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border: none;
  background: none;
  color: var(--text-color-secondary);
  cursor: pointer;
  border-radius: var(--border-radius);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.notification-close:hover {
  background: var(--surface-100);
  color: var(--text-color);
}

/* Animations */
.notification-enter-active,
.notification-leave-active {
  transition: all var(--transition-normal);
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.notification-move {
  transition: transform var(--transition-normal);
}

@media (max-width: 768px) {
  .notification-container {
    left: var(--spacing-md);
    right: var(--spacing-md);
    max-width: none;
  }
  
  .notification {
    margin-bottom: var(--spacing-sm);
  }
}
</style>