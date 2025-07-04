<template>
  <div class="encryption-keys">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Encryption Keys</h1>
        <p class="text-gray-600">Manage encryption keys for data protection</p>
      </div>
      <div class="flex gap-3">
        <Button 
          icon="pi pi-sync" 
          label="Rotate Keys" 
          class="p-button-outlined p-button-sm"
          @click="showKeyRotationDialog = true"
          :disabled="loading"
        />
        <Button 
          icon="pi pi-plus" 
          label="Add Key" 
          class="p-button-primary p-button-sm"
          @click="showKeyDialog = true"
          :disabled="loading"
        />
      </div>
    </div>

    <!-- Tabs -->
    <TabView>
      <TabPanel header="Active Keys">
        <DataTable 
          :value="activeKeys" 
          :loading="loading"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[5, 10, 25, 50]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Showing {first} to {last} of {totalRecords} keys"
          responsiveLayout="scroll"
          v-model:selection="selectedKeys"
          dataKey="id"
        >
          <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
          <Column field="name" header="Name" :sortable="true">
            <template #body="{ data }">
              <span class="font-medium">{{ data.name }}</span>
            </template>
          </Column>
          <Column field="algorithm" header="Algorithm" :sortable="true" />
          <Column field="keySize" header="Key Size" :sortable="true">
            <template #body="{ data }">
              {{ data.keySize }} bits
            </template>
          </Column>
          <Column field="createdAt" header="Created" :sortable="true">
            <template #body="{ data }">
              {{ formatDateTime(data.createdAt) }}
            </template>
          </Column>
          <Column field="expiresAt" header="Expires" :sortable="true">
            <template #body="{ data }">
              <span :class="{ 'text-red-500': isKeyExpiringSoon(data) }">
                {{ formatDateTime(data.expiresAt) }}
                <i v-if="isKeyExpiringSoon(data)" class="pi pi-exclamation-triangle ml-1 text-yellow-500"></i>
              </span>
            </template>
          </Column>
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
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
                  :disabled="data.protected"
                  v-tooltip.top="data.protected ? 'Protected key cannot be deleted' : 'Delete Key'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </TabPanel>
      
      <TabPanel header="Expired Keys">
        <DataTable 
          :value="expiredKeys" 
          :loading="loading"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[5, 10, 25, 50]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Showing {first} to {last} of {totalRecords} keys"
          responsiveLayout="scroll"
        >
          <Column field="name" header="Name" :sortable="true" />
          <Column field="algorithm" header="Algorithm" :sortable="true" />
          <Column field="keySize" header="Key Size" :sortable="true">
            <template #body="{ data }">
              {{ data.keySize }} bits
            </template>
          </Column>
          <Column field="expiredAt" header="Expired On" :sortable="true">
            <template #body="{ data }">
              {{ formatDateTime(data.expiredAt) }}
            </template>
          </Column>
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" severity="danger" />
            </template>
          </Column>
        </DataTable>
      </TabPanel>
      
      <TabPanel header="Key Rotation">
        <div class="p-4 bg-gray-50 rounded-lg">
          <div class="mb-6">
            <h3 class="text-lg font-medium mb-2">Automatic Key Rotation</h3>
            <div class="flex items-center">
              <InputSwitch v-model="autoRotationEnabled" :disabled="loading" />
              <span class="ml-3">Enable automatic key rotation</span>
            </div>
            <p class="text-sm text-gray-500 mt-2">
              When enabled, encryption keys will be automatically rotated according to the schedule below.
            </p>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Rotation Frequency</label>
              <Dropdown 
                v-model="rotationFrequency" 
                :options="rotationFrequencies" 
                optionLabel="name" 
                optionValue="value"
                class="w-full"
                :disabled="!autoRotationEnabled || loading"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Next Rotation</label>
              <Calendar 
                v-model="nextRotationDate" 
                :minDate="new Date()"
                class="w-full"
                :disabled="!autoRotationEnabled || loading"
                dateFormat="yy-mm-dd"
                showIcon
              />
            </div>
            
            <div class="flex items-end">
              <Button 
                label="Save Settings" 
                class="p-button-primary"
                :loading="savingSettings"
                :disabled="!autoRotationEnabled || loading"
                @click="saveRotationSettings"
              />
            </div>
          </div>
          
          <Divider />
          
          <div>
            <h3 class="text-lg font-medium mb-4">Rotation History</h3>
            <DataTable :value="rotationHistory" :paginator="true" :rows="5" class="p-datatable-sm">
              <Column field="date" header="Date" :sortable="true">
                <template #body="{ data }">
                  {{ formatDateTime(data.date) }}
                </template>
              </Column>
              <Column field="type" header="Type" :sortable="true" />
              <Column field="status" header="Status" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="data.status === 'Success' ? 'success' : 'danger'" />
                </template>
              </Column>
              <Column field="details" header="Details" />
            </DataTable>
          </div>
        </div>
      </TabPanel>
    </TabView>

    <!-- Key Details Dialog -->
    <Dialog 
      v-model:visible="showKeyDetailsDialog" 
      :header="selectedKey ? selectedKey.name : 'Key Details'" 
      :modal="true"
      :style="{ width: '700px' }"
      :closable="true"
    >
      <KeyDetails 
        v-if="selectedKey" 
        :keyData="selectedKey" 
        @close="showKeyDetailsDialog = false"
        @export="exportKey"
        @rotate="rotateSingleKey"
      />
    </Dialog>

    <!-- New Key Dialog -->
    <Dialog 
      v-model:visible="showKeyDialog" 
      header="Create New Encryption Key" 
      :modal="true"
      :style="{ width: '500px' }"
      :closable="!saving"
    >
      <KeyForm 
        v-model="newKey"
        :submitted="submitted"
        :algorithms="algorithms"
        :keySizes="keySizes"
        :keyTypes="keyTypes"
        @submit="createKey"
        @cancel="closeKeyDialog"
      />
    </Dialog>

    <!-- Key Rotation Dialog -->
    <KeyRotationDialog 
      v-model:visible="showKeyRotationDialog"
      :activeKeys="activeKeys"
      :loading="rotating"
      @rotate="rotateKeys"
      @cancel="showKeyRotationDialog = false"
    />
    
    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="showDeleteDialog" 
      header="Confirm Deletion" 
      :modal="true" 
      :style="{ width: '450px' }"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to delete <b>{{ selectedKeyToDelete?.name }}</b>?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="showDeleteDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="deleteKey"
          :loading="deleting"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { format, addMonths, addYears, isBefore, addDays, parseISO } from 'date-fns';

