import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface User {
  id: string
  email: string
  name: string
  permissions: string[]
  roles: string[]
  [key: string]: any
}

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(false)
  const user = ref<User | null>(null)

  // Get user permissions
  const permissions = computed(() => user.value?.permissions || [])

  // Check if user has a specific permission
  const hasPermission = (permission: string): boolean => {
    if (!user.value) return false
    return user.value.permissions?.includes(permission) || false
  }

  // Check if user has any of the specified permissions
  const hasAnyPermission = (permissions: string[]): boolean => {
    if (!user.value || !user.value.permissions) return false
    return permissions.some(permission => user.value?.permissions?.includes(permission))
  }

  // Check if user has all of the specified permissions
  const hasAllPermissions = (permissions: string[]): boolean => {
    if (!user.value || !user.value.permissions) return false
    return permissions.every(permission => user.value?.permissions?.includes(permission))
  }

  // Check if user has a specific role
  const hasRole = (role: string): boolean => {
    if (!user.value) return false
    return user.value.roles?.includes(role) || false
  }

  // Check if user has any of the specified roles
  const hasAnyRole = (roles: string[]): boolean => {
    if (!user.value || !user.value.roles) return false
    return roles.some(role => user.value?.roles?.includes(role))
  }

  // Login user
  const login = (userData: any) => {
    user.value = {
      ...userData,
      permissions: userData.permissions || [],
      roles: userData.roles || []
    }
    isAuthenticated.value = true
  }

  // Logout user
  const logout = () => {
    user.value = null
    isAuthenticated.value = false
  }

  return {
    isAuthenticated,
    user,
    permissions,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    hasAnyRole,
    login,
    logout
  }
})