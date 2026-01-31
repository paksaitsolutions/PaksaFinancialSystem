<template>
  <div class="p-4">
    <Card>
      <template #header>
        <div class="flex justify-between items-center p-4">
          <h1 class="text-2xl font-semibold text-primary m-0">Notifications</h1>
          <Button 
            label="Mark All Read" 
            icon="pi pi-check" 
            class="btn-primary"
            @click="markAllAsRead"
            :disabled="unreadCount === 0"
          />
        </div>
      </template>
      
      <template #content>
        <div v-if="notifications.length > 0" class="flex flex-col gap-md">
          <div 
            v-for="notification in notifications" 
            :key="notification.id"
            class="notification-item"
            :class="{ 'notification-unread': !notification.is_read }"
          >
            <div class="notification-icon">
              <i :class="getNotificationIcon(notification.type)" :style="getIconColor(notification.type)"></i>
            </div>
            <div class="notification-content">
              <h3 class="notification-title">{{ notification.title }}</h3>
              <p class="notification-message">{{ notification.message }}</p>
              <small class="notification-date">{{ formatDate(notification.created_at) }}</small>
            </div>
            <Button 
              v-if="!notification.is_read"
              icon="pi pi-check" 
              text 
              size="small"
              class="notification-action"
              @click="markAsRead(notification.id)"
            />
          </div>
        </div>
        
        <div v-else class="empty-state">
          <i class="pi pi-bell empty-icon"></i>
          <p class="empty-text">No notifications</p>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useNotifications } from '@/composables/useNotifications'

const { notifications, unreadCount, fetchNotifications, markAsRead, markAllAsRead } = useNotifications()

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'warning': return 'pi pi-exclamation-triangle'
    case 'error': return 'pi pi-times-circle'
    case 'success': return 'pi pi-check-circle'
    default: return 'pi pi-info-circle'
  }
}

const getIconColor = (type: string) => {
  switch (type) {
    case 'warning': return { color: 'var(--warning-500)' }
    case 'error': return { color: 'var(--error-500)' }
    case 'success': return { color: 'var(--success-500)' }
    default: return { color: 'var(--info-500)' }
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.notification-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--surface-0);
  border-radius: var(--border-radius);
  border: 1px solid var(--surface-200);
  transition: all var(--transition-fast);
}

.notification-unread {
  border-left: 4px solid var(--primary-500);
  background: var(--primary-50);
}

.notification-item:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.notification-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius-full);
  background: var(--surface-100);
  font-size: 1.25rem;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  line-height: var(--line-height-tight);
}

.notification-message {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--text-color-secondary);
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
}

.notification-date {
  color: var(--text-color-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.notification-action {
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-xl);
}

.empty-icon {
  font-size: 4rem;
  color: var(--surface-400);
  margin-bottom: var(--spacing-lg);
}

.empty-text {
  font-size: var(--font-size-lg);
  color: var(--text-color-secondary);
  font-weight: var(--font-weight-medium);
  margin: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .notification-item {
    padding: var(--spacing-md);
    gap: var(--spacing-sm);
  }
  
  .notification-icon {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
  
  .notification-title {
    font-size: var(--font-size-base);
  }
  
  .notification-message {
    font-size: var(--font-size-sm);
  }
}
</style>