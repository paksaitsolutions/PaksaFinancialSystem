<template>
  <div class="layout-wrapper">
    <AppTopbar @menu-toggle="onMenuToggle" />
    <div class="layout-sidebar" :class="{ 'layout-sidebar-active': sidebarActive }">
      <AppSidebar />
    </div>
    <div class="layout-main-container">
      <div class="layout-main">
        <Breadcrumbs />
        <div class="page-content">
          <router-view v-slot="{ Component }">
            <component :is="Component" />
          </router-view>
        </div>
      </div>
    </div>
    <div v-if="sidebarActive" class="layout-mask" @click="onMaskClick"></div>
    
    <!-- AI Assistant Component -->
    <AIAssistant />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppTopbar from '@/components/layout/AppTopbar.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import Breadcrumbs from '@/components/common/Breadcrumbs.vue'
import AIAssistant from '@/components/ai/AIAssistant.vue'

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
  padding-top: 60px;
  background: var(--surface-50);
  font-family: var(--font-family);
}

/* Sidebar styles */
.layout-sidebar {
  width: 250px;
  background: var(--surface-card, #ffffff);
  border-right: 1px solid var(--surface-border, #e5e7eb);
  position: fixed;
  left: -250px;
  top: 60px;
  bottom: 0;
  z-index: 999;
  transition: all 0.3s ease;
  overflow-y: auto;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.layout-sidebar-active {
  left: 0;
}

/* Main content area */
.layout-main-container {
  flex: 1;
  margin-left: 0;
  min-height: calc(100vh - 60px);
  transition: margin-left 0.3s ease;
  background: var(--surface-50);
}

.layout-main {
  padding: 0;
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.page-content {
  flex: 1;
  padding: var(--spacing-lg);
  background: var(--surface-50);
  min-height: calc(100vh - 120px);
}

/* Breadcrumb styling */
:deep(.breadcrumb-container) {
  background: var(--surface-0);
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--surface-200);
  margin: 0;
}

/* Mask for mobile menu */
.layout-mask {
  position: fixed;
  top: 60px;
  left: 0;
  width: 100%;
  height: calc(100% - 60px);
  background: rgba(0, 0, 0, 0.3);
  z-index: 998;
  display: none;
}

/* Desktop styles */
@media (min-width: 992px) {
  .layout-sidebar {
    position: fixed;
    left: 0;
    top: 60px;
    height: calc(100vh - 60px);
  }
  
  .layout-main-container {
    margin-left: 250px;
  }
  
  .layout-mask {
    display: none !important;
  }
}

/* Mobile styles */
@media (max-width: 991px) {
  .layout-sidebar-active + .layout-main-container + .layout-mask {
    display: block;
  }
  
  .page-content {
    padding: 1rem;
  }
}

/* Global page styling */
:deep(.p-card) {
  margin-bottom: var(--spacing-lg);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--surface-200);
}

:deep(.p-card .p-card-header) {
  background: var(--surface-0);
  border-bottom: 1px solid var(--surface-200);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius) var(--border-radius) 0 0;
}

:deep(.p-card .p-card-content) {
  padding: var(--spacing-lg);
}

:deep(.p-card .p-card-title) {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color, #1e293b);
  margin: 0;
}

/* Grid system enhancements */
:deep(.grid) {
  margin: 0 calc(-1 * var(--spacing-sm));
}

:deep(.grid > [class*="col-"]) {
  padding: 0 var(--spacing-sm);
}

:deep(.grid .p-card) {
  height: 100%;
  margin-bottom: var(--spacing-md);
}

/* Button styling */
:deep(.p-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
}

:deep(.p-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Input styling */
:deep(.p-inputtext) {
  border-radius: 8px;
  border: 1px solid var(--surface-border, #e5e7eb);
  transition: all 0.2s ease;
}

:deep(.p-inputtext:focus) {
  border-color: var(--primary-color, #3b82f6);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* DataTable styling */
:deep(.p-datatable) {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--surface-border, #e5e7eb);
}

:deep(.p-datatable .p-datatable-header) {
  background: var(--surface-section, #f8f9fa);
  border-bottom: 1px solid var(--surface-border, #e5e7eb);
  padding: 1rem 1.5rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background: var(--surface-section, #f8f9fa);
  color: var(--text-color-secondary, #64748b);
  font-weight: 600;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--surface-border, #e5e7eb);
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--surface-border, #e5e7eb);
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background: var(--surface-hover, #f1f5f9);
}
</style>