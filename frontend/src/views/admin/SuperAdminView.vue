<template>
  <AppLayout title="Super Admin">
    <v-container>
      <v-card>
        <v-card-title>Super Admin Dashboard</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="3" v-for="stat in stats" :key="stat.title">
              <v-card>
                <v-card-text>
                  <div class="d-flex align-center">
                    <v-icon :color="stat.color" size="40" class="mr-3">{{ stat.icon }}</v-icon>
                    <div>
                      <div class="text-h5">{{ stat.value }}</div>
                      <div class="text-subtitle-1">{{ stat.title }}</div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          
          <v-row class="mt-4">
            <v-col cols="12" md="4" v-for="module in adminModules" :key="module.name">
              <v-card hover>
                <v-card-text class="text-center">
                  <v-icon size="48" :color="module.color">{{ module.icon }}</v-icon>
                  <div class="text-h6 mt-2">{{ module.name }}</div>
                  <div class="text-caption">{{ module.description }}</div>
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
import AppLayout from '@/layouts/AppLayout.vue'

const stats = [
  { title: 'Total Companies', value: '25', icon: 'mdi-domain', color: 'blue' },
  { title: 'Active Users', value: '156', icon: 'mdi-account-group', color: 'green' },
  { title: 'System Health', value: '98%', icon: 'mdi-heart-pulse', color: 'red' },
  { title: 'Storage Used', value: '2.4GB', icon: 'mdi-database', color: 'orange' }
]

const adminModules = [
  { name: 'Company Management', icon: 'mdi-domain', color: 'blue', description: 'Manage tenant companies' },
  { name: 'User Management', icon: 'mdi-account-cog', color: 'green', description: 'System user administration' },
  { name: 'System Settings', icon: 'mdi-cog', color: 'orange', description: 'Global system configuration' },
  { name: 'Audit Logs', icon: 'mdi-file-document-outline', color: 'purple', description: 'System audit trails' },
  { name: 'Monitoring', icon: 'mdi-monitor-dashboard', color: 'teal', description: 'System monitoring' },
  { name: 'Backup & Recovery', icon: 'mdi-backup-restore', color: 'brown', description: 'Data backup management' }
]
</script>