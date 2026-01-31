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
        @submit="createKey"
      />
    </Dialog>

    <!-- Key Rotation Dialog -->
    <KeyRotationDialog 
      v-model="showKeyRotationDialog"
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

// --- INTERFACES ---

interface EncryptionKey {
  id: string;
  name: string;
  algorithm: string;
  keySize: number;
  type: string;
  publicKey?: string;
  fingerprint?: string;
  status: 'ACTIVE' | 'EXPIRED' | 'REVOKED' | 'PENDING_ROTATION';
  protected: boolean;
  usage: string[];
  createdAt: string;
  expiresAt: string;
  lastRotated?: string;
  expiredAt?: string;
  metadata?: {
    createdBy: string;
    environment: string;
    region: string;
  };
}

// This interface now matches the expected KeyFormModel
interface KeyFormData {
  name: string;
  description: string;
  algorithm: string | null;
  keySize: number | null;
  type: string | null;
  expiresAt: Date | string;
  protected: boolean;
  enabled: boolean;
}

interface RotationPayload {
  keyIds: string[];
  strategy: string;
  rotationDate: string;
  notes: string;
  dryRun: boolean;
}

interface RotationResultDetail {
  keyId: string;
  keyName: string;
  status: 'success' | 'warning' | 'error';
  message: string;
}

interface RotationResult {
  success: boolean;
  message: string;
  canProceed?: boolean;
  details: RotationResultDetail[];
}

interface RotationHistoryItem {
    id: string;
    date: string;
    type: string;
    status: 'Success' | 'Failed';
    details: string;
    initiatedBy: string;
}

// --- INITIALIZATION ---
const toast = useToast();

// --- STATE ---
const loading = ref(true);
const saving = ref(false);
const rotating = ref(false);
const savingSettings = ref(false);
const deleting = ref(false);
const submitted = ref(false);

// Dialog visibility
const showKeyDialog = ref(false);
const showKeyDetailsDialog = ref(false);
const showKeyRotationDialog = ref(false);
const showDeleteDialog = ref(false);

// Selections
const selectedKey = ref<EncryptionKey | null>(null);
const selectedKeyToDelete = ref<EncryptionKey | null>(null);
const selectedKeys = ref<EncryptionKey[]>([]); // For DataTable selection

// Form Data
const defaultNewKey = (): KeyFormData => ({
  name: '',
  description: '',
  algorithm: null,
  keySize: null,
  type: 'SYMMETRIC',
  expiresAt: addYears(new Date(), 1),
  protected: false,
  enabled: true,
});
const newKey = ref<KeyFormData>(defaultNewKey());

// Key Rotation Settings
const autoRotationEnabled = ref(false);
const rotationFrequency = ref('P90D');
const nextRotationDate = ref<Date>(addMonths(new Date(), 3));

// --- DATA ---
const allKeys = ref<EncryptionKey[]>([]);
const rotationHistory = ref<RotationHistoryItem[]>([]);

// --- STATIC OPTIONS ---
const algorithms = [
  { name: 'AES', value: 'AES' },
  { name: 'RSA', value: 'RSA' },
  { name: 'ECDSA', value: 'ECDSA' },
  { name: 'HMAC', value: 'HMAC' },
];

const rotationFrequencies = [
  { name: '30 Days', value: 'P30D' },
  { name: '90 Days', value: 'P90D' },
  { name: '180 Days', value: 'P180D' },
  { name: '1 Year', value: 'P1Y' },
];

// --- COMPUTED ---
const activeKeys = computed(() => allKeys.value.filter(k => k.status === 'ACTIVE' || k.status === 'PENDING_ROTATION'));
const expiredKeys = computed(() => allKeys.value.filter(k => k.status === 'EXPIRED'));

// --- METHODS ---

const formatDateTime = (dateString?: string) => {
  if (!dateString) return 'N/A';
  try {
    return format(parseISO(dateString), 'MMM d, yyyy, h:mm a');
  } catch (e) {
    console.error("Failed to format date:", dateString, e);
    return 'Invalid Date';
  }
};

const isKeyExpiringSoon = (key: EncryptionKey) => {
  if (!key.expiresAt) return false;
  const expiryDate = parseISO(key.expiresAt);
  const thirtyDaysFromNow = addDays(new Date(), 30);
  return isBefore(expiryDate, thirtyDaysFromNow) && key.status === 'ACTIVE';
};

const getStatusSeverity = (status: EncryptionKey['status']) => {
  switch (status) {
    case 'ACTIVE': return 'success';
    case 'EXPIRED': return 'danger';
    case 'REVOKED': return 'danger';
    case 'PENDING_ROTATION': return 'warning';
    default: return 'info';
  }
};

const loadKeys = async () => {
  loading.value = true;
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000));
  const now = new Date();
  allKeys.value = [
    { id: 'key-1', name: 'Primary DB Key', algorithm: 'AES', keySize: 256, type: 'SYMMETRIC', status: 'ACTIVE', protected: true, usage: ['Encryption'], createdAt: addDays(now, -100).toISOString(), expiresAt: addYears(now, 1).toISOString() },
    { id: 'key-2', name: 'API Signing Key', algorithm: 'RSA', keySize: 2048, type: 'ASYMMETRIC', status: 'ACTIVE', protected: false, usage: ['Signing'], createdAt: addDays(now, -50).toISOString(), expiresAt: addDays(now, 25).toISOString() },
    { id: 'key-3', name: 'Old Webhook Key', algorithm: 'HMAC', keySize: 256, type: 'SYMMETRIC', status: 'EXPIRED', protected: false, usage: ['Signing'], createdAt: addYears(now, -2).toISOString(), expiresAt: addYears(now, -1).toISOString(), expiredAt: addYears(now, -1).toISOString() },
    { id: 'key-4', name: 'Backup Key', algorithm: 'AES', keySize: 256, type: 'SYMMETRIC', status: 'ACTIVE', protected: false, usage: ['Encryption'], createdAt: addDays(now, -200).toISOString(), expiresAt: addMonths(now, 6).toISOString() },
  ];
  rotationHistory.value = [
      { id: 'rot-1', date: addDays(now, -90).toISOString(), type: 'Automatic', status: 'Success', details: 'Rotated 2 keys', initiatedBy: 'system' },
      { id: 'rot-2', date: addDays(now, -30).toISOString(), type: 'Manual', status: 'Success', details: 'Rotated API Signing Key', initiatedBy: 'admin@example.com' },
  ];
  loading.value = false;
};

