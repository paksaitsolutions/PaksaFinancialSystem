<template>
  <v-navigation-drawer v-model="drawer" app>
    <v-list>
      <v-list-item
        v-for="item in menuItems"
        :key="item.title"
        :to="item.to"
        link
      >
        <template v-slot:prepend>
          <v-icon>{{ item.icon }}</v-icon>
        </template>
        <v-list-item-title>{{ item.title }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const drawer = ref(true);

const menuItems = [
  { title: 'Dashboard', icon: 'mdi-home', to: '/' },
  { title: 'Accounts Payable', icon: 'mdi-credit-card', to: '/ap' },
  { title: 'Accounts Receivable', icon: 'mdi-cash', to: '/ar' },
  { title: 'General Ledger', icon: 'mdi-book', to: '/gl' },
  { title: 'Payroll', icon: 'mdi-account-group', to: '/payroll' },
  { title: 'Inventory', icon: 'mdi-package-variant', to: '/inventory' },
  { title: 'Reports', icon: 'mdi-chart-bar', to: '/reports' }
];
</script>