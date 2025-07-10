<template>
  <div class="app-layout" :class="[layout, { 'rtl': isRTL, 'sidebar-collapsed': isSidebarCollapsed }]">
    <!-- App Header -->
    <AppHeader 
      :is-sidebar-collapsed="isSidebarCollapsed"
      @toggle-sidebar="toggleSidebar"
      @toggle-mobile-menu="toggleMobileMenu"
    />
    
    <div class="app-main">
      <!-- Sidebar -->
      <AppSidebar 
        :collapsed="isSidebarCollapsed"
        :is-mobile-menu-open="isMobileMenuOpen"
        @navigate="closeMobileMenu"
      />
      
      <!-- Main Content -->
      <main class="main-content">
        <!-- Breadcrumbs -->
        <Breadcrumb :model="breadcrumbs" class="p-3" />
        
        <!-- Page Content -->
        <div class="content-container">
          <router-view v-slot="{ Component, route }">
            <transition name="fade" mode="out-in">
              <component :is="Component" :key="route.fullPath" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>
    
    <!-- App Footer -->
    <AppFooter />
    
    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <ProgressSpinner />
      <p v-if="loadingText" class="mt-3">{{ loadingText }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAppStore } from '@/store/app';
import AppHeader from '@/components/layout/AppHeader.vue';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import AppFooter from '@/components/layout/AppFooter.vue';
import Breadcrumb from 'primevue/breadcrumb';
import ProgressSpinner from 'primevue/progressspinner';

const appStore = useAppStore();
const route = useRoute();

// State
const isMobileMenuOpen = ref(false);

// Computed
const isSidebarCollapsed = computed(() => appStore.sidebarCollapsed);
const isLoading = computed(() => appStore.isLoading);
const loadingText = computed(() => appStore.loadingText);
const layout = computed(() => appStore.currentLayout);
const isRTL = computed(() => appStore.isRTL);
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(record => record.meta.breadcrumb);
  return matched.map(record => ({
    label: String(record.meta.breadcrumb),
    to: record.path
  }));
});

// Methods
const toggleSidebar = () => {
  appStore.toggleSidebar();
};

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
};

// Watch route changes to close mobile menu
watch(() => route.path, () => {
  closeMobileMenu();
});
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--surface-ground);
  transition: margin-left 0.3s ease;
}

.app-main {
  display: flex;
  flex: 1;
  margin-top: 4rem; /* Height of header */
  position: relative;
}

.main-content {
  flex: 1;
  padding: 1rem;
  margin-left: 250px; /* Width of sidebar */
  transition: margin-left 0.3s ease;
  min-height: calc(100vh - 4rem);
  overflow-x: hidden;
}

/* Sidebar collapsed */
.sidebar-collapsed .main-content {
  margin-left: 80px;
}

/* RTL support */
.rtl .main-content {
  margin-left: 0;
  margin-right: 250px;
}

.rtl.sidebar-collapsed .main-content {
  margin-right: 80px;
}

/* Content container */
.content-container {
  background: var(--surface-card);
  border-radius: 6px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
  min-height: calc(100% - 2rem);
}

/* Loading overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1100;
  backdrop-filter: blur(2px);
}

/* Responsive */
@media (max-width: 992px) {
  .main-content {
    margin-left: 0 !important;
  }
  
  .rtl .main-content {
    margin-right: 0 !important;
  }
  
  .sidebar-collapsed .main-content {
    margin-left: 0 !important;
  }
  
  .rtl.sidebar-collapsed .main-content {
    margin-right: 0 !important;
  }
}
</style>
