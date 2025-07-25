<template>
  <v-app>
    <ModernNavigation />
    
    <v-app-bar color="primary" dark>
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
import { useRouter } from 'vue-router'
import ModernNavigation from '@/components/navigation/ModernNavigation.vue'

interface Props {
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Paksa Financial System'
})

const router = useRouter()

const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  router.push('/auth/login')
}
</script>