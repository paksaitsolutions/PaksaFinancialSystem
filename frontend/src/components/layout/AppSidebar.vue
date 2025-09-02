<template>
  <div class="sidebar-content">
    <div class="sidebar-menu">
      <ul class="menu-list">
        <li v-for="item in menuItems" :key="item.label" class="menu-item">
          <router-link 
            v-if="!item.items" 
            :to="item.to" 
            class="menu-link"
            :class="{ 'active': isActiveRoute(item.to) }"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </router-link>
          
          <div 
            v-else 
            class="menu-header"
            @click="toggleSubmenu(item.label)"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
            <i class="pi pi-chevron-down toggle-icon" :class="{ 'rotated': expandedMenus.includes(item.label) }"></i>
          </div>
          
          <ul v-if="item.items && expandedMenus.includes(item.label)" class="submenu">
            <li v-for="child in item.items" :key="child.label">
              <router-link 
                :to="child.to" 
                class="submenu-link"
                :class="{ 'active': isActiveRoute(child.to) }"
              >
                <i :class="child.icon"></i>
                <span>{{ child.label }}</span>
              </router-link>
            </li>
          </ul>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const expandedMenus = ref(['Financial Management'])

const menuItems = [
  {
    label: 'Dashboard',
    icon: 'pi pi-home',
    to: '/'
  },
  {
    label: 'Financial Management',
    icon: 'pi pi-chart-line',
    items: [
      {
        label: 'General Ledger',
        icon: 'pi pi-book',
        to: '/gl'
      },
      {
        label: 'Accounts Payable',
        icon: 'pi pi-shopping-cart',
        to: '/ap'
      },
      {
        label: 'Accounts Receivable',
        icon: 'pi pi-credit-card',
        to: '/ar'
      },
      {
        label: 'Cash Management',
        icon: 'pi pi-wallet',
        to: '/cash'
      }
    ]
  },
  {
    label: 'Operations',
    icon: 'pi pi-cog',
    items: [
      {
        label: 'Inventory',
        icon: 'pi pi-box',
        to: '/inventory'
      },
      {
        label: 'Fixed Assets',
        icon: 'pi pi-building',
        to: '/fixed-assets'
      },
      {
        label: 'Budget Management',
        icon: 'pi pi-calculator',
        to: '/budget'
      }
    ]
  },
  {
    label: 'Human Resources',
    icon: 'pi pi-users',
    items: [
      {
        label: 'HRM',
        icon: 'pi pi-user',
        to: '/hrm'
      },
      {
        label: 'Payroll',
        icon: 'pi pi-dollar',
        to: '/payroll'
      }
    ]
  },
  {
    label: 'Tax Management',
    icon: 'pi pi-percentage',
    items: [
      {
        label: 'Dashboard',
        icon: 'pi pi-home',
        to: '/tax'
      },
      {
        label: 'Tax Codes',
        icon: 'pi pi-tags',
        to: '/tax/codes'
      },
      {
        label: 'Tax Rates',
        icon: 'pi pi-percentage',
        to: '/tax/rates'
      },
      {
        label: 'Tax Returns',
        icon: 'pi pi-file',
        to: '/tax/returns'
      },
      {
        label: 'Compliance',
        icon: 'pi pi-check-circle',
        to: '/tax/compliance'
      }
    ]
  },
  {
    label: 'Reports',
    icon: 'pi pi-file-pdf',
    items: [
      {
        label: 'All Reports',
        icon: 'pi pi-list',
        to: '/reports'
      },
      {
        label: 'Financial Reports',
        icon: 'pi pi-chart-line',
        to: '/reports/financial'
      },
      {
        label: 'Operational Reports',
        icon: 'pi pi-cog',
        to: '/reports/operational'
      },
      {
        label: 'Compliance Reports',
        icon: 'pi pi-shield',
        to: '/reports/compliance'
      },
      {
        label: 'Custom Reports',
        icon: 'pi pi-wrench',
        to: '/reports/custom'
      }
    ]
  },
  {
    label: 'AI & Business Intelligence',
    icon: 'pi pi-chart-line',
    items: [
      {
        label: 'AI Dashboard',
        icon: 'pi pi-chart-bar',
        to: '/ai-bi'
      },
      {
        label: 'AI Assistant',
        icon: 'pi pi-comments',
        to: '/ai-bi/assistant'
      },
      {
        label: 'Business Intelligence',
        icon: 'pi pi-chart-pie',
        to: '/ai-bi/intelligence'
      },
      {
        label: 'Analytics Reports',
        icon: 'pi pi-file-pdf',
        to: '/ai-bi/reports'
      }
    ]
  },
  {
    label: 'Settings',
    icon: 'pi pi-cog',
    items: [
      {
        label: 'General Settings',
        icon: 'pi pi-sliders-h',
        to: '/settings/general'
      },
      {
        label: 'User Management',
        icon: 'pi pi-users',
        to: '/settings/users'
      },
      {
        label: 'Tenant Management',
        icon: 'pi pi-building',
        to: '/settings/tenant'
      },
      {
        label: 'Security Settings',
        icon: 'pi pi-shield',
        to: '/settings/security'
      }
    ]
  }
]

const isActiveRoute = (path: string) => {
  return route.path === path || (path !== '/' && route.path.startsWith(path))
}

const toggleSubmenu = (label: string) => {
  const index = expandedMenus.value.indexOf(label)
  if (index > -1) {
    expandedMenus.value.splice(index, 1)
  } else {
    expandedMenus.value.push(label)
  }
}
</script>

<style scoped>
.sidebar-content {
  height: 100%;
  overflow-y: auto;
  background: #ffffff;
}

.sidebar-menu {
  padding: 1rem 0;
}

.menu-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.menu-item {
  margin: 0;
}

.menu-link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  color: #374151;
  text-decoration: none;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.menu-link:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.menu-link.active {
  background: #3b82f6;
  color: white;
  border-left-color: #1d4ed8;
}

.menu-header {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  color: #6b7280;
  font-weight: 600;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
}

.menu-header:hover {
  background: #f9fafb;
}

.menu-link i,
.menu-header i {
  margin-right: 0.75rem;
  width: 1rem;
}

.toggle-icon {
  margin-left: auto !important;
  margin-right: 0 !important;
  transition: transform 0.2s;
  font-size: 0.75rem;
}

.toggle-icon.rotated {
  transform: rotate(180deg);
}

.submenu {
  list-style: none;
  margin: 0;
  padding: 0;
  background: #f9fafb;
}

.submenu-link {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  color: #4b5563;
  text-decoration: none;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.submenu-link:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.submenu-link.active {
  background: #dbeafe;
  color: #1d4ed8;
  border-left: 3px solid #3b82f6;
}

.submenu-link i {
  margin-right: 0.5rem;
  width: 0.875rem;
  font-size: 0.875rem;
}
</style>