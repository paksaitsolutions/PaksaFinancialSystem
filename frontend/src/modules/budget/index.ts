import { App } from 'vue';
import { createPinia } from 'pinia';
import budgetRoutes from '@/router/modules/budget';

// Import stores
import { useBudgetStore } from './store/budgetStore';

// Import components
import BudgetDashboard from './views/BudgetDashboard.vue';
import BudgetList from './views/BudgetList.vue';
import CreateBudget from './views/CreateBudget.vue';
import EditBudget from './views/EditBudget.vue';
import BudgetDetails from './views/BudgetDetails.vue';
import BudgetScenarios from './views/BudgetScenarios.vue';
import BudgetForecasting from './views/BudgetForecasting.vue';
import BudgetReports from './views/BudgetReports.vue';
import BudgetSettings from './views/BudgetSettings.vue';

// Import types
export * from './types/budget';
export * from './types/scenario';

export default {
  install: (app: App) => {
    const pinia = createPinia();
    app.use(pinia);
    
    // Register components
    app.component('BudgetDashboard', BudgetDashboard);
    app.component('BudgetList', BudgetList);
    app.component('CreateBudget', CreateBudget);
    app.component('EditBudget', EditBudget);
    app.component('BudgetDetails', BudgetDetails);
    app.component('BudgetScenarios', BudgetScenarios);
    app.component('BudgetForecasting', BudgetForecasting);
    app.component('BudgetReports', BudgetReports);
    app.component('BudgetSettings', BudgetSettings);
    
    // Register store
    const budgetStore = useBudgetStore();
    app.provide('budgetStore', budgetStore);
  },
  routes: [budgetRoutes]
};
