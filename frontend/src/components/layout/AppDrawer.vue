<template>
  <v-navigation-drawer v-model="drawerModel" app>
    <v-list>
      <v-list-item
        prepend-avatar="/src/assets/logo.svg"
        title="Paksa Financial"
        subtitle="Enterprise System"
      ></v-list-item>
    </v-list>

    <v-divider></v-divider>

    <v-list density="compact" nav>
      <v-list-item to="/" prepend-icon="mdi-view-dashboard" title="Dashboard"></v-list-item>
      
      <v-list-group value="gl">
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" prepend-icon="mdi-book-open-page-variant" title="General Ledger"></v-list-item>
        </template>
        <v-list-item to="/gl/accounts" title="Chart of Accounts"></v-list-item>
        <v-list-item to="/gl/journal-entries" title="Journal Entries"></v-list-item>
        <v-list-item to="/gl/trial-balance" title="Trial Balance"></v-list-item>
      </v-list-group>
      
      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" prepend-icon="mdi-file-document-outline" title="Accounts Payable"></v-list-item>
        </template>
        <v-list-item to="/ap/vendors" title="Vendors"></v-list-item>
        <v-list-item to="/ap/invoices" title="Invoices"></v-list-item>
        <v-list-item to="/ap/payments" title="Payments"></v-list-item>
      </v-list-group>
      
      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" prepend-icon="mdi-cash-multiple" title="Accounts Receivable"></v-list-item>
        </template>
        <v-list-item to="/ar/customers" title="Customers"></v-list-item>
        <v-list-item to="/ar/invoices" title="Invoices"></v-list-item>
        <v-list-item to="/ar/payments" title="Payments"></v-list-item>
      </v-list-group>
      
      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" prepend-icon="mdi-bank" title="Cash Management"></v-list-item>
        </template>
        <v-list-item to="/cash/accounts" title="Bank Accounts"></v-list-item>
        <v-list-item to="/cash/reconciliation" title="Reconciliation"></v-list-item>
        <v-list-item to="/cash/forecast" title="Cash Forecast"></v-list-item>
      </v-list-group>
      
      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" prepend-icon="mdi-account-cash" title="Payroll"></v-list-item>
        </template>
        <v-list-item to="/payroll/employees" title="Employees"></v-list-item>
        <v-list-item to="/payroll/process" title="Process Payroll"></v-list-item>
        <v-list-item to="/payroll/reports" title="Reports"></v-list-item>
      </v-list-group>
      
      <v-list-group>
        <template v-slot:activator="{ props }">
          <v-list-item v-bind="props" prepend-icon="mdi-calculator-variant" title="Tax"></v-list-item>
        </template>
        <v-list-item to="/tax/exemption-certificate" title="Exemption Certificates"></v-list-item>
        <v-list-item to="/tax/policy" title="Tax Policy"></v-list-item>
      </v-list-group>
    </v-list>
  </v-navigation-drawer>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  drawer: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['update:drawer']);

const drawerModel = computed({
  get: () => props.drawer,
  set: (value) => emit('update:drawer', value)
});
</script>