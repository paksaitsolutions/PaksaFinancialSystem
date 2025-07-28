<template>
  <v-container fluid class="pa-6">
    <!-- Welcome Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="text-center">
          <h1 class="text-h4 font-weight-medium text-grey-darken-3 mb-2">
            Welcome to Financial Dashboard
          </h1>
          <p class="text-subtitle-1 text-grey-darken-1">
            Enterprise Management System
          </p>
        </div>
      </v-col>
    </v-row>

    <!-- Quick Actions - Single Row -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3" v-for="stat in quickStats" :key="stat.title">
        <v-card elevation="2" class="h-100">
          <v-card-text class="pa-4">
            <div class="d-flex align-center">
              <v-avatar :color="stat.color" size="40" class="mr-3">
                <v-icon color="white" size="20">{{ stat.icon }}</v-icon>
              </v-avatar>
              <div>
                <div class="text-h6 font-weight-bold">{{ stat.value }}</div>
                <div class="text-caption text-medium-emphasis">{{ stat.title }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Modules Section -->
    <v-row class="mb-4">
      <v-col cols="12">
        <div class="d-flex align-center">
          <v-icon color="primary" size="24" class="mr-2">mdi-view-dashboard</v-icon>
          <h2 class="text-h5 font-weight-medium text-grey-darken-3">Available Modules</h2>
          <v-spacer />
          <v-chip variant="outlined" size="small">
            {{ modules.length }} Modules
          </v-chip>
        </div>
      </v-col>
    </v-row>
    
    <!-- Module Cards Grid - 4 per row -->
    <v-row>
      <v-col 
        cols="12" 
        sm="6" 
        md="4" 
        lg="3" 
        v-for="module in modules" 
        :key="module.name"
      >
        <v-card 
          elevation="2"
          class="module-card h-100"
          @click="navigateToModule(module)"
        >
          <v-card-text class="pa-4 text-center">
            <v-avatar 
              :color="module.color" 
              size="48" 
              class="mb-3"
            >
              <v-icon color="white" size="24">{{ module.icon }}</v-icon>
            </v-avatar>
            
            <h3 class="module-title text-subtitle-1 font-weight-medium mb-2">
              {{ module.name }}
            </h3>
            
            <p class="module-description text-caption mb-3">
              {{ module.description }}
            </p>
            
            <v-chip 
              :color="module.status === 'active' ? 'success' : 'warning'" 
              size="small"
              variant="flat"
            >
              {{ module.status }}
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- System Info -->
    <v-row class="mt-6">
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-text class="pa-4">
            <div class="d-flex align-center mb-3">
              <v-avatar color="orange" size="36" class="mr-3">
                <v-icon color="white" size="18">mdi-api</v-icon>
              </v-avatar>
              <div>
                <h3 class="text-subtitle-1 font-weight-medium">API Documentation</h3>
                <p class="text-caption text-medium-emphasis mb-0">Interactive Swagger UI</p>
              </div>
            </div>
            
            <v-btn 
              color="orange" 
              variant="flat"
              size="small"
              href="http://localhost:8000/docs" 
              target="_blank"
              append-icon="mdi-open-in-new"
            >
              Open Docs
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-card elevation="2">
          <v-card-text class="pa-4">
            <div class="d-flex align-center mb-3">
              <v-avatar color="success" size="36" class="mr-3">
                <v-icon color="white" size="18">mdi-database</v-icon>
              </v-avatar>
              <div>
                <h3 class="text-subtitle-1 font-weight-medium">Database Status</h3>
                <p class="text-caption text-medium-emphasis mb-0">SQLite Connection</p>
              </div>
            </div>
            
            <v-chip color="success" variant="flat" size="small">
              <v-icon start size="14">mdi-database-check</v-icon>
              Connected
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const quickStats = ref([
  {
    title: 'Active Modules',
    value: '12',
    icon: 'mdi-apps',
    color: 'primary'
  },
  {
    title: 'Total Accounts',
    value: '156',
    icon: 'mdi-account-multiple',
    color: 'success'
  },
  {
    title: 'Monthly Revenue',
    value: '$125K',
    icon: 'mdi-trending-up',
    color: 'info'
  },
  {
    title: 'System Health',
    value: '99.9%',
    icon: 'mdi-heart-pulse',
    color: 'warning'
  }
])

const modules = ref([
  {
    name: 'General Ledger',
    description: 'Chart of accounts',
    icon: 'mdi-book-open-variant',
    color: 'deep-purple',
    status: 'active',
    route: '/gl'
  },
  {
    name: 'Accounts Payable',
    description: 'Vendor payments',
    icon: 'mdi-credit-card-outline',
    color: 'blue',
    status: 'active',
    route: '/ap'
  },
  {
    name: 'Accounts Receivable',
    description: 'Customer invoicing',
    icon: 'mdi-cash-multiple',
    color: 'green',
    status: 'active',
    route: '/ar'
  },
  {
    name: 'Cash Management',
    description: 'Bank reconciliation',
    icon: 'mdi-bank',
    color: 'cyan',
    status: 'active',
    route: '/cash'
  },
  {
    name: 'Fixed Assets',
    description: 'Asset tracking',
    icon: 'mdi-office-building',
    color: 'brown',
    status: 'active',
    route: '/assets'
  },
  {
    name: 'Payroll',
    description: 'Employee payroll',
    icon: 'mdi-account-cash',
    color: 'orange',
    status: 'active',
    route: '/payroll'
  },
  {
    name: 'Human Resources',
    description: 'Employee management',
    icon: 'mdi-account-group',
    color: 'indigo',
    status: 'active',
    route: '/hrm'
  },
  {
    name: 'Inventory',
    description: 'Stock management',
    icon: 'mdi-package-variant',
    color: 'teal',
    status: 'active',
    route: '/inventory'
  },
  {
    name: 'Budget Planning',
    description: 'Budget analysis',
    icon: 'mdi-chart-pie',
    color: 'pink',
    status: 'active',
    route: '/budget'
  },
  {
    name: 'Financial Reports',
    description: 'Reporting suite',
    icon: 'mdi-chart-bar',
    color: 'red',
    status: 'active',
    route: '/reports'
  },
  {
    name: 'System Admin',
    description: 'Administration',
    icon: 'mdi-shield-crown',
    color: 'deep-orange',
    status: 'active',
    route: '/admin'
  },
  {
    name: 'Settings',
    description: 'Configuration',
    icon: 'mdi-cog',
    color: 'grey',
    status: 'active',
    route: '/settings'
  }
])

const navigateToModule = (module: any) => {
  console.log('Navigating to:', module.route)
  router.push(module.route).catch(err => {
    console.error('Navigation error:', err)
  })
}
</script>

<style scoped>
.module-card {
  cursor: pointer;
  transition: all 0.2s ease;
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

.module-card:hover .module-title {
  color: rgb(var(--v-theme-primary)) !important;
}

.module-card:hover .module-description {
  color: rgb(var(--v-theme-primary)) !important;
}

.module-title {
  color: rgb(var(--v-theme-on-surface)) !important;
  transition: color 0.2s ease;
}

.module-description {
  color: rgba(var(--v-theme-on-surface), 0.6) !important;
  transition: color 0.2s ease;
}

.v-card {
  border-radius: 8px !important;
}
</style>