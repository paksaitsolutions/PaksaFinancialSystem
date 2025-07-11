<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="nav-brand">
          🏢 Paksa Financial System
        </router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link">🏠 Home</router-link>
          <router-link to="/dashboard" class="nav-link">📊 Dashboard</router-link>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">📚 General Ledger</span>
            <div class="dropdown-menu">
              <router-link to="/gl/accounts" class="dropdown-item">Chart of Accounts</router-link>
              <router-link to="/gl/journal-entries" class="dropdown-item">Journal Entries</router-link>
              <router-link to="/gl/trial-balance" class="dropdown-item">Trial Balance</router-link>
            </div>
          </div>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">💳 Accounts Payable</span>
            <div class="dropdown-menu">
              <router-link to="/ap/vendors" class="dropdown-item">Vendors</router-link>
              <router-link to="/ap/invoices" class="dropdown-item">AP Invoices</router-link>
              <router-link to="/ap/payments" class="dropdown-item">Payments</router-link>
            </div>
          </div>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">💰 Accounts Receivable</span>
            <div class="dropdown-menu">
              <router-link to="/ar/customers" class="dropdown-item">Customers</router-link>
              <router-link to="/ar/invoices" class="dropdown-item">AR Invoices</router-link>
              <router-link to="/ar/payments" class="dropdown-item">Payments</router-link>
            </div>
          </div>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">👥 Payroll</span>
            <div class="dropdown-menu">
              <router-link to="/payroll/employees" class="dropdown-item">Employees</router-link>
              <router-link to="/payroll/process" class="dropdown-item">Process Payroll</router-link>
              <router-link to="/payroll/reports" class="dropdown-item">Payroll Reports</router-link>
            </div>
          </div>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">🏦 Cash Management</span>
            <div class="dropdown-menu">
              <router-link to="/cash/accounts" class="dropdown-item">Bank Accounts</router-link>
              <router-link to="/cash/reconciliation" class="dropdown-item">Reconciliation</router-link>
              <router-link to="/cash/forecast" class="dropdown-item">Cash Forecast</router-link>
            </div>
          </div>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">🏭 Fixed Assets</span>
            <div class="dropdown-menu">
              <router-link to="/assets/list" class="dropdown-item">Asset List</router-link>
              <router-link to="/assets/depreciation" class="dropdown-item">Depreciation</router-link>
              <router-link to="/assets/maintenance" class="dropdown-item">Maintenance</router-link>
            </div>
          </div>
          <router-link to="/reports" class="nav-link">📈 Reports</router-link>
        </div>
      </div>
    </nav>
    
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  color: #333;
}

.navbar {
  background: #1976D2;
  color: white;
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background 0.3s ease;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.2);
}

.nav-dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-toggle {
  cursor: pointer;
}

.dropdown-menu {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  min-width: 160px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 6px;
  z-index: 1000;
  margin-top: 8px;
  border: 1px solid #e0e0e0;
}

.nav-dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  display: block;
  padding: 12px 16px;
  color: #333;
  text-decoration: none;
  font-size: 0.9rem;
  transition: background 0.2s ease;
  white-space: nowrap;
}

.dropdown-item:hover {
  background: #1976D2;
  color: white;
}

.dropdown-item:first-child {
  border-radius: 6px 6px 0 0;
}

.dropdown-item:last-child {
  border-radius: 0 0 6px 6px;
}

.main-content {
  min-height: calc(100vh - 80px);
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
    padding: 0 15px;
  }
  
  .nav-links {
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .nav-link {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
  
  .dropdown-menu {
    position: fixed;
    left: 50%;
    transform: translateX(-50%);
    min-width: 200px;
  }
}
</style>
