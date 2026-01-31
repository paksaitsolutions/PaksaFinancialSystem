<template>
  <div class="layout-topbar">
    <Button 
      icon="pi pi-bars" 
      class="p-button-text menu-toggle"
      @click="$emit('menu-toggle')"
    />
    
    <router-link to="/" class="logo">
      <i class="pi pi-chart-line logo-icon"></i>
      <span class="logo-text">Paksa Financial</span>
    </router-link>

    <div class="search-container">
      <span class="p-input-icon-left">
        <i class="pi pi-search"></i>
        <InputText 
          :model-value="searchQuery"
          @update:model-value="(val: string | undefined) => { searchQuery = val || '' }"
          placeholder="Search..."
          class="search-input"
        />
      </span>
    </div>

    <div class="topbar-actions">
      <Button 
        icon="pi pi-plus" 
        label="New"
        class="p-button-sm new-btn"
        @click="toggleQuickMenu"
      />
      <Menu ref="quickMenu" :model="quickMenuItems" :popup="true" />
      
      <Button 
        icon="pi pi-bell" 
        class="p-button-text p-button-rounded"
        :badge="unreadCount > 0 ? unreadCount.toString() : undefined"
        @click="toggleNotifications"
      />
      <Menu ref="notificationMenu" :model="notificationItems" :popup="true" />
      
      <div class="user-avatar" @click="toggleUserMenu">
        <Avatar :label="userInitials" />
      </div>
      <Menu ref="menu" :model="userMenuItems" :popup="true" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotifications } from '@/composables/useNotifications'

defineEmits(['menu-toggle'])

const router = useRouter()
const authStore = useAuthStore()
const { notifications, unreadCount, fetchNotifications, markAsRead } = useNotifications()
const menu = ref()
const quickMenu = ref()
const notificationMenu = ref()

const searchQuery = ref<string>('')

const userName = computed(() => {
  return authStore.user?.full_name || 'User'
})

const userInitials = computed((): string => {
  return userName.value?.split(' ').map(n => n[0] || '').join('').toUpperCase() || 'U'
})

onMounted(() => {
  fetchNotifications()
})

const quickMenuItems = [
  {
    label: 'New Invoice',
    icon: 'pi pi-file-plus',
    command: () => router.push('/ap/invoices')
  },
  {
    label: 'New Bill',
    icon: 'pi pi-receipt',
    command: () => router.push('/ap/create-bill')
  },
  {
    label: 'New Journal Entry',
    icon: 'pi pi-book',
    command: () => router.push('/accounting/journal-entry')
  },
  {
    label: 'New Customer',
    icon: 'pi pi-user-plus',
    command: () => router.push('/ar/customers')
  }
]

const notificationItems = computed(() => {
  const items = notifications.value.slice(0, 5).map(notification => ({
    label: notification.title,
    icon: getNotificationIcon(notification.type),
    command: () => {
      markAsRead(notification.id)
      // Navigate based on notification type
      if (notification.title.includes('Invoice')) router.push('/ar')
      else if (notification.title.includes('Bill') || notification.title.includes('Approval')) router.push('/ap')
      else if (notification.title.includes('Bank')) router.push('/cash')
    }
  }))
  
  if (items.length > 0) {
    items.push({ separator: true })
  }
  
  items.push({
    label: 'View All Notifications',
    icon: 'pi pi-bell',
    command: () => router.push('/notifications')
  })
  
  return items
})

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'warning': return 'pi pi-exclamation-triangle'
    case 'error': return 'pi pi-times-circle'
    case 'success': return 'pi pi-check-circle'
    default: return 'pi pi-info-circle'
  }
}

const userMenuItems = [
  {
    label: 'My Profile',
    icon: 'pi pi-user',
    command: () => router.push('/profile')
  },
  {
    label: 'Account Settings',
    icon: 'pi pi-cog',
    command: () => router.push('/settings')
  },
  {
    label: 'Help & Support',
    icon: 'pi pi-question-circle',
    command: () => router.push('/help')
  },
  { separator: true },
  {
    label: 'Sign Out',
    icon: 'pi pi-sign-out',
    command: () => {
      authStore.logout()
      router.push('/auth/login')
    }
  }
]

// Search functionality is handled by the input's v-model
// const performSearch = () => {
//   if (searchQuery.value.trim()) {
//     console.log('Searching for:', searchQuery.value)
//     // Implement global search functionality
//   }
// }

const toggleUserMenu = (event: Event) => {
  menu.value.toggle(event)
}

const toggleQuickMenu = (event: Event) => {
  quickMenu.value.toggle(event)
}

const toggleNotifications = (event: Event) => {
  notificationMenu.value.toggle(event)
}
</script>

<style scoped>
.layout-topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  z-index: var(--z-fixed);
  background: var(--surface-0);
  border-bottom: 1px solid var(--surface-200);
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-lg);
  gap: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  font-family: var(--font-family);
}

@media (min-width: 992px) {
  .layout-topbar {
    left: 250px;
  }
}

.menu-toggle {
  display: block;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  text-decoration: none;
  color: var(--text-color);
  font-weight: var(--font-weight-semibold);
}

.logo-icon {
  font-size: var(--font-size-2xl);
  color: var(--primary-600);
}

.logo-text {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
}

.search-container {
  flex: 1;
  max-width: 500px;
  margin: 0 var(--spacing-lg);
  position: relative;
}

.search-container .p-input-icon-left {
  display: flex;
  align-items: center;
  width: 100%;
}

.search-container .pi-search {
  position: absolute;
  left: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-color-secondary);
}

.search-input {
  width: 100%;
  max-width: 100%;
  border-radius: var(--border-radius-full);
  padding: var(--spacing-sm) var(--spacing-lg) var(--spacing-sm) calc(var(--spacing-lg) * 2);
  height: 36px;
  border: 1px solid var(--surface-300);
  background: var(--surface-0);
  color: var(--text-color);
  font-family: var(--font-family);
  transition: all var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-left: auto;
}

.new-btn {
  background: var(--primary-600);
  border-color: var(--primary-600);
  color: white;
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
}

.new-btn:hover {
  background: var(--primary-700);
  border-color: var(--primary-700);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.user-avatar {
  background: var(--primary-600) !important;
  color: white !important;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.user-avatar:hover {
  background: var(--primary-700) !important;
  transform: scale(1.05);
}

@media (min-width: 992px) {
  .menu-toggle {
    display: none;
  }
}

@media (max-width: 768px) {
  .search-container {
    display: none;
  }
}

:deep(.p-menu) {
  min-width: 200px;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 9999;
}

:deep(.p-menuitem-link) {
  padding: 0.75rem 1rem;
}
</style>