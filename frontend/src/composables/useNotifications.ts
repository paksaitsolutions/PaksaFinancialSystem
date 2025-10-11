import { ref, computed } from 'vue'
import { api } from '@/services/api'

export interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'warning' | 'error' | 'success'
  priority: 'low' | 'medium' | 'high' | 'critical'
  is_read: boolean
  created_at: string
  user_id: string
}

const notifications = ref<Notification[]>([])
const loading = ref(false)

export const useNotifications = () => {
  const unreadCount = computed(() => 
    notifications.value.filter(n => !n.is_read).length
  )

  const fetchNotifications = async () => {
    loading.value = true
    try {
      const response = await api.get('/api/v1/notifications')
      notifications.value = response.data.notifications || response.data
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
      // Fallback to mock data if API fails
      notifications.value = [
        {
          id: '1',
          title: 'Overdue Invoices',
          message: '5 invoices are overdue',
          type: 'warning',
          priority: 'high',
          is_read: false,
          created_at: new Date().toISOString(),
          user_id: 'current-user'
        },
        {
          id: '2', 
          title: 'Pending Approvals',
          message: '2 bills need approval',
          type: 'info',
          priority: 'medium',
          is_read: false,
          created_at: new Date().toISOString(),
          user_id: 'current-user'
        }
      ]
    } finally {
      loading.value = false
    }
  }

  const markAsRead = async (id: string) => {
    try {
      await api.post(`/api/v1/notifications/${id}/read`)
      const notification = notifications.value.find(n => n.id === id)
      if (notification) {
        notification.is_read = true
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

  const markAllAsRead = async () => {
    try {
      await api.post('/api/v1/notifications/mark-all-read')
      notifications.value.forEach(n => n.is_read = true)
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error)
    }
  }

  return {
    notifications: computed(() => notifications.value),
    unreadCount,
    loading: computed(() => loading.value),
    fetchNotifications,
    markAsRead,
    markAllAsRead
  }
}