import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/Home.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/auth',
      name: 'auth',
      component: {
        template: '<router-view />'
      },
      children: [
        {
          path: 'login',
          name: 'login',
          component: () => import('../views/auth/Login.vue')
        },
        {
          path: 'register',
          name: 'register',
          component: () => import('../views/auth/Register.vue')
        },
        {
          path: 'forgot-password',
          name: 'forgot-password',
          component: () => import('../views/auth/ForgotPassword.vue')
        }
      ]
    },
    // 404 page for routes that don't match
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFound.vue')
    }
  ]
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token') !== null || sessionStorage.getItem('token') !== null
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({ name: 'login' })
    } else {
      next()
    }
  } else if (to.path.startsWith('/auth') && isAuthenticated) {
    // Redirect to home if user is already authenticated and trying to access auth pages
    next({ path: '/' })
  } else {
    next()
  }
})

export default router