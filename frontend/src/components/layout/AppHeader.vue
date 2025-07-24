<template>
  <v-app-bar color="primary" app>
    <v-app-bar-nav-icon @click="toggleDrawer"></v-app-bar-nav-icon>
    
    <v-app-bar-title>
      <router-link to="/" class="text-decoration-none text-white">
        Paksa Financial System
      </router-link>
    </v-app-bar-title>
    
    <v-spacer></v-spacer>
    
    <v-btn icon>
      <v-icon>mdi-magnify</v-icon>
    </v-btn>
    
    <ThemeToggle />
    
    <KeyboardShortcutsDialog />
    
    <v-btn icon>
      <v-badge dot color="error">
        <v-icon>mdi-bell</v-icon>
      </v-badge>
    </v-btn>
    
    <v-menu>
      <template v-slot:activator="{ props }">
        <v-btn v-bind="props" class="ml-2">
          <v-avatar size="32" class="mr-2">
            <v-img src="https://randomuser.me/api/portraits/men/85.jpg" alt="User"></v-img>
          </v-avatar>
          {{ userName || 'User' }}
          <v-icon class="ml-2">mdi-chevron-down</v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item to="/profile">
          <template v-slot:prepend>
            <v-icon>mdi-account</v-icon>
          </template>
          <v-list-item-title>Profile</v-list-item-title>
        </v-list-item>
        <v-list-item to="/settings">
          <template v-slot:prepend>
            <v-icon>mdi-cog</v-icon>
          </template>
          <v-list-item-title>Settings</v-list-item-title>
        </v-list-item>
        <v-divider></v-divider>
        <v-list-item @click="logout">
          <template v-slot:prepend>
            <v-icon>mdi-logout</v-icon>
          </template>
          <v-list-item-title>Logout</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import ThemeToggle from '@/components/common/ThemeToggle.vue';
import KeyboardShortcutsDialog from '@/components/common/KeyboardShortcutsDialog.vue';

const props = defineProps({
  drawer: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['update:drawer']);

const router = useRouter();
const authStore = useAuthStore();

const userName = computed(() => authStore.userName);

const toggleDrawer = () => {
  emit('update:drawer', !props.drawer);
};

const logout = async () => {
  await authStore.logout();
  router.push('/auth/login');
};
</script>