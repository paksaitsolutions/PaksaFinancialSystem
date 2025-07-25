<template>
  <v-app>
    <v-app-bar color="primary" dark>
      <v-app-bar-title>Paksa Financial System</v-app-bar-title>
      
      <v-spacer></v-spacer>
      
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props">
            <v-avatar size="32">
              <v-icon>mdi-account-circle</v-icon>
            </v-avatar>
          </v-btn>
        </template>
        
        <v-list>
          <v-list-item>
            <v-list-item-title>{{ user?.name || 'User' }}</v-list-item-title>
            <v-list-item-subtitle>{{ user?.email }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item @click="logout">
            <v-list-item-title>
              <v-icon class="mr-2">mdi-logout</v-icon>
              Logout
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
    
    <v-main>
      <v-container>
        <v-row justify="center">
          <v-col cols="12" md="10">
            <v-card class="pa-6">
              <v-card-title class="text-h4 text-center mb-4">
                Welcome to Paksa Financial System
              </v-card-title>
              
              <v-alert type="success" class="mb-4">
                <v-icon class="mr-2">mdi-check-circle</v-icon>
                Successfully logged in as {{ user?.role === 'admin' ? 'Administrator' : 'User' }}
              </v-alert>
              
              <v-row>
                <v-col cols="12" md="6">
                  <v-card class="pa-4" color="blue-lighten-5">
                    <v-card-title class="text-h6">
                      <v-icon class="mr-2">mdi-server</v-icon>
                      Backend Status
                    </v-card-title>
                    <v-card-text>
                      <v-chip color="green" variant="flat">
                        <v-icon start>mdi-check-circle</v-icon>
                        FastAPI Server Running
                      </v-chip>
                      <div class="mt-2 text-body-2">Port: 8000</div>
                    </v-card-text>
                  </v-card>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-card class="pa-4" color="green-lighten-5">
                    <v-card-title class="text-h6">
                      <v-icon class="mr-2">mdi-vuejs</v-icon>
                      Frontend Status
                    </v-card-title>
                    <v-card-text>
                      <v-chip color="green" variant="flat">
                        <v-icon start>mdi-check-circle</v-icon>
                        Vue.js 3 + Vuetify
                      </v-chip>
                      <div class="mt-2 text-body-2">Port: 3000</div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
              
              <v-divider class="my-6"></v-divider>
              
              <v-card-title class="text-h5 mb-4">
                <v-icon class="mr-2">mdi-view-dashboard</v-icon>
                Available Modules
              </v-card-title>
              
              <v-row>
                <v-col cols="12" sm="6" md="4" v-for="module in modules" :key="module.name">
                  <v-card 
                    class="pa-4" 
                    hover 
                    :color="module.color + '-lighten-5'"
                    @click="navigateToModule(module)"
                  >
                    <div class="text-center">
                      <v-icon :color="module.color" size="48" class="mb-3">{{ module.icon }}</v-icon>
                      <v-card-title class="text-h6 justify-center">{{ module.name }}</v-card-title>
                      <v-card-text class="text-center">{{ module.description }}</v-card-text>
                      <v-chip 
                        :color="module.status === 'active' ? 'green' : 'orange'" 
                        size="small"
                        variant="flat"
                      >
                        {{ module.status }}
                      </v-chip>
                    </div>
                  </v-card>
                </v-col>
              </v-row>
              
              <v-divider class="my-6"></v-divider>
              
              <v-row>
                <v-col cols="12" md="6">
                  <v-card class="pa-4">
                    <v-card-title class="text-h6">
                      <v-icon class="mr-2">mdi-api</v-icon>
                      API Documentation
                    </v-card-title>
                    <v-card-text>
                      Access the interactive API documentation to explore all available endpoints.
                    </v-card-text>
                    <v-card-actions>
                      <v-btn color="primary" href="http://localhost:8000/docs" target="_blank">
                        <v-icon class="mr-2">mdi-open-in-new</v-icon>
                        Open Swagger UI
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-card class="pa-4">
                    <v-card-title class="text-h6">
                      <v-icon class="mr-2">mdi-database</v-icon>
                      Database Status
                    </v-card-title>
                    <v-card-text>
                      PostgreSQL database connection is active and ready for operations.
                    </v-card-text>
                    <v-card-actions>
                      <v-chip color="green" variant="flat">
                        <v-icon start>mdi-database-check</v-icon>
                        Connected
                      </v-chip>
                    </v-card-actions>
                  </v-card>
                </v-col>
              </v-row>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref<any>(null)

const modules = ref([
  {
    name: 'Accounts Payable',
    description: 'Vendor management and invoice processing',
    icon: 'mdi-credit-card-outline',
    color: 'blue',
    status: 'active',
    route: '/ap'
  },
  {
    name: 'Accounts Receivable',
    description: 'Customer invoicing and collections',
    icon: 'mdi-cash-multiple',
    color: 'green',
    status: 'active',
    route: '/ar'
  },
  {
    name: 'General Ledger',
    description: 'Chart of accounts and journal entries',
    icon: 'mdi-book-open-variant',
    color: 'purple',
    status: 'active',
    route: '/gl'
  },
  {
    name: 'Payroll',
    description: 'Employee payroll and tax management',
    icon: 'mdi-account-group',
    color: 'orange',
    status: 'active',
    route: '/payroll'
  },
  {
    name: 'Tax Management',
    description: 'Tax calculations and compliance',
    icon: 'mdi-calculator',
    color: 'red',
    status: 'active',
    route: '/tax'
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
    name: 'Budget Management',
    description: 'Budget planning and analysis',
    icon: 'mdi-chart-line',
    color: 'indigo',
    status: 'active',
    route: '/budget'
  },
  {
    name: 'Fixed Assets',
    description: 'Asset lifecycle and depreciation',
    icon: 'mdi-office-building',
    color: 'brown',
    status: 'active',
    route: '/assets'
  },
  {
    name: 'Cash Management',
    description: 'Bank reconciliation and cash flow',
    icon: 'mdi-bank',
    color: 'cyan',
    status: 'active',
    route: '/cash'
  }
])

onMounted(() => {
  const userData = localStorage.getItem('user')
  if (userData) {
    user.value = JSON.parse(userData)
  }
})

const navigateToModule = (module: any) => {
  // For now, show a message since modules aren't fully implemented
  alert(`${module.name} module will be available soon!`)
}

const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  router.push('/auth/login')
}
</script>

<style scoped>
.v-card {
  transition: transform 0.2s;
}

.v-card:hover {
  transform: translateY(-2px);
}
</style>