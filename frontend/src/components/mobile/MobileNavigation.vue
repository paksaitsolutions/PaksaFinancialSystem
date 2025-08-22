<template>
  <div class="mobile-navigation">
    <!-- Mobile App Bar -->
    <v-app-bar
      v-if="isMobile"
      color="primary"
      dark
      app
      clipped-left
    >
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      
      <v-toolbar-title>{{ title }}</v-toolbar-title>
      
      <v-spacer />
      
      <v-btn icon @click="showSearch = !showSearch">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>
      
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props">
            <v-avatar size="32">
              <v-img :src="userAvatar" />
            </v-avatar>
          </v-btn>
        </template>
        
        <v-list>
          <v-list-item @click="$emit('profile')">
            <v-list-item-title>Profile</v-list-item-title>
          </v-list-item>
          <v-list-item @click="$emit('settings')">
            <v-list-item-title>Settings</v-list-item-title>
          </v-list-item>
          <v-list-item @click="$emit('logout')">
            <v-list-item-title>Logout</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
    
    <!-- Mobile Navigation Drawer -->
    <v-navigation-drawer
      v-if="isMobile"
      v-model="drawer"
      app
      temporary
      width="280"
    >
      <v-list>
        <v-list-item
          v-for="item in navigationItems"
          :key="item.title"
          :to="item.to"
          @click="drawer = false"
        >
          <template v-slot:prepend>
            <v-icon>{{ item.icon }}</v-icon>
          </template>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
    
    <!-- Mobile Search -->
    <v-expand-transition>
      <v-card
        v-if="showSearch && isMobile"
        class="mobile-search"
        flat
      >
        <v-card-text>
          <v-text-field
            v-model="searchQuery"
            placeholder="Search..."
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            density="compact"
            hide-details
            autofocus
            @keyup.enter="performSearch"
          />
        </v-card-text>
      </v-card>
    </v-expand-transition>
    
    <!-- Bottom Navigation for Mobile -->
    <v-bottom-navigation
      v-if="isMobile && showBottomNav"
      app
      grow
      color="primary"
    >
      <v-btn
        v-for="item in bottomNavItems"
        :key="item.value"
        :value="item.value"
        :to="item.to"
      >
        <v-icon>{{ item.icon }}</v-icon>
        <span>{{ item.text }}</span>
      </v-btn>
    </v-bottom-navigation>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMobile } from '@/composables/useMobile'

const props = defineProps({
  title: {
    type: String,
    default: 'Paksa Financial'
  },
  userAvatar: {
    type: String,
    default: '/default-avatar.png'
  },
  showBottomNav: {
    type: Boolean,
    default: true
  }
})

defineEmits(['profile', 'settings', 'logout', 'search'])

const { isMobile } = useMobile()

const drawer = ref(false)
const showSearch = ref(false)
const searchQuery = ref('')

const navigationItems = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/dashboard' },
  { title: 'Invoicing', icon: 'mdi-file-document', to: '/invoicing' },
  { title: 'Expenses', icon: 'mdi-credit-card', to: '/expenses' },
  { title: 'Reports', icon: 'mdi-chart-line', to: '/reports' },
  { title: 'Inventory', icon: 'mdi-package-variant', to: '/inventory' },
  { title: 'HR', icon: 'mdi-account-group', to: '/hrm' },
  { title: 'Settings', icon: 'mdi-cog', to: '/settings' }
]

const bottomNavItems = [
  { text: 'Home', icon: 'mdi-home', value: 'home', to: '/dashboard' },
  { text: 'Invoices', icon: 'mdi-file-document', value: 'invoices', to: '/invoicing' },
  { text: 'Expenses', icon: 'mdi-credit-card', value: 'expenses', to: '/expenses' },
  { text: 'Reports', icon: 'mdi-chart-line', value: 'reports', to: '/reports' }
]

const performSearch = () => {
  if (searchQuery.value.trim()) {
    // Emit search event or navigate to search results
    showSearch.value = false
  }
}
</script>

<style scoped>
.mobile-search {
  position: absolute;
  top: 64px;
  left: 0;
  right: 0;
  z-index: 1000;
  border-bottom: 1px solid #e0e0e0;
}

@media (max-width: 600px) {
  .v-app-bar .v-toolbar__content {
    padding: 0 8px;
  }
  
  .v-bottom-navigation {
    border-top: 1px solid #e0e0e0;
  }
}
</style>