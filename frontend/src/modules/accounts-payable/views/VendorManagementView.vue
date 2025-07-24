<template>
  <div class="vendor-management">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <h1 class="text-h4 mb-4">Vendor Management</h1>
          
          <v-tabs v-model="activeTab" bg-color="primary">
            <v-tab value="vendors">Vendors</v-tab>
            <v-tab value="reports">Reports</v-tab>
            <v-tab value="settings">Settings</v-tab>
          </v-tabs>
          
          <v-window v-model="activeTab" class="mt-4">
            <v-window-item value="vendors">
              <vendor-list />
            </v-window-item>
            
            <v-window-item value="reports">
              <v-card>
                <v-card-text>
                  <h3 class="text-h6 mb-4">Vendor Reports</h3>
                  <p>Vendor reporting features will be implemented in a future update.</p>
                </v-card-text>
              </v-card>
            </v-window-item>
            
            <v-window-item value="settings">
              <v-card>
                <v-card-text>
                  <h3 class="text-h6 mb-4">Vendor Settings</h3>
                  <p>Vendor configuration settings will be implemented in a future update.</p>
                </v-card-text>
              </v-card>
            </v-window-item>
          </v-window>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import VendorList from '../components/vendor/VendorList.vue';

// Data
const activeTab = ref('vendors');
</script>

<style scoped>
.vendor-management {
  padding: 16px;
}
</style>