const createKey = async () => {
  submitted.value = true;
  if (!newKey.value.name || !newKey.value.algorithm || !newKey.value.keySize || !newKey.value.type) {
    toast.add({ severity: 'warn', summary: 'Validation Error', detail: 'Please fill out all required fields.', life: 3000 });
    return;
  }
  
  saving.value = true;
  await new Promise(resolve => setTimeout(resolve, 500));
  
  const createdKey: EncryptionKey = {
    id: `key-${Math.random().toString(36).substring(2, 9)}`,
    name: newKey.value.name,
    algorithm: newKey.value.algorithm!,
    keySize: newKey.value.keySize!,
    type: newKey.value.type!,
    expiresAt: typeof newKey.value.expiresAt === 'string' ? newKey.value.expiresAt : newKey.value.expiresAt.toISOString(),
    status: 'ACTIVE',
    protected: newKey.value.protected,
    fingerprint: `SHA256:${Math.random().toString(36).substring(2, 15)}`,
    publicKey: newKey.value.type !== 'SYMMETRIC' ? '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAz8t8Jh...' : undefined,
    usage: [newKey.value.type === 'SYMMETRIC' ? 'Encryption' : 'Signing'],
    createdAt: new Date().toISOString(),
    lastRotated: new Date().toISOString(),
    metadata: { createdBy: 'admin', environment: 'production', region: 'us-east-1' }
  };

  allKeys.value.unshift(createdKey);
  toast.add({ severity: 'success', summary: 'Success', detail: 'Encryption key created successfully.', life: 3000 });
  
  closeKeyDialog();
  saving.value = false;
};

const deleteKey = async () => {
  if (!selectedKeyToDelete.value) return;
  deleting.value = true;
  await new Promise(resolve => setTimeout(resolve, 500));
  allKeys.value = allKeys.value.filter(key => key.id !== selectedKeyToDelete.value!.id);
  toast.add({ severity: 'success', summary: 'Success', detail: 'Encryption key deleted.', life: 3000 });
  deleting.value = false;
  showDeleteDialog.value = false;
  selectedKeyToDelete.value = null;
};

const rotateKeys = (payload: RotationPayload, callback: (results: RotationResult) => void) => {
  rotating.value = true;
  console.log('Starting rotation with payload:', payload);

  // Simulate API call
  setTimeout(() => {
    const results: RotationResult = {
      success: true,
      message: `${payload.dryRun ? 'Dry run' : 'Rotation'} completed.`,
      canProceed: payload.dryRun,
      details: payload.keyIds.map(id => {
        const key = allKeys.value.find(k => k.id === id);
        return {
          keyId: id,
          keyName: key?.name || 'Unknown Key',
          status: 'success',
          message: `Key ${payload.dryRun ? 'can be' : 'was'} rotated successfully.`
        };
      })
    };

    if (!payload.dryRun) {
      allKeys.value = allKeys.value.map(key => {
        if (payload.keyIds.includes(key.id)) {
          return { ...key, lastRotated: new Date().toISOString() };
        }
        return key;
      });
      rotationHistory.value.unshift({
          id: `rot-${rotationHistory.value.length + 1}`,
          date: new Date().toISOString(),
          type: 'Manual Rotation',
          status: 'Success',
          details: `Rotated ${payload.keyIds.length} key(s)`,
          initiatedBy: 'admin@example.com'
      });
    }

    callback(results);
    rotating.value = false;
  }, 1000);
};

const saveRotationSettings = async () => {
  savingSettings.value = true;
  await new Promise(resolve => setTimeout(resolve, 500));
  toast.add({ severity: 'success', summary: 'Success', detail: 'Rotation settings saved.', life: 3000 });
  savingSettings.value = false;
};

const viewKeyDetails = (key: EncryptionKey) => {
  selectedKey.value = key;
  showKeyDetailsDialog.value = true;
};

const confirmDeleteKey = (key: EncryptionKey) => {
  selectedKeyToDelete.value = key;
  showDeleteDialog.value = true;
};

const closeKeyDialog = () => {
  showKeyDialog.value = false;
  newKey.value = defaultNewKey();
  submitted.value = false;
};

const exportKey = (key: EncryptionKey) => {
  console.log('Exporting key:', key.id);
  toast.add({ severity: 'info', summary: 'Export Started', detail: `Preparing export for ${key.name}...`, life: 3000 });
};

const rotateSingleKey = (key: EncryptionKey) => {
  // This is a simplified approach. A better UX might be to open the
  // rotation dialog with this single key pre-selected.
  console.log(`Request to rotate single key: ${key.name}`);
  showKeyRotationDialog.value = true;
  // We can't pre-select in the dialog easily with current setup,
  // but opening the dialog is a good first step.
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