// Components
import KeyDetails from './components/KeyDetails.vue';
import KeyForm from './components/KeyForm.vue';
import KeyRotationDialog from './components/KeyRotationDialog.vue';

// Initialize toast
const toast = useToast?.() || { add: console.log };

// State
const loading = ref(false);
const saving = ref(false);
const rotating = ref(false);
const savingSettings = ref(false);
const deleting = ref(false);
const submitted = ref(false);

// UI State
const showKeyDialog = ref(false);
const showKeyDetailsDialog = ref(false);
const showKeyRotationDialog = ref(false);
const showDeleteDialog = ref(false);
const selectedKey = ref<any>(null);
const selectedKeyToDelete = ref<any>(null);
const selectedKeys = ref([]);
const selectedKeysForRotation = ref<string[]>([]);
const rotateAllKeys = ref(false);

// Form Data
const newKey = ref({
  name: '',
  algorithm: '',
  keySize: 0,
  type: '',
  expiresAt: addYears(new Date(), 1),
  protected: false
});

// Key Rotation
const autoRotationEnabled = ref(false);
const rotationFrequency = ref('P30D');
const nextRotationDate = ref(addMonths(new Date(), 1));
const rotationStrategy = ref('IN_PLACE');
const rotationNotes = ref('');

// Options
const algorithms = [
  { name: 'AES', value: 'AES' },
  { name: 'RSA', value: 'RSA' },
  { name: 'ECDSA', value: 'ECDSA' },
  { name: 'HMAC', value: 'HMAC' },
  { name: 'PBKDF2', value: 'PBKDF2' },
];

