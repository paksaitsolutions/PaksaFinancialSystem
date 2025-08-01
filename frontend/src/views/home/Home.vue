<template>
  <div class="surface-ground min-h-screen p-4">
    <!-- Hero Section with Gradient Background -->
    <div 
      class="hero-section mb-6 p-6 md:p-8 text-center border-round-3xl"
      :style="{
        background: 'linear-gradient(135deg, var(--primary-color) 0%, var(--primary-600) 100%)',
        position: 'relative',
        overflow: 'hidden',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.12)'
      }"
    >
      <div class="container mx-auto px-4">
        <Avatar 
          icon="pi pi-wallet" 
          size="xlarge" 
          class="mb-4" 
          :style="{
            background: 'rgba(255, 255, 255, 0.2)', 
            backdropFilter: 'blur(5px)',
            width: '5rem',
            height: '5rem'
          }"
          shape="circle"
        />
        <h1 class="text-4xl md:text-5xl text-white font-bold mb-3">
          Welcome to Financial Dashboard
        </h1>
        <p class="text-xl text-white opacity-90 mb-0">
          Enterprise Management System
        </p>
        <Chip
          class="mt-4 border-none"
          :pt="{
            root: 'bg-white text-primary border-none',
            icon: 'mr-2',
            label: 'font-medium'
          }"
        >
          <template #icon>
            <i class="pi pi-sync mr-2"></i>
          </template>
          Last updated: Just now
        </Chip>
      </div>
      
      <!-- Decorative Elements -->
      <div class="decorative-circles">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
        <div class="circle circle-3"></div>
      </div>
    </div>

    <!-- Quick Stats with Modern Cards -->
    <div class="grid mb-6">
      <div 
        v-for="(stat, index) in quickStats" 
        :key="index" 
        class="col-12 sm:col-6 lg:col-3 mb-4"
      >
        <Card class="h-full border-round-2xl shadow-2 hover:shadow-4 transition-all transition-duration-200">
          <template #content>
            <div class="flex align-items-center">
              <Avatar 
                :icon="stat.icon" 
                size="xlarge"
                :style="{
                  backgroundColor: stat.color + '20', 
                  color: stat.color,
                  borderRadius: '12px',
                  width: '3.5rem',
                  height: '3.5rem'
                }"
                class="mr-3 flex-shrink-0"
              />
              <div class="overflow-hidden">
                <h3 class="text-900 font-medium mb-1 text-sm sm:text-base">{{ stat.title }}</h3>
                <p class="text-700 font-bold text-xl sm:text-2xl mb-0 truncate">{{ stat.value }}</p>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Modules Section with Modern Grid -->
    <Card class="mb-6 border-round-2xl shadow-2">
      <template #title>
        <div class="flex align-items-center">
          <i class="pi pi-th-large text-primary mr-2"></i>
          <span class="text-xl font-semibold">Application Modules</span>
        </div>
      </template>
      <template #content>
        <div class="grid">
          <div 
            v-for="(module, index) in modules" 
            :key="index"
            class="col-12 sm:col-6 md:col-4 lg:col-3"
          >
            <div 
              class="module-card p-4 border-round-2xl mb-4 cursor-pointer transition-all transition-duration-200 hover:shadow-4 border-1 border-transparent hover:border-primary-100"
              :class="{ 'bg-primary-50 border-primary-200': module.status === 'active' }"
              @click="navigateToModule(module)"
            >
              <div class="flex align-items-start">
                <Avatar 
                  :icon="module.icon" 
                  :style="{
                    backgroundColor: module.color + '20', 
                    color: module.color,
                    borderRadius: '12px',
                    width: '3rem',
                    height: '3rem'
                  }"
                  size="large"
                  class="mr-3 flex-shrink-0"
                  shape="square"
                />
                <div class="flex-grow-1 min-w-0">
                  <h3 class="text-base font-semibold mb-1 text-900 truncate">{{ module.name }}</h3>
                  <p class="text-sm text-600 mb-2 line-clamp-2" style="min-height: 2.5rem;">{{ module.description }}</p>
                  <Tag 
                    :value="module.status === 'active' ? 'Active' : 'In Development'" 
                    :severity="module.status === 'active' ? 'success' : 'warning'" 
                    :icon="module.status === 'active' ? 'pi pi-check-circle' : 'pi pi-exclamation-triangle'"
                    class="font-medium text-xs"
                    :pt="{
                      root: 'px-2 py-1'
                    }"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- System Information Cards -->
    <div class="grid mb-6">
      <div class="col-12 md:col-6 mb-4">
        <Card class="h-full border-round-2xl shadow-2 hover:shadow-4 transition-all transition-duration-200">
          <template #content>
            <div class="flex align-items-center">
              <Avatar 
                icon="pi pi-book" 
                size="xlarge" 
                class="bg-orange-100 text-orange-600 mr-3 flex-shrink-0" 
                :style="{
                  borderRadius: '12px',
                  width: '3.5rem',
                  height: '3.5rem'
                }" 
              />
              <div class="flex-grow-1 min-w-0">
                <h3 class="text-lg font-bold mb-1 text-900">API Documentation</h3>
                <p class="text-sm text-600 mb-0 truncate">Interactive Swagger UI</p>
              </div>
              <div class="ml-3 flex-shrink-0">
                <Button 
                  label="Open Docs" 
                  icon="pi pi-external-link" 
                  class="p-button-sm p-button-text p-button-rounded"
                  @click="openExternal('http://localhost:8000/docs')"
                />
              </div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6 mb-4">
        <Card class="h-full border-round-2xl shadow-2 hover:shadow-4 transition-all transition-duration-200">
          <template #content>
            <div class="flex align-items-center">
              <Avatar 
                icon="pi pi-github" 
                size="xlarge" 
                class="bg-blue-100 text-blue-600 mr-3 flex-shrink-0"
                :style="{
                  borderRadius: '12px',
                  width: '3.5rem',
                  height: '3.5rem'
                }"
              />
              <div class="flex-grow-1 min-w-0">
                <h3 class="text-lg font-bold mb-1 text-900">GitHub Repository</h3>
                <p class="text-sm text-600 mb-0 truncate">View source code and contribute</p>
              </div>
              <div class="ml-3 flex-shrink-0">
                <Button 
                  label="View on GitHub" 
                  icon="pi pi-github" 
                  class="p-button-sm p-button-text p-button-rounded"
                  @click="openExternal('https://github.com/your-org/paksa-financial')"
                />
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Tag from 'primevue/tag'

