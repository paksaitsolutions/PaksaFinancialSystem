import { createApp } from 'vue'
import { createVuetify } from 'vuetify'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

// Vuetify
import 'vuetify/styles'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976d2',
          secondary: '#424242',
          accent: '#82b1ff',
          error: '#ff5252',
          info: '#2196f3',
          success: '#4caf50',
          warning: '#ffc107'
        }
      }
    }
  }
})

const pinia = createPinia()

// Router with auth guard
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/auth/login',
      name: 'Login',
      component: () => import('./views/auth/Login.vue')
    },
    {
      path: '/auth/register',
      name: 'Register',
      component: () => import('./views/auth/Register.vue')
    },
    {
      path: '/auth/forgot-password',
      name: 'ForgotPassword',
      component: () => import('./views/auth/ForgotPassword.vue')
    },
    {
      path: '/',
      name: 'Home',
      component: () => import('./views/Home.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('./views/Home.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Auth guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/auth/login')
  } else if (to.path === '/auth/login' && token) {
    next('/')
  } else {
    next()
  }
})

const app = createApp(App)

app.use(vuetify)
app.use(pinia)
app.use(router)

app.mount('#app')