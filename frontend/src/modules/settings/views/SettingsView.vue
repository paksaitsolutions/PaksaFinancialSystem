<template>
  <div class="settings-container p-4">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1 class="text-3xl font-bold text-900 m-0">Settings</h1>
    </div>
    
    <div class="settings-layout">
      <div class="settings-navigation mb-4">
        <div class="flex flex-wrap gap-2">
          <Button 
            :class="{ 'p-button-outlined': $route.name !== 'GeneralSettings' }"
            label="General" 
            icon="pi pi-cog" 
            @click="$router.push({ name: 'GeneralSettings' })"
          />
          <Button 
            :class="{ 'p-button-outlined': $route.name !== 'CompanyProfile' }"
            label="Company" 
            icon="pi pi-building" 
            @click="$router.push({ name: 'CompanyProfile' })"
          />
          <Button 
            :class="{ 'p-button-outlined': $route.name !== 'ChartOfAccounts' }"
            label="Accounts" 
            icon="pi pi-list" 
            @click="$router.push({ name: 'ChartOfAccounts' })"
          />
          <Button 
            :class="{ 'p-button-outlined': $route.name !== 'TaxRates' }"
            label="Tax Rates" 
            icon="pi pi-calculator" 
            @click="$router.push({ name: 'TaxRates' })"
          />
          <Button 
            :class="{ 'p-button-outlined': $route.name !== 'UserManagement' }"
            label="Users" 
            icon="pi pi-users" 
            @click="$router.push({ name: 'UserManagement' })"
          />
          <Button 
            :class="{ 'p-button-outlined': $route.name !== 'SystemPreferences' }"
            label="System" 
            icon="pi pi-desktop" 
            @click="$router.push({ name: 'SystemPreferences' })"
          />
          <Button 
            :class="{ 'p-button-outlined': $route.name !== 'IntegrationSettings' }"
            label="Integrations" 
            icon="pi pi-link" 
            @click="$router.push({ name: 'IntegrationSettings' })"
          />
          <Button 
            :class="{ 'p-button-outlined': $route.name !== 'BackupRestore' }"
            label="Backup" 
            icon="pi pi-cloud-upload" 
            @click="$router.push({ name: 'BackupRestore' })"
          />
          <Button 
            :class="{ 'p-button-outlined': $route.name !== 'SecuritySettings' }"
            label="Security" 
            icon="pi pi-shield" 
            @click="$router.push({ name: 'SecuritySettings' })"
          />
        </div>
      </div>
      
      <div class="settings-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// No imports needed as we're using router-view
</script>

<style scoped>
.settings-container {
  max-width: 1200px;
  margin: 0 auto;
}

.settings-navigation .p-button {
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
}

.settings-content {
  min-height: 500px;
}

@media (max-width: 768px) {
  .settings-navigation .flex {
    flex-direction: column;
  }
  
  .settings-navigation .p-button {
    width: 100%;
    margin-right: 0;
  }
}
</style>