<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Hero Section -->
    <div class="bg-white">
      <div class="max-w-7xl mx-auto py-16 px-4 sm:py-24 sm:px-6 lg:px-8 text-center">
        <h1 class="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
          <span class="block">Paksa Financial System</span>
          <span class="block text-blue-600">Financial Management Simplified</span>
        </h1>
        <p class="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          Streamline your financial operations with our comprehensive accounting and financial management solution.
        </p>
        <div class="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
          <div class="rounded-md shadow">
            <router-link to="/login" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10">
              Get Started
            </router-link>
          </div>
          <div class="mt-3 rounded-md shadow sm:mt-0 sm:ml-3">
            <router-link to="/features" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10">
              Learn more
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="py-12 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="lg:text-center">
          <h2 class="text-base text-blue-600 font-semibold tracking-wide uppercase">Features</h2>
          <p class="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
            Everything you need to manage your finances
          </p>
          <p class="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
            Comprehensive financial tools designed to help you stay in control of your business finances.
          </p>
        </div>

        <div class="mt-10">
          <div class="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
            <div v-for="feature in features" :key="feature.title" class="relative">
              <div class="absolute flex items-center justify-center h-12 w-12 rounded-md" :class="feature.bgColor">
                <svg class="h-6 w-6" :class="feature.textColor" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="feature.icon" />
                </svg>
              </div>
              <div class="ml-16">
                <h3 class="text-lg leading-6 font-medium text-gray-900">{{ feature.title }}</h3>
                <p class="mt-2 text-base text-gray-500">
                  {{ feature.description }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CTA Section -->
    <section class="py-16 bg-blue-600 text-white">
      <div class="container mx-auto px-4 text-center">
        <h2 class="text-3xl md:text-4xl font-bold mb-6">Ready to get started?</h2>
        <p class="text-xl mb-8 max-w-2xl mx-auto">Join thousands of businesses managing their finances with Paksa Financial System</p>
        <router-link to="/register" class="inline-block bg-white text-blue-600 hover:bg-gray-100 font-semibold py-3 px-8 rounded-lg transition duration-200">
          Get Started for Free
        </router-link>
      </div>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { RouterLink } from 'vue-router';

interface Feature {
  title: string;
  description: string;
  icon: string;
  bgColor: string;
  textColor: string;
}

export default defineComponent({
  name: 'HomeView',
  components: {
    RouterLink
  },
  data() {
    return {
      features: [
        {
          title: 'General Ledger',
          description: 'Comprehensive financial record keeping with multi-currency support and real-time reporting',
          icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
          bgColor: 'bg-blue-100',
          textColor: 'text-blue-600'
        },
        {
          title: 'Accounts Payable',
          description: 'Streamline vendor payments and track expenses efficiently with automated workflows',
          icon: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.1-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
          bgColor: 'bg-green-100',
          textColor: 'text-green-600'
        },
        {
          title: 'Accounts Receivable',
          description: 'Manage customer invoices and track payments with automated reminders',
          icon: 'M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z',
          bgColor: 'bg-purple-100',
          textColor: 'text-purple-600'
        },
        {
          title: 'Financial Reporting',
          description: 'Generate detailed financial statements, analytics, and custom reports',
          icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
          bgColor: 'bg-yellow-100',
          textColor: 'text-yellow-600'
        },
        {
          title: 'Budget Management',
          description: 'Create, track, and analyze budgets across departments and projects',
          icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01',
          bgColor: 'bg-red-100',
          textColor: 'text-red-600'
        },
        {
          title: 'Tax Compliance',
          description: 'Stay compliant with automated tax calculations and reporting',
          icon: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
          bgColor: 'bg-indigo-100',
          textColor: 'text-indigo-600'
        }
      ] as Feature[]
    };
  }  title: 'Dashboard',
    description: 'View financial overview and key metrics',
    icon: 'mdi-view-dashboard',
    color: 'primary',
    route: '/dashboard'
  },
  {
    title: 'Tax Management',
    description: 'Access tax dashboard and tools',
    icon: 'mdi-calculator',
    color: 'purple',
    route: '/tax/dashboard'
  },
  {
    title: 'Chart of Accounts',
    description: 'Manage your chart of accounts',
    icon: 'mdi-format-list-bulleted',
    color: 'blue',
    route: '/gl/accounts'
  },
  {
    title: 'Journal Entries',
    description: 'Create and manage journal entries',
    icon: 'mdi-book-plus',
    color: 'green',
    route: '/gl/journal-entries'
  },
  {
    title: 'Tax Compliance',
    description: 'View tax compliance status',
    icon: 'mdi-shield-check',
    color: 'teal',
    route: '/tax/compliance'
  },
  {
    title: 'Reports',
    description: 'Generate financial and tax reports',
    icon: 'mdi-chart-line',
    color: 'orange',
    route: '/reports'
  }
]
</script>

<style scoped>
.home-page {
  min-height: 100vh;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 0;
  margin: -24px -24px 0 -24px;
}

.feature-card {
  transition: transform 0.2s ease-in-out;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.stat-card {
  transition: transform 0.2s ease-in-out;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.quick-action-card {
  transition: all 0.2s ease-in-out;
  cursor: pointer;
}

.quick-action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.features-section,
.stats-section,
.quick-access-section {
  padding: 60px 0;
}
</style>