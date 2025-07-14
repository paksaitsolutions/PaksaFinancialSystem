<template>
  <div class="home-page">
    <!-- Header -->
    <header class="hero-section">
      <div class="container">
        <div class="hero-content">
          <div class="hero-icon">💰</div>
          <h1>Welcome to Paksa Financial System</h1>
          <p>Comprehensive Enterprise Financial Management Solution</p>
          <div class="hero-buttons">
            <button class="btn btn-primary" @click="$router.push('/dashboard')">
              📊 Go to Dashboard
            </button>
            <button class="btn btn-secondary" @click="scrollToFeatures">
              📖 Learn More
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Features Section -->
    <section id="features" class="features-section">
      <div class="container">
        <h2>Key Features</h2>
        <p class="subtitle">Everything you need to manage your finances</p>
        
        <div class="features-grid">
          <div class="feature-card" v-for="feature in features" :key="feature.title">
            <div class="feature-icon">{{ feature.icon }}</div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section">
      <div class="container">
        <h2>System Overview</h2>
        <div class="stats-grid">
          <div class="stat-card" v-for="stat in stats" :key="stat.title">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-title">{{ stat.title }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Quick Access Section -->
    <section class="quick-access-section">
      <div class="container">
        <h2>Quick Access</h2>
        <p class="subtitle">Jump to the most used features</p>
        
        <div class="actions-grid">
          <div 
            class="action-card" 
            v-for="action in quickActions" 
            :key="action.title"
            @click="$router.push(action.route)"
          >
            <div class="action-icon">{{ action.icon }}</div>
            <h4>{{ action.title }}</h4>
            <p>{{ action.description }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const features = [
  {
    title: 'General Ledger',
    description: 'Complete chart of accounts management with journal entries',
    icon: '📚'
  },
  {
    title: 'Accounts Payable',
    description: 'Vendor management and invoice processing',
    icon: '💳'
  },
  {
    title: 'Accounts Receivable',
    description: 'Customer invoicing and payment tracking',
    icon: '💰'
  },
  {
    title: 'Payroll Management',
    description: 'Employee payroll processing with tax calculations',
    icon: '👥'
  },
  {
    title: 'Cash Management',
    description: 'Bank reconciliation and cash flow forecasting',
    icon: '🏦'
  },
  {
    title: 'Fixed Assets',
    description: 'Asset lifecycle management and depreciation',
    icon: '🏭'
  }
]

const stats = [
  { title: 'Active Accounts', value: '150+' },
  { title: 'Monthly Transactions', value: '2.5K+' },
  { title: 'Employees', value: '45' },
  { title: 'Reports Generated', value: '500+' }
]

const quickActions = [
  {
    title: 'Dashboard',
    description: 'View financial overview',
    icon: '📊',
    route: '/dashboard'
  },
  {
    title: 'Chart of Accounts',
    description: 'Manage accounts',
    icon: '📋',
    route: '/gl/accounts'
  },
  {
    title: 'Journal Entries',
    description: 'Create entries',
    icon: '➕',
    route: '/gl/journal-entries'
  },
  {
    title: 'Reports',
    description: 'Generate reports',
    icon: '📈',
    route: '/reports'
  },
  {
    title: 'Payroll',
    description: 'Process payroll',
    icon: '💼',
    route: '/payroll'
  },
  {
    title: 'Settings',
    description: 'Configure system',
    icon: '⚙️',
    route: '/settings'
  }
]

const scrollToFeatures = () => {
  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 100px 0;
  text-align: center;
}

.hero-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.hero-section h1 {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 20px;
}

.hero-section p {
  font-size: 1.5rem;
  margin-bottom: 40px;
  opacity: 0.9;
}

.hero-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 15px 30px;
  font-size: 1.1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: #1976D2;
  color: white;
}

.btn-primary:hover {
  background: #1565C0;
  transform: translateY(-2px);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: white;
  color: #667eea;
}

/* Features Section */
.features-section {
  padding: 80px 0;
  background: #f8f9fa;
}

.features-section h2 {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 20px;
  color: #333;
}

.subtitle {
  text-align: center;
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 60px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

/* Stats Section */
.stats-section {
  padding: 80px 0;
  background: white;
}

.stats-section h2 {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 60px;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
}

.stat-card {
  text-align: center;
  padding: 30px;
  background: #f8f9fa;
  border-radius: 12px;
}

.stat-value {
  font-size: 3rem;
  font-weight: bold;
  color: #1976D2;
  margin-bottom: 10px;
}

.stat-title {
  font-size: 1.1rem;
  color: #666;
}

/* Quick Access Section */
.quick-access-section {
  padding: 80px 0;
  background: #f8f9fa;
}

.quick-access-section h2 {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 20px;
  color: #333;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.action-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.action-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.action-card h4 {
  font-size: 1.3rem;
  margin-bottom: 10px;
  color: #333;
}

.action-card p {
  color: #666;
  font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 768px) {
  .hero-section h1 {
    font-size: 2rem;
  }
  
  .hero-section p {
    font-size: 1.2rem;
  }
  
  .hero-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .features-grid,
  .stats-grid,
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>