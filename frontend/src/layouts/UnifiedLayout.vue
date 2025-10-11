<template>
  <UnifiedTheme>
    <div class="unified-layout">
      <!-- Navigation -->
      <UnifiedNavigation />
      
      <!-- Main Content Area -->
      <main class="main-content" :class="{ 'nav-collapsed': navigationCollapsed }">
        <!-- Top Bar -->
        <header class="top-bar">
          <div class="top-bar-left">
            <Button 
              icon="pi pi-bars" 
              class="nav-toggle-btn"
              text
              @click="toggleNavigation"
            />
            <div class="breadcrumb">
              <span v-for="(crumb, index) in breadcrumbs" :key="index" class="breadcrumb-item">
                <router-link v-if="crumb.to" :to="crumb.to" class="breadcrumb-link">
                  {{ crumb.label }}
                </router-link>
                <span v-else class="breadcrumb-text">{{ crumb.label }}</span>
                <i v-if="index < breadcrumbs.length - 1" class="pi pi-chevron-right breadcrumb-separator"></i>
              </span>
            </div>
          </div>
          
          <div class="top-bar-right">
            <Button 
              icon="pi pi-bell" 
              class="notification-btn"
              text
              :badge="unreadNotifications > 0 ? unreadNotifications.toString() : undefined"
            />
            <Button 
              icon="pi pi-user" 
              class="user-menu-btn"
              text
              @click="showUserMenu = !showUserMenu"
            />
          </div>
        </header>
        
        <!-- Page Content -->
        <div class="page-content">
          <router-view v-slot="{ Component }">
            <Suspense>
              <template #default>
                <component :is="Component" />
              </template>
              <template #fallback>
                <UnifiedLoading type="skeleton" :skeleton-lines="5" />
              </template>
            </Suspense>
          </router-view>
        </div>
      </main>
      
      <!-- Global Notifications -->
      <UnifiedNotification />
      
      <!-- User Menu Modal -->
      <UnifiedModal
        v-model:visible="showUserMenu"
        title="User Menu"
        size="sm"
        :show-footer="false"
      >
        <div class="user-menu">
          <div class="user-info">
            <div class="user-avatar">
              <i class="pi pi-user"></i>
            </div>
            <div class="user-details">
              <div class="user-name">{{ user?.name || 'User' }}</div>
              <div class="user-email">{{ user?.email || 'user@example.com' }}</div>
            </div>
          </div>
          
          <div class="menu-items">
            <button class="menu-item" @click="goToProfile">
              <i class="pi pi-user"></i>
              <span>Profile</span>
            </button>
            <button class="menu-item" @click="goToSettings">
              <i class="pi pi-cog"></i>
              <span>Settings</span>
            </button>
            <button class="menu-item" @click="toggleTheme">
              <i class="pi pi-moon"></i>
              <span>Toggle Theme</span>
            </button>
            <hr class="menu-divider">
            <button class="menu-item logout" @click="logout">
              <i class="pi pi-sign-out"></i>
              <span>Logout</span>
            </button>
          </div>
        </div>
      </UnifiedModal>
    </div>
  </UnifiedTheme>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/modules/auth/store'
import { useTheme } from '@/composables/useTheme'
import { useUnifiedNotifications } from '@/composables/useUnifiedNotifications'
import Button from 'primevue/button'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { toggleTheme } = useTheme()
const { notifications } = useUnifiedNotifications()

const navigationCollapsed = ref(false)
const showUserMenu = ref(false)

const user = computed(() => authStore.user)
const unreadNotifications = computed(() => notifications.value.length)

const breadcrumbs = computed(() => {
  const crumbs = []
  const pathSegments = route.path.split('/').filter(Boolean)
  
  crumbs.push({ label: 'Home', to: '/dashboard' })
  
  let currentPath = ''
  pathSegments.forEach((segment, index) => {
    currentPath += `/${segment}`
    const isLast = index === pathSegments.length - 1
    
    crumbs.push({
      label: segment.charAt(0).toUpperCase() + segment.slice(1).replace('-', ' '),
      to: isLast ? undefined : currentPath
    })
  })
  
  return crumbs
})

const toggleNavigation = () => {
  navigationCollapsed.value = !navigationCollapsed.value
}

const goToProfile = () => {
  router.push('/profile')
  showUserMenu.value = false
}

const goToSettings = () => {
  router.push('/settings')
  showUserMenu.value = false
}

const logout = () => {
  authStore.logout()
  showUserMenu.value = false
}
</script>

<style scoped>
.unified-layout {
  display: flex;
  min-height: 100vh;
  background: var(--surface-50);
}

.main-content {
  flex: 1;
  margin-left: 280px;
  display: flex;
  flex-direction: column;
  transition: margin-left var(--transition-normal);
}

.nav-collapsed .main-content {
  margin-left: 72px;
}

.top-bar {
  height: 64px;
  background: var(--surface-0);
  border-bottom: 1px solid var(--surface-200);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-lg);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.nav-toggle-btn {
  display: none;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.breadcrumb-link {
  color: var(--primary-600);
  text-decoration: none;
  font-size: var(--font-size-sm);
  
  &:hover {
    text-decoration: underline;
  }
}

.breadcrumb-text {
  color: var(--text-color);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.breadcrumb-separator {
  color: var(--text-color-secondary);
  font-size: 12px;
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.page-content {
  flex: 1;
  padding: var(--spacing-xl);
  overflow-y: auto;
}

.user-menu {
  padding: var(--spacing-md);
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--surface-50);
  border-radius: var(--border-radius);
  margin-bottom: var(--spacing-lg);
}

.user-avatar {
  width: 48px;
  height: 48px;
  background: var(--primary-100);
  color: var(--primary-600);
  border-radius: var(--border-radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  margin-bottom: var(--spacing-xs);
}

.user-email {
  font-size: var(--font-size-sm);
  color: var(--text-color-secondary);
}

.menu-items {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: none;
  border: none;
  border-radius: var(--border-radius);
  color: var(--text-color);
  cursor: pointer;
  transition: all var(--transition-fast);
  width: 100%;
  text-align: left;
  
  &:hover {
    background: var(--surface-100);
  }
  
  &.logout {
    color: var(--error-500);
    
    &:hover {
      background: rgba(239, 68, 68, 0.1);
    }
  }
}

.menu-divider {
  border: none;
  border-top: 1px solid var(--surface-200);
  margin: var(--spacing-sm) 0;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
  
  .nav-toggle-btn {
    display: flex;
  }
  
  .breadcrumb {
    display: none;
  }
  
  .page-content {
    padding: var(--spacing-lg);
  }
}
</style>