const keySizes = [
  { name: '128 bits', value: 128 },
  { name: '192 bits', value: 192 },
  { name: '256 bits', value: 256 },
  { name: '384 bits', value: 384 },
  { name: '512 bits', value: 512 },
  { name: '1024 bits', value: 1024 },
  { name: '2048 bits', value: 2048 },
  { name: '4096 bits', value: 4096 },
];

const keyTypes = [
  { name: 'Symmetric', value: 'SYMMETRIC' },
  { name: 'Asymmetric (Public/Private Key Pair)', value: 'ASYMMETRIC' },
  { name: 'HMAC Key', value: 'HMAC' },
];

const rotationFrequencies = [
  { name: '30 days', value: 'P30D' },
  { name: '60 days', value: 'P60D' },
  { name: '90 days', value: 'P90D' },
  { name: '180 days', value: 'P180D' },
  { name: '1 year', value: 'P1Y' },
  { name: '2 years', value: 'P2Y' },
];

const rotationStrategies = [
  { name: 'In-place Rotation (Recommended)', value: 'IN_PLACE' },
  { name: 'Dual Key Transition', value: 'DUAL_KEY' },
  { name: 'Key Versioning', value: 'VERSIONING' },
];

// Mock data - in a real app, this would come from an API
const allKeys = ref([
  {
    id: 'key-001',
    name: 'Database Encryption Key',
    algorithm: 'AES',
    keySize: 256,
    type: 'SYMMETRIC',
    publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz8t8Jh...',
    fingerprint: 'SHA256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
    status: 'ACTIVE',
    protected: true,
    usage: ['Database Encryption', 'API Token Signing'],
    createdAt: '2025-01-15T08:30:00Z',
    expiresAt: '2026-01-15T08:30:00Z',
    lastRotated: '2025-01-15T08:30:00Z',
    metadata: {
      createdBy: 'system',
      environment: 'production',
      region: 'us-east-1'
    }
  },
  {
    id: 'key-002',
    name: 'JWT Signing Key',
    algorithm: 'RSA',
    keySize: 2048,
    type: 'ASYMMETRIC',
    publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz8t8Jh...',
    fingerprint: 'SHA256:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
    status: 'ACTIVE',
    protected: false,
    usage: ['JWT Signing', 'API Authentication'],
    createdAt: '2025-03-20T14:15:00Z',
    expiresAt: '2025-09-20T14:15:00Z',
    lastRotated: '2025-03-20T14:15:00Z',
    metadata: {
      createdBy: 'admin',
      environment: 'staging',
      region: 'us-west-2'
    }
  },
  {
    id: 'key-003',
    name: 'File Encryption Key',
    algorithm: 'AES',
    keySize: 256,
    type: 'SYMMETRIC',
    publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz8t8Jh...',
    fingerprint: 'SHA256:6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b',
    status: 'ACTIVE',
    protected: false,
    usage: ['File Encryption', 'Backup Encryption'],
    createdAt: '2025-05-10T09:45:00Z',
    expiresAt: '2025-08-10T09:45:00Z', // Expiring soon
    lastRotated: '2025-05-10T09:45:00Z',
    metadata: {
      createdBy: 'admin',
      environment: 'production',
      region: 'eu-central-1'
    }
  },
  // Expired keys
  {
    id: 'key-004',
    name: 'Legacy Encryption Key',
    algorithm: 'AES',
    keySize: 128,
    type: 'SYMMETRIC',
    publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz8t8Jh...',
    fingerprint: 'SHA256:d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35',
    status: 'EXPIRED',
    protected: false,
    usage: ['Legacy System'],
    createdAt: '2024-01-01T00:00:00Z',
    expiresAt: '2024-12-31T23:59:59Z',
    expiredAt: '2024-12-31T23:59:59Z',
    lastRotated: '2024-06-30T10:00:00Z',
    metadata: {
      createdBy: 'system',
      environment: 'production',
      region: 'us-east-1'
    }
  }
]);

