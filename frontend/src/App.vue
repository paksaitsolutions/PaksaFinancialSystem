<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-container">
        <router-link to="/" class="nav-brand">
          <img src="/src/assets/logo.svg" alt="Paksa" class="nav-logo" />
        </router-link>
        <div class="nav-links">
          <router-link to="/" class="nav-link">Home</router-link>
          <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">General Ledger</span>
            <div class="dropdown-menu">
              <router-link to="/gl/advanced" class="dropdown-item">GL Dashboard</router-link>
              <router-link to="/gl/accounts" class="dropdown-item">Chart of Accounts</router-link>
              <router-link to="/gl/journal-entries" class="dropdown-item">Journal Entries</router-link>
              <router-link to="/gl/trial-balance" class="dropdown-item">Trial Balance</router-link>
            </div>
          </div>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">Accounts Payable</span>
            <div class="dropdown-menu">
              <router-link to="/ap/vendors" class="dropdown-item">Vendors</router-link>
              <router-link to="/ap/invoices" class="dropdown-item">AP Invoices</router-link>
              <router-link to="/ap/payments" class="dropdown-item">Payments</router-link>
              <router-link to="/ap/analytics" class="dropdown-item">Analytics</router-link>
            </div>
          </div>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">Accounts Receivable</span>
            <div class="dropdown-menu">
              <router-link to="/ar/customers" class="dropdown-item">Customers</router-link>
              <router-link to="/ar/invoices" class="dropdown-item">AR Invoices</router-link>
              <router-link to="/ar/payments" class="dropdown-item">Payments</router-link>
              <router-link to="/ar/analytics" class="dropdown-item">AI Analytics</router-link>
            </div>
          </div>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">Payroll</span>
            <div class="dropdown-menu">
              <router-link to="/payroll/employees" class="dropdown-item">Employees</router-link>
              <router-link to="/payroll/process" class="dropdown-item">Process Payroll</router-link>
              <router-link to="/payroll/reports" class="dropdown-item">Payroll Reports</router-link>
            </div>
          </div>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">Cash Management</span>
            <div class="dropdown-menu">
              <router-link to="/cash/accounts" class="dropdown-item">Bank Accounts</router-link>
              <router-link to="/cash/reconciliation" class="dropdown-item">Reconciliation</router-link>
              <router-link to="/cash/forecast" class="dropdown-item">Cash Forecast</router-link>
            </div>
          </div>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">Fixed Assets</span>
            <div class="dropdown-menu">
              <router-link to="/assets/list" class="dropdown-item">Asset List</router-link>
              <router-link to="/assets/depreciation" class="dropdown-item">Depreciation</router-link>
              <router-link to="/assets/maintenance" class="dropdown-item">Maintenance</router-link>
            </div>
          </div>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">Tax</span>
            <div class="dropdown-menu">
              <router-link to="/tax/exemption-certificate" class="dropdown-item">Tax Exemption Certificate</router-link>
              <router-link to="/tax/policy" class="dropdown-item">Tax Policy</router-link>
            </div>
          </div>
          <div class="nav-dropdown">
            <span class="nav-link dropdown-toggle">Reports</span>
            <div class="dropdown-menu">
              <router-link to="/reports" class="dropdown-item">All Reports</router-link>
              <router-link to="/reports/ar" class="dropdown-item">AR Reports</router-link>
            </div>
          </div>
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
  padding: 0;
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
  height: 64px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.nav-logo {
  height: 40px;
  width: auto;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 20px 16px;
  transition: background 0.3s ease;
  white-space: nowrap;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.2);
}

.nav-dropdown {
  position: relative;
}

.dropdown-toggle {
  cursor: pointer;
  padding: 20px 16px;
}

.dropdown-menu {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  min-width: 180px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 4px;
  z-index: 1000;
  margin-top: 0;
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
}

.dropdown-item:hover {
  background: #f5f5f5;
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

<style>
@import './assets/styles/ap-advanced.css';
@import './assets/styles/ap-analytics.css';
</style>
