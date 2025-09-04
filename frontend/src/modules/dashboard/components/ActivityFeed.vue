<template>
  <Card class="activity-feed-card">
    <template #title>
      <div class="feed-header">
        <h3>Recent Activity</h3>
        <Button 
          icon="pi pi-refresh" 
          class="p-button-text p-button-sm"
          @click="refreshFeed"
          v-tooltip="'Refresh'"
        />
      </div>
    </template>
    <template #content>
      <div class="activity-list" v-if="activities.length > 0">
        <div 
          v-for="activity in activities" 
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-avatar" :class="activityTypeClass(activity.type)">
            <i :class="activityIcon(activity.type)"></i>
          </div>
          <div class="activity-content">
            <div class="activity-header">
              <h4 class="activity-title">{{ activity.title }}</h4>
              <small class="activity-time">{{ formatTime(activity.timestamp) }}</small>
            </div>
            <p class="activity-description">{{ activity.description }}</p>
            <div class="activity-meta" v-if="activity.amount || activity.user">
              <span v-if="activity.amount" class="activity-amount">
                {{ formatAmount(activity.amount) }}
              </span>
              <span v-if="activity.user" class="activity-user">
                by {{ activity.user }}
              </span>
            </div>
          </div>
          <div class="activity-status" v-if="activity.status">
            <Badge 
              :value="activity.status" 
              :severity="statusSeverity(activity.status)"
              class="activity-badge"
            />
          </div>
        </div>
      </div>
      <div v-else class="no-activity">
        <i class="pi pi-clock"></i>
        <p>No recent activity</p>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  activities: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['refresh'])

const refreshFeed = () => {
  emit('refresh')
}

const activityTypeClass = (type) => ({
  'avatar-transaction': type === 'transaction',
  'avatar-payment': type === 'payment',
  'avatar-invoice': type === 'invoice',
  'avatar-user': type === 'user',
  'avatar-system': type === 'system',
  'avatar-report': type === 'report'
})

const activityIcon = (type) => {
  switch (type) {
    case 'transaction': return 'pi pi-arrow-right-arrow-left'
    case 'payment': return 'pi pi-credit-card'
    case 'invoice': return 'pi pi-file-pdf'
    case 'user': return 'pi pi-user'
    case 'system': return 'pi pi-cog'
    case 'report': return 'pi pi-chart-bar'
    default: return 'pi pi-info-circle'
  }
}

const statusSeverity = (status) => {
  switch (status?.toLowerCase()) {
    case 'completed': return 'success'
    case 'pending': return 'warning'
    case 'failed': return 'danger'
    case 'cancelled': return 'secondary'
    default: return 'info'
  }
}

const formatTime = (timestamp) => {
  const now = new Date()
  const time = new Date(timestamp)
  const diff = now - time
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  
  return time.toLocaleDateString()
}

const formatAmount = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}
</script>

<style scoped>
.activity-feed-card {
  height: 100%;
}

.feed-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.feed-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
  max-height: 400px;
  overflow-y: auto;
  padding-right: var(--spacing-2);
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  border-radius: var(--border-radius-md);
  background: var(--surface-section);
  border: 1px solid var(--surface-border);
  transition: all 0.2s ease;
}

.activity-item:hover {
  background: var(--surface-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.activity-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.avatar-transaction {
  background: rgba(59, 130, 246, 0.1);
  color: var(--blue-500);
}

.avatar-payment {
  background: rgba(16, 185, 129, 0.1);
  color: var(--green-500);
}

.avatar-invoice {
  background: rgba(245, 158, 11, 0.1);
  color: var(--yellow-500);
}

.avatar-user {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.avatar-system {
  background: rgba(100, 116, 139, 0.1);
  color: var(--text-color-secondary);
}

.avatar-report {
  background: rgba(236, 72, 153, 0.1);
  color: #ec4899;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-1);
  gap: var(--spacing-2);
}

.activity-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
  line-height: 1.3;
}

.activity-time {
  font-size: 0.75rem;
  color: var(--text-color-muted);
  flex-shrink: 0;
}

.activity-description {
  font-size: 0.8125rem;
  color: var(--text-color-secondary);
  margin: 0 0 var(--spacing-2) 0;
  line-height: 1.4;
}

.activity-meta {
  display: flex;
  gap: var(--spacing-3);
  align-items: center;
}

.activity-amount {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary-600);
}

.activity-user {
  font-size: 0.75rem;
  color: var(--text-color-muted);
}

.activity-status {
  flex-shrink: 0;
}

.activity-badge {
  font-size: 0.6875rem;
}

.no-activity {
  text-align: center;
  padding: var(--spacing-8) var(--spacing-4);
  color: var(--text-color-secondary);
}

.no-activity i {
  font-size: 3rem;
  color: var(--text-color-muted);
  margin-bottom: var(--spacing-3);
}

.no-activity p {
  font-size: 1rem;
  margin: 0;
}

/* Custom scrollbar for activity list */
.activity-list::-webkit-scrollbar {
  width: 4px;
}

.activity-list::-webkit-scrollbar-track {
  background: var(--surface-section);
  border-radius: 2px;
}

.activity-list::-webkit-scrollbar-thumb {
  background: var(--surface-border);
  border-radius: 2px;
}

.activity-list::-webkit-scrollbar-thumb:hover {
  background: var(--text-color-muted);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .activity-item {
    padding: var(--spacing-2);
    gap: var(--spacing-2);
  }
  
  .activity-avatar {
    width: 32px;
    height: 32px;
    font-size: 0.875rem;
  }
  
  .activity-title {
    font-size: 0.8125rem;
  }
  
  .activity-description {
    font-size: 0.75rem;
  }
  
  .activity-list {
    max-height: 300px;
  }
}

@media (max-width: 576px) {
  .activity-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-1);
  }
  
  .activity-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-1);
  }
  
  .activity-status {
    align-self: flex-end;
    margin-top: var(--spacing-2);
  }
}
</style>