const rotationHistory = ref([
  {
    id: 'rot-001',
    date: '2025-06-15T03:00:00Z',
    type: 'Scheduled Rotation',
    status: 'Success',
    details: 'Rotated 2 encryption keys',
    initiatedBy: 'system'
  },
  {
    id: 'rot-002',
    date: '2025-05-15T03:00:00Z',
    type: 'Scheduled Rotation',
    status: 'Success',
    details: 'Rotated 1 encryption key',
    initiatedBy: 'system'
  },
  {
    id: 'rot-003',
    date: '2025-04-15T03:00:00Z',
    type: 'Scheduled Rotation',
    status: 'Success',
    details: 'Rotated 2 encryption keys',
    initiatedBy: 'system'
  },
  {
    id: 'rot-004',
    date: '2025-03-20T14:30:00Z',
    type: 'Manual Rotation',
    status: 'Success',
    details: 'Rotated JWT Signing Key (manual)',
    initiatedBy: 'admin@example.com'
  }
]);

// Computed properties
const activeKeys = computed(() => {
  return allKeys.value.filter(key => key.status === 'ACTIVE');
});

const expiredKeys = computed(() => {
  return allKeys.value.filter(key => key.status === 'EXPIRED');
});

// Methods
const loadKeys = async () => {
  loading.value = true;
  try {
    // In a real app, this would be an API call
    // const response = await api.get('/api/security/keys');
    // allKeys.value = response.data;
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
  } catch (error) {
    console.error('Error loading encryption keys:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load encryption keys',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};

const createKey = async () => {
  submitted.value = true;
  
  // Validate form
  if (!newKey.value.name || !newKey.value.algorithm || !newKey.value.keySize || !newKey.value.type || !newKey.value.expiresAt) {
    return;
  }
  
  saving.value = true;
  
  try {
    // In a real app, this would be an API call
    // const response = await api.post('/api/security/keys', newKey.value);
    
    // Add the new key to the list (simulated)
    const newKeyData = {
      id: `key-${String(allKeys.value.length + 1).padStart(3, '0')}`,
      ...newKey.value,
      status: 'ACTIVE',
      fingerprint: `SHA256:${Math.random().toString(36).substring(2, 15)}`,
      publicKey: '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz8t8Jh...',
      usage: [newKey.value.type === 'SYMMETRIC' ? 'Encryption' : 'Signing'],
      createdAt: new Date().toISOString(),
      lastRotated: new Date().toISOString(),
      metadata: {
        createdBy: 'admin',
        environment: 'production',
        region: 'us-east-1'
      }
    };
    
    allKeys.value.unshift(newKeyData);
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Encryption key created successfully',
      life: 3000
    });
    
    closeKeyDialog();
    
  } catch (error) {
    console.error('Error creating encryption key:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to create encryption key',
      life: 3000
    });
  } finally {
    saving.value = false;
  }
};

const deleteKey = async () => {
  if (!selectedKeyToDelete.value) return;
  
  deleting.value = true;
  
  try {
    // In a real app, this would be an API call
    // await api.delete(`/api/security/keys/${selectedKeyToDelete.value.id}`);
    
    // Remove the key from the list (simulated)
    allKeys.value = allKeys.value.filter(key => key.id !== selectedKeyToDelete.value.id);
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Encryption key deleted successfully',
      life: 3000
    });
    
  } catch (error) {
    console.error('Error deleting encryption key:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete encryption key',
      life: 3000
    });
  } finally {
    deleting.value = false;
    showDeleteDialog.value = false;
    selectedKeyToDelete.value = null;
  }
};

