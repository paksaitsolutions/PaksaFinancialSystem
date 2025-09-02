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
            :class="{ 'p-button-outlined': $route.name !== 'UserManagement' }"
            label="Users" 
            icon="pi pi-users" 
            @click="$router.push({ name: 'UserManagement' })"
          />
          <Button 
            :class="{ 'p-button-outlined': $route.name !== 'TenantSettings' }"
            label="Tenant" 
            icon="pi pi-building" 
            @click="$router.push({ name: 'TenantSettings' })"
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