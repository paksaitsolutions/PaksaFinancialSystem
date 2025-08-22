<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <h1 class="text-h4">Vendor Management</h1>
          <v-btn color="primary" @click="showAddVendor = true">
            <v-icon left>mdi-plus</v-icon>
            Add Vendor
          </v-btn>
        </div>
        
        <v-tabs v-model="activeTab">
          <v-tab value="list">Vendor List</v-tab>
          <v-tab value="approvals">Approvals</v-tab>
          <v-tab value="performance">Performance</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="list">
            <vendor-list @edit="editVendor" @view-performance="viewPerformance" />
          </v-window-item>
          
          <v-window-item value="approvals">
            <vendor-approvals @approve="approveVendor" @reject="rejectVendor" />
          </v-window-item>
          
          <v-window-item value="performance">
            <vendor-performance-dashboard />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
    
    <!-- Add/Edit Vendor Dialog -->
    <vendor-form-dialog 
      v-model="showAddVendor" 
      :vendor="selectedVendor"
      @save="saveVendor"
    />
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import VendorList from '../components/vendor/VendorList.vue'
import VendorFormDialog from '../components/vendor/VendorFormDialog.vue'
import VendorApprovals from '../components/vendor/VendorApprovals.vue'
import VendorPerformanceDashboard from '../components/vendor/VendorPerformanceDashboard.vue'
import { useVendorStore } from '../store/vendors'

const vendorStore = useVendorStore()
const activeTab = ref('list')
const showAddVendor = ref(false)
const selectedVendor = ref(null)

const editVendor = (vendor) => {
  selectedVendor.value = vendor
  showAddVendor.value = true
}

const viewPerformance = (vendor) => {
  selectedVendor.value = vendor
  activeTab.value = 'performance'
}

const saveVendor = async (vendorData) => {
  if (selectedVendor.value) {
    await vendorStore.updateVendor(selectedVendor.value.id, vendorData)
  } else {
    await vendorStore.createVendor(vendorData)
  }
  showAddVendor.value = false
  selectedVendor.value = null
}

const approveVendor = async (vendorId, approvalData) => {
  await vendorStore.approveVendor(vendorId, approvalData)
}

const rejectVendor = async (vendorId, rejectionData) => {
  await vendorStore.rejectVendor(vendorId, rejectionData)
}
</script>

<style scoped>
.vendor-management {
  padding: 16px;
}
</style>