const rotateKeys = async (keyIds: string[]) => {
  if (!keyIds || keyIds.length === 0) return;
  
  rotating.value = true;
  
  try {
    // In a real app, this would be an API call
    // await api.post('/api/security/keys/rotate', { keyIds });
    
    // Update the keys (simulated)
    const now = new Date().toISOString();
    
    allKeys.value = allKeys.value.map(key => {
      if (keyIds.includes(key.id)) {
        return {
          ...key,
          lastRotated: now,
          expiresAt: addYears(new Date(), 1).toISOString()
        };
      }
      return key;
    });
    
    // Add to rotation history
    rotationHistory.value.unshift({
      id: `rot-${String(rotationHistory.value.length + 1).padStart(3, '0')}`,
      date: now,
      type: 'Manual Rotation',
      status: 'Success',
      details: `Rotated ${keyIds.length} encryption key${keyIds.length > 1 ? 's' : ''}`,
      initiatedBy: 'admin@example.com'
    });
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `Successfully rotated ${keyIds.length} key${keyIds.length > 1 ? 's' : ''}`,
      life: 3000
    });
    
  } catch (error) {
    console.error('Error rotating encryption keys:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to rotate encryption keys',
      life: 3000
    });
  } finally {
    rotating.value = false;
    showKeyRotationDialog.value = false;
    selectedKeysForRotation.value = [];
    rotateAllKeys.value = false;
  }
};

const rotateSingleKey = (key: any) => {
  selectedKeysForRotation.value = [key.id];
  rotateKeys([key.id]);
};

const saveRotationSettings = async () => {
  savingSettings.value = true;
  
  try {
    // In a real app, this would be an API call
    // await api.put('/api/security/keys/rotation-settings', {
    //   enabled: autoRotationEnabled.value,
    //   frequency: rotationFrequency.value,
    //   nextRotation: nextRotationDate.value
    // });
    
    await new Promise(resolve => setTimeout(resolve, 500));
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Rotation settings saved successfully',
      life: 3000
    });
    
  } catch (error) {
    console.error('Error saving rotation settings:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save rotation settings',
      life: 3000
    });
  } finally {
    savingSettings.value = false;
  }
};

const viewKeyDetails = (key: any) => {
  selectedKey.value = key;
  showKeyDetailsDialog.value = true;
};

const confirmDeleteKey = (key: any) => {
  selectedKeyToDelete.value = key;
  showDeleteDialog.value = true;
};

const closeKeyDialog = () => {
  showKeyDialog.value = false;
  newKey.value = {
    name: '',
    algorithm: '',
    keySize: 0,
    type: '',
    expiresAt: addYears(new Date(), 1),
    protected: false
  };
  submitted.value = false;
};

const exportKey = (key: any) => {
  // In a real app, this would trigger a file download
  console.log('Exporting key:', key.id);
  
  toast.add({
    severity: 'info',
    summary: 'Export Started',
    detail: `Preparing export for ${key.name}...`,
    life: 3000
  });
};

const toggleSelectAllKeys = () => {
  if (rotateAllKeys.value) {
    selectedKeysForRotation.value = activeKeys.value
      .filter(key => !key.protected)
      .map(key => key.id);
  } else {
    selectedKeysForRotation.value = [];
  }
};

const isKeyExpiringSoon = (key: any) => {
  if (!key.expiresAt) return false;
  
  const expiryDate = new Date(key.expiresAt);
  const thirtyDaysFromNow = addDays(new Date(), 30);
  
  return isBefore(expiryDate, thirtyDaysFromNow) && key.status === 'ACTIVE';
};

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'ACTIVE':
      return 'success';
    case 'EXPIRED':
      return 'danger';
    case 'PENDING_ROTATION':
      return 'warning';
    default:
      return 'info';
  }
};

const formatDateTime = (dateString: string, formatStr = 'PPpp') => {
  if (!dateString) return 'N/A';
  return format(parseISO(dateString), formatStr);
};

// Lifecycle hooks
onMounted(() => {
  loadKeys();
});
</script>

<style scoped>
.encryption-keys {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.p-tabview-panels) {
  padding: 0;
  margin-top: 1rem;
}

:deep(.p-datatable) {
  border-radius: 6px;
  overflow: hidden;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f9fafb;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  color: #4b5563;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.75rem 1rem;
}

:deep(.p-tag) {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  font-weight: 500;
}

.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem 0;
}

:deep(.p-inputswitch) {
  margin-right: 0.5rem;
}

:deep(.p-datatable .p-paginator-bottom) {
  border-top: 0 none;
  border-radius: 0 0 6px 6px;
}
</style>
