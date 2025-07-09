<template>
  <div class="gl-module">
    <h1>General Ledger</h1>
    
    <div class="gl-dashboard">
      <div class="gl-module-cards">
        <router-link 
          v-for="module in modules" 
          :key="module.path" 
          :to="{ name: module.path }" 
          class="module-card"
        >
          <div class="module-icon">
            <i :class="module.icon"></i>
          </div>
          <h3>{{ module.name }}</h3>
          <p>{{ module.description }}</p>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GLView',
  data() {
    return {
      modules: [
        {
          name: 'Chart of Accounts',
          path: 'gl-accounts',
          icon: 'pi pi-book',
          description: 'Manage your chart of accounts and account hierarchy'
        },
        {
          name: 'Journal Entries',
          path: 'journal-entries',
          icon: 'pi pi-file-edit',
          description: 'Create and manage journal entries'
        },
        {
          name: 'Financial Statements',
          path: 'financial-statements',
          icon: 'pi pi-file-pdf',
          description: 'Generate and view financial statements'
        },
        {
          name: 'Reconciliation',
          path: 'reconciliation',
          icon: 'pi pi-sync',
          description: 'Reconcile accounts and transactions'
        },
        {
          name: 'Period Close',
          path: 'period-close',
          icon: 'pi pi-calendar-times',
          description: 'Manage period close processes'
        },
        {
          name: 'Reports',
          path: 'reports',
          icon: 'pi pi-chart-bar',
          description: 'Generate GL reports and analytics'
        }
      ]
    };
  }
};
</script>

<style scoped>
.gl-module {
  padding: 1.5rem;
}

h1 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.gl-dashboard {
  margin-top: 2rem;
}

.gl-module-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.module-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  text-decoration: none;
  color: #2c3e50;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.module-icon {
  font-size: 2rem;
  color: #3b82f6;
  margin-bottom: 1rem;
}

.module-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.module-card p {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
}
</style>
