<template>
  <div class="sidebar">
    <div class="sidebar-content">
      <div v-for="item in sidebarModules" :key="item.title">
        <div v-if="!item.children" class="menu-item">
          <router-link 
            :to="item.to" 
            class="p-ripple p-d-flex p-ai-center p-p-3"
            :class="{ 'active-route': isActive(item) }"
          >
            <i :class="item.icon" class="p-mr-2"></i>
            <span>{{ item.title }}</span>
          </router-link>
        </div>
        
        <div v-else class="menu-item">
          <div 
            class="p-d-flex p-ai-center p-p-3 menu-header"
            @click="toggleExpand(item)"
          >
            <i :class="item.icon" class="p-mr-2"></i>
            <span class="p-mr-auto">{{ item.title }}</span>
            <i :class="expanded[item.title] ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"></i>
          </div>
          
          <div v-if="expanded[item.title]" class="submenu">
            <router-link 
              v-for="child in item.children" 
              :key="child.title"
              :to="child.to"
              class="p-ripple p-d-flex p-ai-center p-p-3 p-pl-5"
              :class="{ 'active-route': isActive(child) }"
            >
              <i :class="child.icon" class="p-mr-2"></i>
              <span>{{ child.title }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useRoute } from 'vue-router';
import { sidebarModules } from '@/utils/sidebarModules';


const route = useRoute();
const drawer = ref(true);
const expanded = reactive<Record<string, boolean>>({});

// Initialize expanded state
sidebarModules.forEach(item => {
  if (item.children) {
    expanded[item.title] = false;
  }
});

const isActive = (item: any) => {
  if (!item.to) return false;
  return route.path === item.to || 
         (item.children && item.children.some((child: any) => route.path === child.to));
};

const toggleExpand = (item: any) => {
  if (item.children) {
    expanded[item.title] = !expanded[item.title];
  }
};
</script>

<style scoped>
.sidebar {
  height: 100%;
  background-color: var(--surface-card);
  border-right: 1px solid var(--surface-border);
  width: 250px;
  transition: width 0.3s;
}

.sidebar-content {
  padding: 1rem 0;
}

.menu-item a {
  color: var(--text-color);
  text-decoration: none;
  display: block;
  transition: background-color 0.2s;
  border-radius: 4px;
  margin: 0.25rem 0.5rem;
}

.menu-item a:hover {
  background-color: var(--surface-hover);
}

.menu-item .menu-header {
  cursor: pointer;
  color: var(--text-color);
  border-radius: 4px;
  margin: 0.25rem 0.5rem;
  transition: background-color 0.2s;
}

.menu-item .menu-header:hover {
  background-color: var(--surface-hover);
}

.submenu {
  overflow: hidden;
  transition: max-height 0.3s ease-in-out;
}

.active-route {
  background-color: var(--primary-color);
  color: white !important;
}

.active-route:hover {
  background-color: var(--primary-600) !important;
}
</style>