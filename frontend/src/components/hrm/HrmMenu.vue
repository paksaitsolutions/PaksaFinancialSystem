<template>
  <div class="hrm-menu">
    <Menubar :model="menuItems" class="border-none shadow-2">
      <template #start>
        <span class="text-xl font-bold text-primary">HRM</span>
      </template>
      <template #item="{ item, hasSubmenu }">
        <router-link v-if="item['route']" :to="item['route']" class="flex align-items-center p-menuitem-link">
          <span :class="item['icon']" class="mr-2"></span>
          <span class="ml-2">{{ item['label'] }}</span>
          <span v-if="item['badge']" class="ml-auto border-round" :class="'bg-' + item['badgeClass']">
            {{ item['badge'] }}
          </span>
          <span v-if="hasSubmenu" class="ml-auto pi pi-fw pi-angle-down"></span>
        </router-link>
        <a v-else-if="item.url" :href="item.url" class="flex align-items-center p-menuitem-link" :target="item.target || '_self'">
          <span :class="item['icon']" class="mr-2"></span>
          <span class="ml-2">{{ item['label'] }}</span>
          <span v-if="item['badge']" class="ml-auto border-round" :class="'bg-' + item['badgeClass']">
            {{ item['badge'] }}
          </span>
          <span v-if="hasSubmenu" class="ml-auto pi pi-fw pi-angle-down"></span>
        </a>
      </template>
    </Menubar>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRoute } from 'vue-router';
import type { MenuItem } from 'primevue/menuitem';


/**
 * HrmMenu Component
 * 
 * @component
 */

interface MenuItemRoute {
  name: string;
  query?: Record<string, string | number | undefined>;
  params?: Record<string, string | number>;
}

interface MenuItemWithRoute extends Omit<MenuItem, 'active' | 'route'> {
  route?: MenuItemRoute;
  url?: string;
  target?: string;
  badge?: string | number;
  badgeClass?: string;
  active?: boolean;
  items?: MenuItemWithRoute[];
  command?: (event?: any) => void;
  disabled?: boolean;
  visible?: boolean;
}

export default defineComponent({
  name: 'HrmMenu',
  setup() {
    const route = useRoute();
    
    const isActive = (routeName: string, exact = true): boolean => {
      if (exact) return route.name === routeName;
      return route.name?.toString().startsWith(routeName) || false;
    };

    const menuItems = ref<MenuItemWithRoute[]>([
      {
        label: 'Dashboard',
        icon: 'pi pi-fw pi-home',
        route: { name: 'HRM' },
        get active() { return isActive('HRM'); }
      },
      {
        label: 'Employees',
        icon: 'pi pi-fw pi-users',
        route: { name: 'HrmEmployees' },
        get active() { return isActive('HrmEmployees', false); },
        items: [
          { 
            label: 'All Employees', 
            route: { 
              name: 'HrmEmployees'
            }
          },
          { 
            label: 'Add New', 
            route: { 
              name: 'HrmEmployees', 
              query: { action: 'new' } 
            }
          },
          { 
            label: 'Departments', 
            route: { 
              name: 'HrmDepartments'
            }
          },
          { 
            label: 'Positions', 
            route: { 
              name: 'HrmPositions'
            }
          }
        ]
      },
      {
        label: 'Attendance',
        icon: 'pi pi-fw pi-calendar',
        route: { name: 'HrmAttendance' },
        badge: 'New',
        badgeClass: 'primary'
      },
      {
        label: 'Leave Management',
        icon: 'pi pi-fw pi-calendar-plus',
        items: [
          { label: 'Leave Requests', route: { name: 'HrmLeaveRequests' } },
          { label: 'Leave Types', route: { name: 'HrmLeaveTypes' } },
          { label: 'Leave Calendar', route: { name: 'HrmLeaveCalendar' } },
          { label: 'Leave Balance', route: { name: 'HrmLeaveBalance' } }
        ]
      },
      {
        label: 'Recruitment',
        icon: 'pi pi-fw pi-briefcase',
        items: [
          { label: 'Job Openings', route: { name: 'HrmJobOpenings' } },
          { label: 'Candidates', route: { name: 'HrmCandidates' } },
          { label: 'Interviews', route: { name: 'HrmInterviews' } },
          { label: 'Onboarding', route: { name: 'HrmOnboarding' } }
        ]
      },
      {
        label: 'Performance',
        icon: 'pi pi-fw pi-chart-bar',
        items: [
          { label: 'Appraisals', route: { name: 'HrmAppraisals' } },
          { label: 'Goals', route: { name: 'HrmGoals' } },
          { label: 'Training', route: { name: 'HrmTraining' } },
          { label: 'Skills', route: { name: 'HrmSkills' } }
        ]
      },
      {
        label: 'Payroll',
        icon: 'pi pi-fw pi-money-bill',
        route: { name: 'Payroll' },
        badge: '2',
        badgeClass: 'primary'
      },
      {
        label: 'Reports',
        icon: 'pi pi-fw pi-chart-line',
        items: [
          { label: 'Employee Directory', route: { name: 'HrmReportDirectory' } },
          { label: 'Attendance', route: { name: 'HrmReportAttendance' } }
        ]
      },
      {
        label: 'Settings',
        icon: 'pi pi-fw pi-cog',
        items: [
          { label: 'HR Policies', route: { name: 'HrmPolicies' } },
          { label: 'Email Templates', route: { name: 'HrmEmailTemplates' } },
          { label: 'Workflows', route: { name: 'HrmWorkflows' } },
          { label: 'Custom Fields', route: { name: 'HrmCustomFields' } }
        ]
      }
    ]);

    return {
      menuItems
    };
  }
});
</script>

<style scoped>
.hrm-menu {
  margin-bottom: 1.5rem;
}

:deep(.p-menubar) {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
}

:deep(.p-menubar .p-menuitem-link) {
  padding: 0.75rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

:deep(.p-menubar .p-menuitem-link:hover) {
  background: var(--surface-hover);
}

:deep(.p-menubar .p-menuitem-link.router-link-active) {
  background: var(--primary-color);
  color: var(--primary-color-text);
}

:deep(.p-menubar .p-menuitem-link.router-link-active .pi) {
  color: var(--primary-color-text);
}

:deep(.p-menubar .p-menubar-root-list > .p-menuitem > .p-menuitem-link > .p-menuitem-text) {
  font-weight: 500;
}

:deep(.p-badge) {
  font-size: 0.7rem;
  min-width: 1.2rem;
  height: 1.2rem;
  line-height: 1.2rem;
}
</style>
