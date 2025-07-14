<template>
  <v-container fluid class="home-page">
    <!-- Hero Section -->
    <v-row class="hero-section mb-8">
      <v-col cols="12" class="text-center">
        <v-icon size="120" color="primary" class="mb-4">
          mdi-finance
        </v-icon>
        <h1 class="text-h2 font-weight-bold mb-4">
          Welcome to Paksa Financial System
        </h1>
        <p class="text-h6 text-grey-600 mb-6">
          Comprehensive Enterprise Financial Management Solution
        </p>
        <v-btn
          color="primary"
          size="large"
          to="/dashboard"
          class="mr-4"
        >
          <v-icon left>mdi-view-dashboard</v-icon>
          Go to Dashboard
        </v-btn>
        <v-btn
          variant="outlined"
          size="large"
          href="#features"
        >
          Learn More
        </v-btn>
      </v-col>
    </v-row>

    <!-- Features Section -->
    <v-row id="features" class="features-section mb-8">
      <v-col cols="12" class="text-center mb-6">
        <h2 class="text-h3 font-weight-bold">Key Features</h2>
        <p class="text-subtitle-1 text-grey-600">
          Everything you need to manage your finances
        </p>
      </v-col>
      
      <v-col cols="12" md="4" v-for="feature in features" :key="feature.title">
        <v-card class="feature-card h-100" elevation="2">
          <v-card-text class="text-center pa-6">
            <v-avatar :color="feature.color" size="64" class="mb-4">
              <v-icon color="white" size="32">{{ feature.icon }}</v-icon>
            </v-avatar>
            <h3 class="text-h5 font-weight-bold mb-3">{{ feature.title }}</h3>
            <p class="text-body-1">{{ feature.description }}</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Stats Section -->
    <v-row class="stats-section mb-8">
      <v-col cols="12" class="text-center mb-6">
        <h2 class="text-h3 font-weight-bold">System Overview</h2>
      </v-col>
      
      <v-col cols="12" sm="6" md="3" v-for="stat in stats" :key="stat.title">
        <v-card class="stat-card text-center" elevation="1">
          <v-card-text class="pa-6">
            <div class="text-h3 font-weight-bold" :class="stat.color">
              {{ stat.value }}
            </div>
            <div class="text-subtitle-1 text-grey-600">
              {{ stat.title }}
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Access Section -->
    <v-row class="quick-access-section">
      <v-col cols="12" class="text-center mb-6">
        <h2 class="text-h3 font-weight-bold">Quick Access</h2>
        <p class="text-subtitle-1 text-grey-600">
          Jump to the most used features
        </p>
      </v-col>
      
      <v-col cols="12" sm="6" md="4" v-for="action in quickActions" :key="action.title">
        <v-card 
          class="quick-action-card" 
          elevation="2" 
          :to="action.route"
          hover
        >
          <v-card-text class="text-center pa-6">
            <v-avatar :color="action.color" size="48" class="mb-3">
              <v-icon color="white">{{ action.icon }}</v-icon>
            </v-avatar>
            <h4 class="text-h6 font-weight-bold mb-2">{{ action.title }}</h4>
            <p class="text-body-2 text-grey-600">{{ action.description }}</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
const features = [
  {
    title: 'General Ledger',
    description: 'Complete chart of accounts management with journal entries and financial reporting',
    icon: 'mdi-book-open-variant',
    color: 'blue'
  },
  {
    title: 'Accounts Payable',
    description: 'Vendor management, invoice processing, and automated payment workflows',
    icon: 'mdi-credit-card-outline',
    color: 'red'
  },
  {
    title: 'Accounts Receivable',
    description: 'Customer invoicing, payment tracking, and collections management',
    icon: 'mdi-cash-multiple',
    color: 'green'
  },
  {
    title: 'Payroll Management',
    description: 'Employee payroll processing with tax calculations and compliance',
    icon: 'mdi-account-group',
    color: 'orange'
  },
  {
    title: 'Cash Management',
    description: 'Bank reconciliation, cash flow forecasting, and liquidity planning',
    icon: 'mdi-bank',
    color: 'teal'
  },
  {
    title: 'Fixed Assets',
    description: 'Asset lifecycle management with depreciation and maintenance tracking',
    icon: 'mdi-factory',
    color: 'purple'
  }
]

const stats = [
  { title: 'Active Accounts', value: '150+', color: 'text-blue' },
  { title: 'Monthly Transactions', value: '2.5K+', color: 'text-green' },
  { title: 'Employees', value: '45', color: 'text-orange' },
  { title: 'Reports Generated', value: '500+', color: 'text-purple' }
]

const quickActions = [
  {
    title: 'Dashboard',
    description: 'View financial overview and key metrics',
    icon: 'mdi-view-dashboard',
    color: 'primary',
    route: '/dashboard'
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
    title: 'Reports',
    description: 'Generate financial reports',
    icon: 'mdi-chart-line',
    color: 'orange',
    route: '/reports'
  },
  {
    title: 'Payroll',
    description: 'Process employee payroll',
    icon: 'mdi-account-cash',
    color: 'teal',
    route: '/payroll'
  },
  {
    title: 'Settings',
    description: 'Configure system settings',
    icon: 'mdi-cog',
    color: 'grey',
    route: '/settings'
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