// Types
type ModuleStatus = 'active' | 'development' | 'coming-soon'

interface QuickStat {
  title: string
  value: string
  icon: string
  color: string
}

interface Module {
  id: string
  name: string
  description: string
  icon: string
  color: string
  status: ModuleStatus
  route: string
}

const router = useRouter()

const quickStats = ref<QuickStat[]>([
  {
    title: 'Active Modules',
    value: '12',
    icon: 'pi pi-th-large',
    color: 'var(--primary-color)'
  },
  {
    title: 'Total Accounts',
    value: '156',
    icon: 'pi pi-users',
    color: 'var(--green-500)'
  },
  {
    title: 'Monthly Revenue',
    value: '$125K',
    icon: 'pi pi-chart-line',
    color: 'var(--blue-500)'
  },
  {
    title: 'System Health',
    value: '99.9%',
    icon: 'pi pi-heart',
    color: 'var(--yellow-500)'
  }
])

const modules = ref<Module[]>([
  {
    id: 'dashboard',
    name: 'Dashboard',
    description: 'Overview of your financial data and key metrics',
    icon: 'pi pi-chart-pie',
    color: '#6366F1',
    status: 'active',
    route: '/dashboard'
  },
  {
    id: 'general-ledger',
    name: 'General Ledger',
    description: 'Manage chart of accounts, journal entries, and financial statements',
    icon: 'pi pi-book',
    color: '#10B981',
    status: 'active',
    route: '/general-ledger'
  },
  {
    id: 'accounts-payable',
    name: 'Accounts Payable',
    description: 'Track and manage vendor invoices and payments',
    icon: 'pi pi-credit-card',
    color: '#F59E0B',
    status: 'active',
    route: '/accounts-payable'
  },
  {
    id: 'accounts-receivable',
    name: 'Accounts Receivable',
    description: 'Manage customer invoices, payments, and collections',
    icon: 'pi pi-money-bill',
    color: '#3B82F6',
    status: 'active',
    route: '/accounts-receivable'
  },
  {
    id: 'cash-management',
    name: 'Cash Management',
    description: 'Track bank accounts, transactions, and cash positions',
    icon: 'pi pi-wallet',
    color: '#8B5CF6',
    status: 'active',
    route: '/cash-management'
  },
  {
    id: 'fixed-assets',
    name: 'Fixed Assets',
    description: 'Track and manage company assets and depreciation',
    icon: 'pi pi-building',
    color: '#EC4899',
    status: 'active',
    route: '/fixed-assets'
  },
  {
    id: 'payroll',
    name: 'Payroll',
    description: 'Process employee payments, taxes, and benefits',
    icon: 'pi pi-users',
    color: '#F97316',
    status: 'active',
    route: '/payroll'
  },
  {
    id: 'reports',
    name: 'Reports',
    description: 'Generate comprehensive financial reports and analytics',
    icon: 'pi pi-chart-bar',
    color: '#14B8A6',
    status: 'active',
    route: '/reports'
  }
])

