<template>
  <div class="layout-wrapper">
    <AppTopbar @menu-toggle="onMenuToggle" />
    <div class="layout-sidebar" :class="{ 'layout-sidebar-active': sidebarActive }">
      <AppSidebar />
    </div>
    <div class="layout-main-container">
      <div class="layout-main">
        <Breadcrumbs />
        <router-view />
      </div>
    </div>
    <div v-if="sidebarActive" class="layout-mask" @click="onMaskClick"></div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppTopbar from '@/components/layout/AppTopbar.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import Breadcrumbs from '@/components/common/Breadcrumbs.vue'

const sidebarActive = ref(false)

const onMenuToggle = () => {
  sidebarActive.value = !sidebarActive.value
}

const onMaskClick = () => {
  sidebarActive.value = false
}
</script>

<style scoped>
.layout-wrapper {
  display: flex;
  min-height: 100vh;
  position: relative;
  padding-top: 60px; /* Height of the topbar */
}

/* Sidebar styles */
.layout-sidebar {
  width: 250px;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  position: fixed;
  left: -250px;
  top: 60px; /* Below the topbar */
  bottom: 0;
  z-index: 999;
  transition: all 0.3s;
  overflow-y: auto;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

.layout-sidebar-active {
  left: 0;
}

/* Main content area */
.layout-main-container {
  flex: 1;
  margin-left: 0;
  min-height: calc(100vh - 60px);
  transition: margin-left 0.3s;
  background: #f8f9fa;
}

.layout-main {
  padding: 1.5rem;
  min-height: 100%;
}

/* Breadcrumb spacing */
.layout-main > :first-child {
  margin-top: 0;
}

/* Mask for mobile menu */
.layout-mask {
  position: fixed;
  top: 60px; /* Below the topbar */
  left: 0;
  width: 100%;
  height: calc(100% - 60px);
  background: rgba(0, 0, 0, 0.3);
  z-index: 998;
  display: none; /* Hidden by default, shown on mobile */
}

/* Desktop styles */
@media (min-width: 992px) {
  .layout-sidebar {
    position: fixed;
    left: 0;
    top: 60px; /* Below the topbar */
    height: calc(100vh - 60px);
  }
  
  .layout-main-container {
    margin-left: 250px; /* Same as sidebar width */
  }
  
  .layout-mask {
    display: none !important; /* Always hide on desktop */
  }
}

/* Responsive adjustments */
@media (max-width: 991px) {
  .layout-sidebar-active + .layout-mask {
    display: block; /* Show mask when sidebar is active on mobile */
  }
}
</style>