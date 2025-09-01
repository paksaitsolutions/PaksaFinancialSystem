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
        :badge="notificationCount.toString()"
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import InputText from 'primevue/inputtext'
import Avatar from 'primevue/avatar'
import Menu from 'primevue/menu'
import Button from 'primevue/button'

defineEmits(['menu-toggle'])

const router = useRouter()
const authStore = useAuthStore()
const menu = ref()
const quickMenu = ref()
const notificationMenu = ref()

const searchQuery = ref<string>('')
const notificationCount = ref(3)
const userName = ref('John Doe')
// User role is not currently used but kept for future use
// const userRole = ref('Financial Manager')

const userInitials = computed((): string => {
  return userName.value?.split(' ').map(n => n[0] || '').join('').toUpperCase() || 'US'
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

const notificationItems = [
  {
    label: 'Overdue Invoices',
    icon: 'pi pi-exclamation-triangle',
    badge: '5',
    command: () => router.push('/ar')
  },
  {
    label: 'Pending Approvals',
    icon: 'pi pi-clock',
    badge: '2',
    command: () => router.push('/ap')
  },
  {
    label: 'Bank Reconciliation',
    icon: 'pi pi-check-circle',
    command: () => router.push('/cash')
  },
  { separator: true },
  {
    label: 'View All Notifications',
    icon: 'pi pi-bell',
    command: () => console.log('View all notifications')
  }
]

const userMenuItems = [
  {
    label: 'My Profile',
    icon: 'pi pi-user',
    command: () => console.log('Navigate to profile')
  },
  {
    label: 'Account Settings',
    icon: 'pi pi-cog',
    command: () => router.push('/settings')
  },
  {
    label: 'Help & Support',
    icon: 'pi pi-question-circle',
    command: () => console.log('Open help')
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
  z-index: 1001;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  padding: 0 1rem;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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
  gap: 0.5rem;
  text-decoration: none;
  color: #1f2937;
  font-weight: 600;
}

.logo-icon {
  font-size: 1.5rem;
  color: #3b82f6;
}

.logo-text {
  font-size: 1.1rem;
}

.search-container {
  flex: 1;
  max-width: 500px;
  margin: 0 1rem;
  position: relative;
}

.search-container .p-input-icon-left {
  display: flex;
  align-items: center;
  width: 100%;
}

.search-container .pi-search {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6b7280;
}

.search-input {
  width: 100%;
  max-width: 100%;
  border-radius: 20px;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  height: 36px;
  border: 1px solid #d1d5db;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 0.2rem rgba(59, 130, 246, 0.25);
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: auto;
}

.new-btn {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.user-avatar {
  background: #3b82f6 !important;
  color: white !important;
  cursor: pointer;
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