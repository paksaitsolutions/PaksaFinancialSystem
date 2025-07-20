<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import GlAccountList from '../components/GlAccountList.vue';
import GlImportExportDialog from '../components/GlImportExportDialog.vue';
import Button from 'primevue/button';

const router = useRouter();

// Set page title
document.title = 'GL Accounts | Paksa Financial System';

const toast = useToast();
const showImportExportDialog = ref(false);
interface GlAccount {
  id: string | number;
  code: string;
  name: string;
  type: string;
  isActive: boolean;
  // Add other account properties as needed
}

const selectedAccounts = ref<GlAccount[]>([]);

// Handle import completion
const handleImportComplete = () => {
  // Refresh the account list after import
  // This will be handled by the GlAccountList component's watchers
  toast.add({
    severity: 'success',
    summary: 'Import Complete',
    detail: 'Accounts have been imported successfully.',
    life: 5000
  });};

// Handle bulk actions
const handleBulkAction = (action: string) => {
  if (selectedAccounts.value.length === 0) {
    toast.add({
      severity: 'warn',
      summary: 'No Accounts Selected',
      detail: 'Please select one or more accounts to perform this action.',
      life: 5000
    });
    return;
  }

  switch (action) {
    case 'export':
      // Export selected accounts
      showImportExportDialog.value = true;
      break;
    case 'deactivate':
      // Deactivate selected accounts
      toast.add({
        severity: 'info',
        summary: 'Bulk Update',
        detail: `Deactivating ${selectedAccounts.value.length} accounts...`,
        life: 3000
      });
      // TODO: Implement bulk deactivation
      break;
    case 'delete':
      // Delete selected accounts
      if (confirm(`Are you sure you want to delete ${selectedAccounts.value.length} accounts? This action cannot be undone.`)) {
        toast.add({
          severity: 'info',
          summary: 'Deleting Accounts',
          detail: `Deleting ${selectedAccounts.value.length} accounts...`,
          life: 3000
        });
        // TODO: Implement bulk deletion
      }
      break;
  }
};

// Handle row selection from GlAccountList
interface RowSelectEvent {
  data: GlAccount[];
}

const handleRowSelect = (event: RowSelectEvent) => {
  selectedAccounts.value = event.data;
};
</script>

<template>
  <div class="gl-accounts-page">
    <div class="surface-section px-4 py-6 md:px-6 lg:px-8">
      <div class="mb-4">
        <div class="flex justify-content-between align-items-center">
          <div>
            <div class="text-3xl text-900 font-bold mb-2">General Ledger Accounts</div>
            <div class="text-600 line-height-3">
              Manage your chart of accounts, view balances, and track financial transactions.
            </div>
          </div>
          <div>
            <Button 
              icon="pi pi-plus" 
              label="New Account" 
              class="p-button-sm"
              @click="router.push('/gl/accounts/new')"
            />
          </div>
        </div>
      </div>
      
      <!-- Bulk Actions Toolbar -->
      <div 
        v-if="selectedAccounts.length > 0" 
        class="mb-4 p-3 border-round border-1 border-200 bg-blue-50"
      >
        <div class="flex align-items-center justify-content-between">
          <div class="text-600">
            <i class="pi pi-check-square mr-2"></i>
            {{ selectedAccounts.length }} account{{ selectedAccounts.length !== 1 ? 's' : '' }} selected
          </div>
          <div class="flex gap-2">
            <Button 
              icon="pi pi-download" 
              label="Export Selected" 
              class="p-button-outlined p-button-sm"
              @click="handleBulkAction('export')"
            />
            <Button 
              icon="pi pi-ban" 
              label="Deactivate" 
              class="p-button-outlined p-button-sm p-button-warning"
              @click="handleBulkAction('deactivate')"
            />
            <Button 
              icon="pi pi-trash" 
              label="Delete" 
              class="p-button-outlined p-button-sm p-button-danger"
              @click="handleBulkAction('delete')"
            />
          </div>
        </div>
      </div>
      
      <!-- GL Account List Component -->
      <GlAccountList 
        @row-select="handleRowSelect"
        :selection="selectedAccounts"
        :filters="{}"
      />
      
      <!-- Quick Actions -->
      <div class="mt-6 pt-4 border-top-1 surface-border">
        <div class="flex flex-wrap gap-2">
          <Button 
            icon="pi pi-upload" 
            label="Import Accounts" 
            class="p-button-outlined p-button-sm"
            @click="showImportExportDialog = true"
          />
          <Button 
            icon="pi pi-download" 
            label="Export All" 
            class="p-button-outlined p-button-sm"
          />
          <Button 
            icon="pi pi-file-pdf" 
            label="Print Report" 
            class="p-button-outlined p-button-sm"
            @click="router.push('/gl/accounts/reports')"
          />
          <Button 
            icon="pi pi-chart-bar" 
            label="View Reports" 
            class="p-button-outlined p-button-sm"
          />
        </div>
      </div>
      
      <!-- Import/Export Dialog -->
      <GlImportExportDialog 
        v-model:visible="showImportExportDialog"
        @import-complete="handleImportComplete"
      />
    </div>
  </div>
</template>

<style scoped>
.gl-accounts-page {
  min-height: calc(100vh - 9rem);
}
</style>
