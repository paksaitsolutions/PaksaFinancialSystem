<template>
  <div class="chart-of-accounts">
    <h1>Chart of Accounts</h1>
    <p>Manage your chart of accounts structure</p>
    
    <div class="accounts-table">
      <table>
        <thead>
          <tr>
            <th>Code</th>
            <th>Name</th>
            <th>Type</th>
            <th>Balance</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="account in accounts" :key="account.id">
            <td>{{ account.code }}</td>
            <td>{{ account.name }}</td>
            <td>{{ account.type }}</td>
            <td>{{ formatCurrency(account.balance) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface Account {
  id: string;
  code: string;
  name: string;
  type: string;
  balance: number;
}

const accounts = ref<Account[]>([
  { id: '1', code: '1000', name: 'Cash', type: 'Asset', balance: 10000 },
  { id: '2', code: '1100', name: 'Accounts Receivable', type: 'Asset', balance: 5000 }
]);

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
};
</script>

<style scoped>
.chart-of-accounts {
  padding: 20px;
}

.accounts-table table {
  width: 100%;
  border-collapse: collapse;
}

.accounts-table th,
.accounts-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.accounts-table th {
  background-color: #f5f5f5;
  font-weight: 600;
}
</style>