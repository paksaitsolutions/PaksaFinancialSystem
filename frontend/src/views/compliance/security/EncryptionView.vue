<script setup lang="ts">
import { useEncryptionManagement } from './EncryptionView.script';

const {
  // State
  loading,
  saving,
  rotating,
  togglingStatus,
  
  // UI State
  showKeyDialog,
  showKeyDetails,
  showDeleteDialog,
  showImportDialog,
  
  // Form Data
  newKey,
  importKey,
  selectedKey,
  
  // Data
  encryptionKeys,
  encryptionLogs,
  settings,
  
  // Constants
  keyAlgorithms,
  keySizes,
  encryptionLevels,
  
  // Methods
  generateKey,
  importKeyAction,
  viewKeyDetails,
  rotateKey,
  toggleKeyStatus,
  confirmDeleteKey,
  deleteKey,
  saveSettings,
  copyToClipboard,
  cancelNewKey,
  cancelImport,
  formatDateTime,
  getKeyStatusSeverity,
  getLogStatusSeverity
} = useEncryptionManagement();
</script>

<template>
  <div class="encryption-management">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Data Encryption Management</h1>
        <p class="text-gray-600">Manage encryption keys and data protection settings</p>
      </div>
      <div class="flex gap-3">
        <Button
          icon="pi pi-key" 
          label="Generate Key" 
          class="p-button-primary p-button-sm"
          @click="showKeyDialog = true"
        />
        <Button 
          icon="pi pi-upload" 
          label="Import Key" 
          class="p-button-outlined p-button-sm"
          @click="showImportDialog = true"
        />
      </div>
    </div>

    <!-- Tabs -->
    <TabView>
      <TabPanel header="Encryption Keys">
        <DataTable 
          :value="encryptionKeys" 
          :loading="loading"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[5, 10, 25]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Showing {first} to {last} of {totalRecords} keys"
          responsiveLayout="scroll"
        >
          <Column field="id" header="ID" :sortable="true" />
          <Column field="name" header="Key Name" :sortable="true">
            <template #body="{ data }">
              <div class="flex items-center">
                <i class="pi pi-key mr-2"></i>
                <span>{{ data.name }}</span>
              </div>
            </template>
          </Column>
          <Column field="algorithm" header="Algorithm" :sortable="true" />
          <Column field="createdAt" header="Created" :sortable="true">
            <template #body="{ data }">
              {{ formatDateTime(data.createdAt) }}
            </template>
          </Column>
          <Column field="expiresAt" header="Expires" :sortable="true">
            <template #body="{ data }">
              {{ data.expiresAt ? formatDateTime(data.expiresAt) : 'Never' }}
            </template>
          </Column>
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getKeyStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions" style="width: 15%; min-width: 10rem">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-text p-button-rounded p-button-sm"
                  @click="viewKeyDetails(data)"
                  v-tooltip.top="'View Details'"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-rounded p-button-sm p-button-danger"
                  @click="confirmDeleteKey(data)"
                  :disabled="data.status === 'active'"
                  v-tooltip.top="data.status === 'active' ? 'Cannot delete active key' : 'Delete Key'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </TabPanel>
      
      <TabPanel header="Encryption Logs">
        <DataTable 
          :value="encryptionLogs" 
          :loading="loading"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[5, 10, 25]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Showing {first} to {last} of {totalRecords} logs"
          responsiveLayout="scroll"
        >
          <Column field="timestamp" header="Timestamp" :sortable="true">
            <template #body="{ data }">
              {{ formatDateTime(data.timestamp) }}
            </template>
          </Column>
          <Column field="action" header="Action" :sortable="true" />
          <Column field="keyName" header="Key" :sortable="true" />
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getLogStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column field="initiatedBy" header="User" :sortable="true" />
        </DataTable>
      </TabPanel>
      
      <TabPanel header="Settings">
        <Card>
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-cog mr-2"></i>
              <span>Encryption Settings</span>
            </div>
          </template>
          <template #content>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 class="text-lg font-medium mb-4">Key Rotation</h3>
                <div class="field">
                  <label for="rotationInterval" class="block text-sm font-medium text-gray-700 mb-1">Rotation Interval (days)</label>
                  <InputNumber 
                    id="rotationInterval" 
                    v-model="settings.keyRotationInterval" 
                    :min="30" 
                    :max="365" 
                    showButtons
                    buttonLayout="horizontal"
                    incrementButtonIcon="pi pi-plus"
                    decrementButtonIcon="pi pi-minus"
                    class="w-full"
                  />
                </div>
                <div class="field">
                  <label for="autoRotate" class="flex items-center">
                    <Checkbox id="autoRotate" v-model="settings.autoRotate" :binary="true" />
                    <span class="ml-2">Enable automatic key rotation</span>
                  </label>
                </div>
              </div>
              
              <div>
                <h3 class="text-lg font-medium mb-4">Encryption Policy</h3>
                <div class="field">
                  <label for="encryptionLevel" class="block text-sm font-medium text-gray-700 mb-1">Encryption Level</label>
                  <Dropdown 
                    id="encryptionLevel" 
                    v-model="settings.encryptionLevel" 
                    :options="encryptionLevels" 
                    optionLabel="name" 
                    optionValue="value"
                    class="w-full"
                  />
                </div>
                <div class="field">
                  <label for="requireMfa" class="flex items-center">
                    <Checkbox id="requireMfa" v-model="settings.requireMfa" :binary="true" />
                    <span class="ml-2">Require MFA for key operations</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div class="flex justify-end mt-6">
              <Button 
                label="Save Settings" 
                icon="pi pi-save" 
                class="p-button-primary"
                @click="saveSettings"
                :loading="saving"
              />
            </div>
          </template>
        </Card>
      </TabPanel>
    </TabView>

    <!-- Dialogs -->
    <Dialog 
      v-model:visible="showKeyDialog" 
      header="Generate New Encryption Key" 
      :modal="true"
      :style="{ width: '500px' }"
      :closable="false"
    >
      <div class="grid grid-cols-1 gap-4">
        <div class="field">
          <label for="keyName" class="block text-sm font-medium text-gray-700 mb-1">Key Name</label>
          <InputText id="keyName" v-model="newKey.name" class="w-full" />
        </div>
        <div class="field">
          <label for="keyAlgorithm" class="block text-sm font-medium text-gray-700 mb-1">Algorithm</label>
          <Dropdown 
            id="keyAlgorithm" 
            v-model="newKey.algorithm" 
            :options="keyAlgorithms" 
            optionLabel="name" 
            optionValue="value"
            class="w-full"
          />
        </div>
        <div class="field">
          <label for="keySize" class="block text-sm font-medium text-gray-700 mb-1">Key Size (bits)</label>
          <Dropdown 
            id="keySize" 
            v-model="newKey.keySize" 
            :options="keySizes" 
            optionLabel="name" 
            optionValue="value"
            class="w-full"
          />
        </div>
        <div class="field">
          <label for="expiryDate" class="block text-sm font-medium text-gray-700 mb-1">Expiry Date (Optional)</label>
          <Calendar 
            id="expiryDate" 
            v-model="newKey.expiryDate" 
            :showIcon="true" 
            :showButtonBar="true"
            dateFormat="yy-mm-dd"
            class="w-full"
          />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="cancelNewKey" />
        <Button label="Generate Key" icon="pi pi-check" class="p-button-primary" @click="generateKey" />
      </template>
    </Dialog>

    <!-- Key Details Dialog -->
    <Dialog 
      v-model:visible="showKeyDetails" 
      :header="selectedKey ? `Key Details: ${selectedKey.name}` : 'Key Details'" 
      :modal="true"
      :style="{ width: '600px' }"
    >
      <div v-if="selectedKey" class="key-details">
        <div class="grid grid-cols-2 gap-4 mb-6">
          <div>
            <div class="text-sm text-gray-500">Key ID</div>
            <div class="font-medium">{{ selectedKey.id }}</div>
          </div>
          <div>
            <div class="text-sm text-gray-500">Status</div>
            <Tag :value="selectedKey.status" :severity="getKeyStatusSeverity(selectedKey.status)" />
          </div>
          <div>
            <div class="text-sm text-gray-500">Algorithm</div>
            <div>{{ selectedKey.algorithm }}</div>
          </div>
          <div>
            <div class="text-sm text-gray-500">Key Size</div>
            <div>{{ selectedKey.keySize }} bits</div>
          </div>
          <div>
            <div class="text-sm text-gray-500">Created</div>
            <div>{{ formatDateTime(selectedKey.createdAt) }}</div>
          </div>
          <div>
            <div class="text-sm text-gray-500">Expires</div>
            <div>{{ selectedKey.expiresAt ? formatDateTime(selectedKey.expiresAt) : 'Never' }}</div>
          </div>
        </div>
        
        <div class="mb-6">
          <div class="flex justify-between items-center mb-2">
            <h4 class="font-medium">Key Material</h4>
            <Button 
              icon="pi pi-copy" 
              class="p-button-text p-button-sm"
              @click="copyToClipboard(selectedKey.keyMaterial || '')"
              v-tooltip.top="'Copy to Clipboard'"
            />
          </div>
          <div class="bg-gray-100 p-3 rounded-md font-mono text-sm overflow-auto max-h-40">
            {{ selectedKey.keyMaterial }}
          </div>
          <small class="text-gray-500">This is a one-time view. Please save this key in a secure location.</small>
        </div>
        
        <div class="flex justify-between items-center">
          <div>
            <Button 
              label="Rotate Key" 
              icon="pi pi-sync" 
              class="p-button-warning p-button-sm"
              @click="rotateKey"
              :loading="rotating"
            />
          </div>
          <div>
            <Button 
              :label="selectedKey.status === 'active' ? 'Deactivate' : 'Activate'" 
              :icon="selectedKey.status === 'active' ? 'pi pi-ban' : 'pi pi-check'" 
              :class="selectedKey.status === 'active' ? 'p-button-danger' : 'p-button-success'"
              class="p-button-sm"
              @click="toggleKeyStatus"
              :loading="togglingStatus"
            />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Close" icon="pi pi-times" class="p-button-text" @click="showKeyDetails = false" />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="showDeleteDialog" 
      header="Confirm Deletion" 
      :modal="true"
      :style="{ width: '450px' }"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="selectedKey">
          Are you sure you want to delete the key <b>{{ selectedKey.name }}</b>? This action cannot be undone.
        </span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" class="p-button-text" @click="showDeleteDialog = false" />
        <Button label="Yes" icon="pi pi-check" class="p-button-danger" @click="deleteKey" />
      </template>
    </Dialog>
    
    <!-- Import Key Dialog -->
    <Dialog 
      v-model:visible="showImportDialog" 
      header="Import Encryption Key" 
      :modal="true"
      :style="{ width: '500px' }"
      :closable="false"
    >
      <div class="grid grid-cols-1 gap-4">
        <div class="field">
          <label for="importKeyName" class="block text-sm font-medium text-gray-700 mb-1">Key Name</label>
          <InputText id="importKeyName" v-model="importKey.name" class="w-full" />
        </div>
        <div class="field">
          <label for="importKeyMaterial" class="block text-sm font-medium text-gray-700 mb-1">Key Material</label>
          <Textarea id="importKeyMaterial" v-model="importKey.keyMaterial" rows="5" class="w-full font-mono" />
        </div>
        <div class="field">
          <label for="importKeyPassword" class="block text-sm font-medium text-gray-700 mb-1">Password (Optional)</label>
          <Password 
            id="importKeyPassword" 
            v-model="importKey.password" 
            :feedback="false" 
            toggleMask 
            class="w-full"
            inputClass="w-full"
          />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="cancelImport" />
        <Button label="Import Key" icon="pi pi-upload" class="p-button-primary" @click="importKeyAction" />
      </template>
    </Dialog>
    
    <Toast />
    <ConfirmDialog />
  </div>
</template>

<style scoped>
.encryption-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.key-details {
  max-height: 70vh;
  overflow-y: auto;
}

.confirmation-content {
  display: flex;
  align-items: center;
  padding: 1rem;
}
</style>