const navigateToModule = (module: Module) => {
  router.push(module.route)
}

const openExternal = (url: string) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}
</script>

<style scoped>
/* Modern Card Styles */
.module-card {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid var(--surface-border);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08) !important;
}

/* Decorative Elements for Hero Section */
.decorative-circles .circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
  pointer-events: none;
  z-index: 0;
  opacity: 0.6;
}

.circle-1 {
  width: 18rem;
  height: 18rem;
  top: -5rem;
  right: -5rem;
  background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 70%);
}

.circle-2 {
  width: 12rem;
  height: 12rem;
  bottom: -3rem;
  left: -3rem;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
}

.circle-3 {
  width: 8rem;
  height: 8rem;
  bottom: 20%;
  right: 10%;
  background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0) 70%);
}

/* Responsive Adjustments */
@media (max-width: 1024px) {
  .hero-section {
    padding: 3rem 1.5rem !important;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  .decorative-circles .circle {
    opacity: 0.4;
  }
}

@media (max-width: 640px) {
  .hero-section {
    padding: 2rem 1rem !important;
  }
  
  h1 {
    font-size: 1.75rem;
  }
  
  .decorative-circles {
    display: none;
  }
  
  .p-card {
    border-radius: 1rem !important;
    background: var(--primary-color);
  }
}

/* Smooth scrolling for the page */
html {
  scroll-behavior: smooth;
}

/* Better focus states for accessibility */
:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Animation for module cards */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.module-card {
  animation: fadeInUp 0.4s ease-out forwards;
  opacity: 0;
}

/* Add delay to each module card */
.module-card:nth-child(1) { animation-delay: 0.1s; }
.module-card:nth-child(2) { animation-delay: 0.2s; }
.module-card:nth-child(3) { animation-delay: 0.3s; }
.module-card:nth-child(4) { animation-delay: 0.4s; }
.module-card:nth-child(5) { animation-delay: 0.5s; }
.module-card:nth-child(6) { animation-delay: 0.6s; }
.module-card:nth-child(7) { animation-delay: 0.7s; }
.module-card:nth-child(8) { animation-delay: 0.8s; }

.progress-bar-wrapper.progress-bar-green :deep(.p-progressbar-value) {
  background: var(--green-500);
}

.progress-bar-wrapper.progress-bar-blue :deep(.p-progressbar-value) {
  background: var(--blue-500);
}

.progress-bar-wrapper.progress-bar-yellow :deep(.p-progressbar-value) {
  background: var(--yellow-500);
}

/* Hover Effects */
.module-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1) !important;
}

.module-card:hover .p-avatar {
  transform: scale(1.1);
}
</style>