<template>
  <v-container fluid class="home-container">
    <!-- Hero Section -->
    <v-row class="hero-section mb-6">
      <v-col cols="12">
        <div class="d-flex align-center justify-center">
          <v-img 
            src="/src/assets/PFS Logo.png" 
            alt="Paksa Financial" 
            max-width="80"
            max-height="80"
            class="mr-4"
          />
          <div>
            <h1 class="hero-title mb-1">Paksa Financial</h1>
            <p class="hero-subtitle">Enterprise Management System</p>
          </div>
          <v-spacer />
          <v-chip color="success" size="small">
            <v-icon start size="16">mdi-check-circle</v-icon>
            Ready
          </v-chip>
        </div>
      </v-col>
    </v-row>

    <!-- Quick Actions -->
    <v-row class="mb-8">
      <v-col cols="12">
        <h2 class="section-title mb-4">
          <v-icon class="mr-2">mdi-lightning-bolt</v-icon>
          Quick Actions
        </h2>
        <v-row>
          <v-col v-for="action in quickActions" :key="action.title" cols="12" sm="6" md="3">
            <v-card 
              class="quick-action-card" 
              elevation="2"
              @click="router.push(action.route)"
            >
              <v-card-text class="text-center pa-6">
                <v-avatar :color="action.color" size="64" class="mb-3">
                  <v-icon color="white" size="32">{{ action.icon }}</v-icon>
                </v-avatar>
                <h3 class="text-h6 mb-2">{{ action.title }}</h3>
                <p class="text-body-2 text-medium-emphasis">{{ action.description }}</p>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
              
    <!-- Financial Modules -->
    <v-row class="mb-8">
      <v-col cols="12">
        <h2 class="section-title mb-4">
          <v-icon class="mr-2">mdi-view-dashboard</v-icon>
          Financial Modules
        </h2>
              
        <v-row>
          <v-col v-for="module in modules" :key="module.name" cols="12" sm="6" md="4" lg="3">
            <v-card 
              class="module-card" 
              elevation="3"
              @click="navigateToModule(module)"
            >
              <v-card-text class="text-center pa-6">
                <div class="module-icon-container mb-3">
                  <v-avatar :color="module.color" size="72">
                    <v-icon color="white" size="36">{{ module.icon }}</v-icon>
                  </v-avatar>
                </div>
                <h3 class="text-h6 mb-2">{{ module.name }}</h3>
                <p class="text-body-2 text-medium-emphasis mb-3">{{ module.description }}</p>
                <v-chip 
                  :color="module.status === 'active' ? 'success' : 'warning'" 
                  size="small"
                  variant="flat"
                >
                  <v-icon start size="16">{{ module.status === 'active' ? 'mdi-check' : 'mdi-clock' }}</v-icon>
                  {{ module.status }}
                </v-chip>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
              
    <!-- System Information -->
    <v-row>
      <v-col cols="12">
        <h2 class="section-title mb-4">
          <v-icon class="mr-2">mdi-information</v-icon>
          System Information
        </h2>
        <v-row>
          <v-col cols="12" md="4">
            <v-card class="info-card" elevation="2">
              <v-card-text class="text-center pa-6">
                <v-icon color="primary" size="48" class="mb-3">mdi-api</v-icon>
                <h3 class="text-h6 mb-2">API Documentation</h3>
                <p class="text-body-2 text-medium-emphasis mb-4">Interactive API documentation</p>
                <v-btn color="primary" variant="outlined" href="http://localhost:8000/docs" target="_blank">
                  <v-icon start>mdi-open-in-new</v-icon>
                  Open Swagger UI
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-card class="info-card" elevation="2">
              <v-card-text class="text-center pa-6">
                <v-icon color="success" size="48" class="mb-3">mdi-database</v-icon>
                <h3 class="text-h6 mb-2">Database Status</h3>
                <p class="text-body-2 text-medium-emphasis mb-4">PostgreSQL connection active</p>
                <v-chip color="success" variant="flat">
                  <v-icon start>mdi-database-check</v-icon>
                  Connected
                </v-chip>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-card class="info-card" elevation="2">
              <v-card-text class="text-center pa-6">
                <v-icon color="info" size="48" class="mb-3">mdi-shield-check</v-icon>
                <h3 class="text-h6 mb-2">Security Status</h3>
                <p class="text-body-2 text-medium-emphasis mb-4">Multi-tenant isolation active</p>
                <v-chip color="info" variant="flat">
                  <v-icon start>mdi-shield-check</v-icon>
                  Secured
                </v-chip>
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
const user = ref<any>(null)

