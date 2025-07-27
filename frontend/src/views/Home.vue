<template>
  <v-container fluid class="home-container">
    <!-- Compact Header -->
    <v-row class="header-section mb-4">
      <v-col cols="12">
        <v-card class="header-card" elevation="0">
          <v-card-text class="pa-4">
            <div class="d-flex align-center">
              <v-avatar size="48" class="header-logo">
                <v-icon size="24" color="white">mdi-finance</v-icon>
              </v-avatar>
              <div class="ml-4">
                <h1 class="header-title">Financial Dashboard</h1>
                <p class="header-subtitle">Enterprise Management System</p>
              </div>
              <v-spacer />
              <v-chip color="success" variant="flat" size="small">
                <v-icon start size="14">mdi-check-circle</v-icon>
                Online
              </v-chip>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Stats -->
    <v-row class="mb-4">
      <v-col cols="12" sm="6" md="3" v-for="stat in quickStats" :key="stat.title">
        <v-card class="stat-card" elevation="1">
          <v-card-text class="pa-4">
            <div class="d-flex align-center">
              <v-avatar :color="stat.color" size="40" class="stat-icon">
                <v-icon color="white" size="20">{{ stat.icon }}</v-icon>
              </v-avatar>
              <div class="ml-3">
                <div class="text-h6 font-weight-bold">{{ stat.value }}</div>
                <div class="text-caption text-medium-emphasis">{{ stat.title }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Modules Grid -->
    <v-row class="mb-4">
      <v-col cols="12">
        <div class="d-flex align-center mb-3">
          <h2 class="section-title">Modules</h2>
          <v-spacer />
          <v-chip size="small" variant="outlined">{{ modules.length }} Available</v-chip>
        </div>
        
        <v-row>
          <v-col 
            v-for="module in modules" 
            :key="module.name" 
            cols="12" 
            sm="6" 
            md="4" 
            lg="3"
          >
            <v-card 
              class="module-card" 
              elevation="1"
              @click="navigateToModule(module)"
              :ripple="true"
            >
              <v-card-text class="pa-4">
                <div class="d-flex align-center mb-3">
                  <v-avatar :color="module.color" size="36" class="module-icon">
                    <v-icon color="white" size="18">{{ module.icon }}</v-icon>
                  </v-avatar>
                  <div class="ml-3 flex-grow-1">
                    <h3 class="module-title">{{ module.name }}</h3>
                    <v-chip 
                      :color="module.status === 'active' ? 'success' : 'warning'" 
                      size="x-small"
                      variant="flat"
                    >
                      {{ module.status }}
                    </v-chip>
                  </div>
                </div>
                <p class="module-description">{{ module.description }}</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>

    <!-- System Status -->
    <v-row>
      <v-col cols="12">
        <div class="d-flex align-center mb-3">
          <h2 class="section-title">System Status</h2>
        </div>
        
        <v-row>
          <v-col cols="12" md="4" v-for="status in systemStatus" :key="status.title">
            <v-card class="status-card" elevation="1">
              <v-card-text class="pa-4">
                <div class="d-flex align-center mb-2">
                  <v-icon :color="status.color" size="20" class="mr-2">{{ status.icon }}</v-icon>
                  <h3 class="status-title">{{ status.title }}</h3>
                </div>
                <p class="status-description mb-3">{{ status.description }}</p>
                
                <div class="d-flex align-center justify-space-between">
                  <v-chip :color="status.color" variant="flat" size="small">
                    <v-icon start size="12">{{ status.statusIcon }}</v-icon>
                    {{ status.status }}
                  </v-chip>
                  
                  <v-btn 
                    v-if="status.action"
                    :color="status.color" 
                    variant="text" 
                    size="small"
                    :href="status.actionUrl"
                    target="_blank"
                  >
                    {{ status.action }}
                    <v-icon end size="14">mdi-open-in-new</v-icon>
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
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
    description: 'Chart of accounts and journal entries',
    icon: 'mdi-book-open-variant',
    color: 'blue-darken-2',
    status: 'active',
    route: '/gl'
  },
  {
    name: 'Accounts Payable',
    description: 'Vendor management and payments',
    icon: 'mdi-credit-card-outline',
    color: 'red-darken-2',
    status: 'active',
    route: '/ap'
  },
  {
    name: 'Accounts Receivable',
    description: 'Customer invoicing and collections',
    icon: 'mdi-wallet-outline',
    color: 'green-darken-2',
    status: 'active',
    route: '/ar'
  },
  {
    name: 'Cash Management',
    description: 'Bank accounts and reconciliation',
    icon: 'mdi-bank',
    color: 'cyan-darken-2',
    status: 'active',
    route: '/cash'
  },
  {
    name: 'Fixed Assets',
    description: 'Asset tracking and depreciation',
    icon: 'mdi-office-building',
    color: 'purple-darken-2',
    status: 'active',
    route: '/assets'
  },
  {
    name: 'Payroll',
    description: 'Employee payroll processing',
    icon: 'mdi-account-cash',
    color: 'orange-darken-2',
    status: 'active',
    route: '/payroll'
  },
  {
    name: 'Human Resources',
    description: 'Employee management system',
    icon: 'mdi-account-group',
    color: 'indigo-darken-2',
    status: 'active',
    route: '/hrm'
  },
  {
    name: 'Inventory',
    description: 'Stock management and tracking',
    icon: 'mdi-package-variant',
    color: 'teal-darken-2',
    status: 'active',
    route: '/inventory'
  },
  {
    name: 'Budget Planning',
    description: 'Budget creation and monitoring',
    icon: 'mdi-chart-pie',
    color: 'deep-orange-darken-2',
    status: 'active',
    route: '/budget'
  },
  {
    name: 'Financial Reports',
    description: 'Comprehensive reporting suite',
    icon: 'mdi-chart-line',
    color: 'pink-darken-2',
    status: 'active',
    route: '/reports'
  },
  {
    name: 'System Admin',
    description: 'System administration panel',
    icon: 'mdi-shield-crown',
    color: 'brown-darken-2',
    status: 'active',
    route: '/admin'
  },
  {
    name: 'Settings',
    description: 'Company configuration',
    icon: 'mdi-cog',
    color: 'grey-darken-2',
    status: 'active',
    route: '/settings'
  }
])

