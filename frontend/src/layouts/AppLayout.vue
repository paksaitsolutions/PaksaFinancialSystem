<template>
  <v-app>
    <v-navigation-drawer v-model="drawer" app>
      <v-list>
        <v-list-item class="pa-4">
          <div class="d-flex align-center">
            <v-img src="/logo.png" height="32" width="32" class="mr-3"></v-img>
            <div>
              <div class="text-subtitle-1 font-weight-medium">{{ user?.name || 'User' }}</div>
              <div class="text-caption text-medium-emphasis">{{ user?.email }}</div>
            </div>
          </div>
        </v-list-item>
      </v-list>
      
      <v-divider></v-divider>
      
      <v-list density="compact" nav>
        <v-list-item prepend-icon="mdi-view-dashboard" title="Dashboard" @click="navigateTo('/')"></v-list-item>
        
        <v-list-group value="accounting">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-calculator" title="Accounting"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-book-open-variant" title="General Ledger" @click="navigateTo('/gl')"></v-list-item>
          <v-list-item prepend-icon="mdi-credit-card-outline" title="Accounts Payable" @click="navigateTo('/ap')"></v-list-item>
          <v-list-item prepend-icon="mdi-cash-multiple" title="Accounts Receivable" @click="navigateTo('/ar')"></v-list-item>
        </v-list-group>
        
        <v-list-item prepend-icon="mdi-chart-bar" title="Reports" @click="navigateTo('/reports')"></v-list-item>
        
        <v-list-group value="admin">
          <template v-slot:activator="{ props }">
            <v-list-item v-bind="props" prepend-icon="mdi-cog" title="Administration"></v-list-item>
          </template>
          <v-list-item prepend-icon="mdi-shield-crown" title="Super Admin" @click="navigateTo('/admin')"></v-list-item>
          <v-list-item prepend-icon="mdi-cog" title="Settings" @click="navigateTo('/settings')"></v-list-item>
          <v-list-item prepend-icon="mdi-account-key" title="Role Management" @click="navigateTo('/rbac')"></v-list-item>
        </v-list-group>
      </v-list>
    </v-navigation-drawer>
    
    <v-app-bar color="primary" dark>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-app-bar-title>{{ title }}</v-app-bar-title>
      
      <v-spacer></v-spacer>
      
      <v-btn icon @click="logout">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>
    
    <v-main>
      <v-container fluid>
        <slot />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

interface Props {
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Paksa Financial System'
})

const router = useRouter()
const user = ref<any>(null)
const drawer = ref(true)

onMounted(() => {
  const userData = localStorage.getItem('user')
  if (userData) {
    user.value = JSON.parse(userData)
  }
})

const navigateTo = (path: string) => {
  router.push(path)
}

const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  router.push('/auth/login')
}
</script>