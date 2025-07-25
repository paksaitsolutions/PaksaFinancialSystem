<template>
  <AppLayout title="Company Settings">
    <v-container>
      <v-card>
        <v-card-title>Company Settings</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="4" v-for="setting in settingModules" :key="setting.name">
              <v-card hover @click="navigateTo(setting.route)">
                <v-card-text class="text-center">
                  <v-icon size="48" :color="setting.color">{{ setting.icon }}</v-icon>
                  <div class="text-h6 mt-2">{{ setting.name }}</div>
                  <div class="text-caption">{{ setting.description }}</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-container>
  </AppLayout>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'

const router = useRouter()

const settingModules = [
  { name: 'Company Profile', route: '/settings/profile', icon: 'mdi-domain', color: 'blue', description: 'Basic company information' },
  { name: 'Currency Management', route: '/settings/currency', icon: 'mdi-currency-usd', color: 'green', description: 'Multi-currency settings' },
  { name: 'User Management', route: '/settings/users', icon: 'mdi-account-group', color: 'orange', description: 'Manage company users' },
  { name: 'Integrations', route: '/settings/integrations', icon: 'mdi-api', color: 'purple', description: 'Third-party integrations' },
  { name: 'Security', route: '/settings/security', icon: 'mdi-shield-check', color: 'red', description: 'Security settings' },
  { name: 'Notifications', route: '/settings/notifications', icon: 'mdi-bell', color: 'teal', description: 'Notification preferences' }
]

const navigateTo = (route: string) => {
  router.push(route)
}
</script>