const systemStatus = ref([
  {
    title: 'API Documentation',
    description: 'Interactive API documentation',
    icon: 'mdi-api',
    color: 'primary',
    status: 'Available',
    statusIcon: 'mdi-check-circle',
    action: 'Open Docs',
    actionUrl: 'http://localhost:8000/docs'
  },
  {
    title: 'Database Status',
    description: 'Real-time database connection',
    icon: 'mdi-database',
    color: 'success',
    status: 'Connected',
    statusIcon: 'mdi-database-check'
  },
  {
    title: 'Security Status',
    description: 'Multi-tenant security monitoring',
    icon: 'mdi-shield-check',
    color: 'info',
    status: 'Secured',
    statusIcon: 'mdi-shield-check'
  }
])

const navigateToModule = (module: any) => {
  console.log('Navigating to:', module.route)
  router.push(module.route).catch(err => {
    console.error('Navigation error:', err)
    // Fallback to dashboard if route doesn't exist
    router.push('/dashboard')
  })
}
</script>

<style scoped>
.home-container {
  background: #fafafa;
  min-height: 100vh;
  padding: 16px;
}

/* Compact Header */
.header-section {
  margin-bottom: 1rem;
}

.header-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
}

.header-logo {
  background: linear-gradient(135deg, #1976d2, #1565c0);
}

.header-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #212121;
  margin: 0;
}

.header-subtitle {
  font-size: 0.875rem;
  color: #757575;
  margin: 0;
}

/* Section Titles */
.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #424242;
}

/* Stats Cards */
.stat-card {
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  background: white;
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: #bdbdbd;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.stat-icon {
  flex-shrink: 0;
}

/* Module Cards */
.module-card {
  cursor: pointer;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  background: white;
  transition: all 0.2s ease;
  height: 100%;
}

.module-card:hover {
  border-color: #1976d2;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.15);
  transform: translateY(-2px);
}

.module-icon {
  flex-shrink: 0;
}

.module-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #212121;
  margin: 0;
  line-height: 1.2;
}

.module-description {
  font-size: 0.8rem;
  color: #757575;
  margin: 0;
  line-height: 1.3;
}

/* Status Cards */
.status-card {
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  background: white;
  transition: all 0.2s ease;
  height: 100%;
}

.status-card:hover {
  border-color: #bdbdbd;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.status-title {
  font-size: 1rem;
  font-weight: 600;
  color: #212121;
  margin: 0;
}

.status-description {
  font-size: 0.875rem;
  color: #757575;
  margin: 0;
  line-height: 1.4;
}

/* Responsive Design */
@media (max-width: 960px) {
  .home-container {
    padding: 12px;
  }
  
  .header-title {
    font-size: 1.25rem;
  }
  
  .section-title {
    font-size: 1.125rem;
  }
}

@media (max-width: 600px) {
  .home-container {
    padding: 8px;
  }
  
  .header-card .pa-4 {
    padding: 12px !important;
  }
  
  .stat-card .pa-4,
  .module-card .pa-4,
  .status-card .pa-4 {
    padding: 12px !important;
  }
}
</style>