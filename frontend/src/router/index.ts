import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import DashboardView from '@/views/compliance/DashboardView.vue';
import EventsView from '@/views/compliance/security/EventsView.vue';
import PoliciesView from '@/views/compliance/security/PoliciesView.vue';
import EncryptionView from '@/views/compliance/security/EncryptionView.vue';
import EncryptionKeysView from '@/views/compliance/security/EncryptionKeysView.vue';
import SettingsView from '@/views/compliance/SettingsView.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/compliance/dashboard',
  },
  {
    path: '/compliance/dashboard',
    name: 'ComplianceDashboard',
    component: DashboardView,
  },
  {
    path: '/compliance/security/events',
    name: 'SecurityEvents',
    component: EventsView,
  },
  {
    path: '/compliance/security/policies',
    name: 'SecurityPolicies',
    component: PoliciesView,
  },
  {
    path: '/compliance/security/encryption',
    name: 'SecurityEncryption',
    component: EncryptionView,
  },
  {
    path: '/compliance/security/encryption-keys',
    name: 'SecurityEncryptionKeys',
    component: EncryptionKeysView,
  },
  {
    path: '/compliance/settings',
    name: 'ComplianceSettings',
    component: SettingsView,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
