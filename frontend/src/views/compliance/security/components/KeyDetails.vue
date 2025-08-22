<template>
  <div class="key-details">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <h3 class="text-lg font-medium mb-4">Key Information</h3>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-600">Key ID:</span>
            <span class="font-mono">{{ keyData.id }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Algorithm:</span>
            <span>{{ keyData.algorithm }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Key Size:</span>
            <span>{{ keyData.keySize }} bits</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Key Type:</span>
            <span>{{ formatKeyType(keyData.type) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Created:</span>
            <span>{{ formatDateTime(keyData.createdAt) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Last Rotated:</span>
            <span>{{ formatDateTime(keyData.lastRotated) || 'Never' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Expires:</span>
            <span :class="{ 'text-red-500': isKeyExpiringSoon }">
              {{ formatDateTime(keyData.expiresAt) }}
              <i v-if="isKeyExpiringSoon" class="pi pi-exclamation-triangle ml-1 text-yellow-500"></i>
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Status:</span>
            <Tag :value="keyData.status" :severity="getStatusSeverity(keyData.status)" />
          </div>
        </div>
        
        <div class="mt-6">
          <h4 class="font-medium mb-2">Key Usage</h4>
          <div class="space-y-2">
            <div v-for="(usage, index) in keyData.usage" :key="index" class="flex items-center">
              <i class="pi pi-check-circle text-green-500 mr-2"></i>
              <span>{{ usage }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div>
        <h3 class="text-lg font-medium mb-4">Key Material</h3>
        <div class="bg-gray-50 p-4 rounded-md mb-4">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm font-medium">Public Key</span>
            <Button 
              icon="pi pi-copy" 
              class="p-button-text p-button-sm"
              @click="copyToClipboard(keyData.publicKey)"
              v-tooltip="'Copy to clipboard'"
            />
          </div>
          <pre class="text-xs p-2 bg-gray-100 rounded overflow-auto max-h-32">{{ keyData.publicKey }}</pre>
        </div>
        
        <div class="bg-gray-50 p-4 rounded-md">
          <div class="flex justify-between items-center mb-2">
            <span class="text-sm font-medium">Key Fingerprint</span>
            <Button 
              icon="pi pi-copy" 
              class="p-button-text p-button-sm"
              @click="copyToClipboard(keyData.fingerprint)"
              v-tooltip="'Copy to clipboard'"
            />
          </div>
          <pre class="text-xs p-2 bg-gray-100 rounded overflow-auto">{{ keyData.fingerprint }}</pre>
        </div>
        
        <div class="mt-6">
          <h4 class="font-medium mb-2">Metadata</h4>
          <div class="space-y-2">
            <div v-if="keyData.metadata" class="space-y-1">
              <div class="flex justify-between" v-if="keyData.metadata.createdBy">
                <span class="text-gray-600">Created By:</span>
                <span>{{ keyData.metadata.createdBy }}</span>
              </div>
              <div class="flex justify-between" v-if="keyData.metadata.environment">
                <span class="text-gray-600">Environment:</span>
                <span class="capitalize">{{ keyData.metadata.environment }}</span>
              </div>
              <div class="flex justify-between" v-if="keyData.metadata.region">
                <span class="text-gray-600">Region:</span>
                <span>{{ keyData.metadata.region }}</span>
              </div>
            </div>
            <div v-else class="text-gray-500 text-sm">
              No metadata available
            </div>
          </div>
        </div>
        
        <div class="mt-6 border-t pt-4 flex justify-between">
          <div>
            <div class="flex items-center" v-if="keyData.protected">
              <i class="pi pi-lock text-green-500 mr-2"></i>
              <span class="text-sm text-gray-600">This key is protected and cannot be deleted</span>
            </div>
            <div class="flex items-center" v-else>
              <i class="pi pi-unlock text-gray-400 mr-2"></i>
              <span class="text-sm text-gray-600">This key can be deleted</span>
            </div>
          </div>
          
          <div class="flex gap-2">
            <Button 
              label="Export Key" 
              icon="pi pi-download" 
              class="p-button-outlined p-button-sm"
              @click="$emit('export', keyData)"
            />
            <Button 
              label="Rotate Key" 
              icon="pi pi-sync" 
              class="p-button-outlined p-button-warning p-button-sm"
              @click="$emit('rotate', keyData)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useToast } from 'vue/usetoast';
import { format, isBefore, addDays, parseISO } from 'date-fns';

const props = defineProps({
  keyData: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close', 'export', 'rotate']);

// Initialize toast
const toast = useToast?.() || { add: console.log };

// Computed properties
const isKeyExpiringSoon = computed(() => {
  if (!props.keyData.expiresAt) return false;
  
  const expiryDate = new Date(props.keyData.expiresAt);
  const thirtyDaysFromNow = addDays(new Date(), 30);
  
  return isBefore(expiryDate, thirtyDaysFromNow) && props.keyData.status === 'ACTIVE';
});

// Methods
const formatDateTime = (dateString: string, formatStr = 'PPpp') => {
  if (!dateString) return 'N/A';
  return format(parseISO(dateString), formatStr);
};

const formatKeyType = (type: string) => {
  const types: { [key: string]: string } = {
    'SYMMETRIC': 'Symmetric',
    'ASYMMETRIC': 'Asymmetric (Public/Private Key Pair)',
    'HMAC': 'HMAC Key'
  };
  
  return types[type] || type;
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

const copyToClipboard = (text: string) => {
  if (!text) return;
  
  navigator.clipboard.writeText(text).then(() => {
    toast.add({
      severity: 'success',
      summary: 'Copied',
      detail: 'Text copied to clipboard',
      life: 2000
    });
  }).catch(err => {
    console.error('Failed to copy text:', err);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to copy text to clipboard',
      life: 3000
    });
  });
};
</script>

<style scoped>
.key-details {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 0.5rem;
}

/* Custom scrollbar */
.key-details::-webkit-scrollbar {
  width: 6px;
}

.key-details::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.key-details::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.key-details::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .key-details {
    max-height: none;
    overflow-y: visible;
  }
}
</style>
