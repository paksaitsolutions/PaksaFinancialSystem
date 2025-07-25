<template>
  <v-app>
    <v-app-bar color="primary" dark>
      <v-btn icon @click="goHome">
        <v-icon>mdi-home</v-icon>
      </v-btn>
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

onMounted(() => {
  const userData = localStorage.getItem('user')
  if (userData) {
    user.value = JSON.parse(userData)
  }
})

const goHome = () => {
  router.push('/')
}

const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  router.push('/auth/login')
}
</script>