const quickActions = ref([
  {
    title: 'AI Dashboard',
    description: 'Advanced analytics',
    icon: 'mdi-brain',
    color: 'primary',
    route: '/dashboard'
  },
  {
    title: 'Create Invoice',
    description: 'New customer invoice',
    icon: 'mdi-file-document-plus',
    color: 'success',
    route: '/ar'
  },
  {
    title: 'View Reports',
    description: 'Financial reports',
    icon: 'mdi-chart-line',
    color: 'info',
    route: '/reports'
  },
  {
    title: 'Manage Users',
    description: 'User administration',
    icon: 'mdi-account-group',
    color: 'warning',
    route: '/rbac'
  }
])

const modules = ref([
  {
    name: 'General Ledger',
    description: 'Chart of accounts and journal entries',
    icon: 'mdi-book-open-variant',
    color: 'primary',
    status: 'active',
    route: '/gl'
  },
  {
    name: 'Accounts Payable',
    description: 'Vendor management and payments',
    icon: 'mdi-credit-card',
    color: 'error',
    status: 'active',
    route: '/ap'
  },
  {
    name: 'Accounts Receivable',
    description: 'Customer invoicing and collections',
    icon: 'mdi-wallet',
    color: 'success',
    status: 'active',
    route: '/ar'
  },
  {
    name: 'Cash Management',
    description: 'Bank accounts and reconciliation',
    icon: 'mdi-bank',
    color: 'info',
    status: 'active',
    route: '/cash'
  },
  {
    name: 'Fixed Assets',
    description: 'Asset management and depreciation',
    icon: 'mdi-office-building',
    color: 'secondary',
    status: 'active',
    route: '/assets'
  },
  {
    name: 'Payroll',
    description: 'Employee payroll processing',
    icon: 'mdi-account-cash',
    color: 'warning',
    status: 'active',
    route: '/payroll'
  },
  {
    name: 'Human Resources',
    description: 'Employee management system',
    icon: 'mdi-account-group',
    color: 'purple',
    status: 'active',
    route: '/hrm'
  },
  {
    name: 'Inventory',
    description: 'Stock management and tracking',
    icon: 'mdi-package-variant',
    color: 'teal',
    status: 'active',
    route: '/inventory'
  },
  {
    name: 'Budget Planning',
    description: 'Budget creation and monitoring',
    icon: 'mdi-chart-pie',
    color: 'orange',
    status: 'active',
    route: '/budget'
  },
  {
    name: 'Financial Reports',
    description: 'Comprehensive reporting suite',
    icon: 'mdi-chart-bar',
    color: 'indigo',
    status: 'active',
    route: '/reports'
  },
  {
    name: 'System Admin',
    description: 'System administration panel',
    icon: 'mdi-shield-crown',
    color: 'deep-purple',
    status: 'active',
    route: '/admin'
  },
  {
    name: 'Settings',
    description: 'Company configuration',
    icon: 'mdi-cog',
    color: 'grey',
    status: 'active',
    route: '/settings'
  }
])

onMounted(() => {
  const userData = localStorage.getItem('user')
  if (userData) {
    user.value = JSON.parse(userData)
  }
})

const navigateToModule = (module: any) => {
  router.push(module.route)
}

const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  router.push('/auth/login')
}
</script>

<style scoped>
.home-container {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  padding: 24px;
}

.hero-section {
  padding: 20px 0;
}

.hero-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
}

.hero-subtitle {
  font-size: 1rem;
  color: #7f8c8d;
  font-weight: 400;
}

.section-title {
  font-size: 1.75rem;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
}

.quick-action-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 16px;
  height: 100%;
}

.quick-action-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}

.module-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 16px;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
}

.module-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 16px 48px rgba(0,0,0,0.2);
}

.module-icon-container {
  position: relative;
}

.info-card {
  height: 100%;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.info-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
}

@media (max-width: 960px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
}
</style>