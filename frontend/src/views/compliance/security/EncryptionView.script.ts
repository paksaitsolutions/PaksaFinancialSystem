import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { format } from 'date-fns';
import { encryptionService, type EncryptionKey, type EncryptionLog, type Settings } from '@/services/encryptionService';

// Types are now imported from encryptionService

export function useEncryptionManagement() {
  // State
  const toast = useToast();
  const confirm = useConfirm();

  // UI State
  const loading = ref(false);
  const saving = ref(false);
  const rotating = ref(false);
  const togglingStatus = ref(false);
  const showKeyDialog = ref(false);
  const showImportDialog = ref(false);
  const showKeyDetailsDialog = ref(false);
  const showDeleteDialog = ref(false);
  const selectedKey = ref<EncryptionKey | null>(null);
  const selectedKeys = ref<EncryptionKey[]>([]);

  // Form Data
  const newKey = ref({
    name: '',
    algorithm: 'AES-256',
    keySize: 256,
    expiryDate: null as Date | null
  });

  const importKey = ref({
    name: '',
    keyMaterial: '',
    password: ''
  });

  // Mock data - Replace with API calls
  const encryptionKeys = ref<EncryptionKey[]>([]);
  const encryptionLogs = ref<EncryptionLog[]>([]);
  const settings = ref<Settings>({
    keyRotationInterval: 90,
    autoRotate: true,
    encryptionLevel: 'high',
    requireMfa: true
  });

  // Constants
  const keyAlgorithms = [
    { name: 'AES-256', value: 'AES-256' },
    { name: 'RSA-4096', value: 'RSA-4096' },
    { name: 'ECC-384', value: 'ECC-384' }
  ] as const;

  const keySizes = [
    { name: '128 bits', value: 128 },
    { name: '192 bits', value: 192 },
    { name: '256 bits', value: 256 },
    { name: '384 bits', value: 384 },
    { name: '512 bits', value: 512 },
    { name: '1024 bits', value: 1024 },
    { name: '2048 bits', value: 2048 },
    { name: '4096 bits', value: 4096 }
  ] as const;

  const encryptionLevels = [
    { name: 'Standard (AES-256)', value: 'standard' },
    { name: 'High (RSA-4096)', value: 'high' },
    { name: 'FIPS 140-2 Compliant', value: 'fips' }
  ] as const;

  // Methods
  const loadData = async () => {
    loading.value = true;
    try {
      // Load encryption keys
      const [keys, logs, settingsData] = await Promise.all([
        encryptionService.getKeys(),
        encryptionService.getLogs(),
        encryptionService.getSettings()
      ]);
      
      encryptionKeys.value = keys;
      encryptionLogs.value = logs;
      settings.value = settingsData;
    } catch (error) {
      console.error('Error loading encryption data:', error);
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load encryption data',
        life: 5000
      });
    } finally {
      loading.value = false;
    }
  };

  const generateKey = async () => {
    if (!newKey.value.name.trim()) {
      toast.add({
        severity: 'warn',
        summary: 'Validation Error',
        detail: 'Please enter a key name',
        life: 3000
      });
      return;
    }

    saving.value = true;
    try {
      const keyData = {
        name: newKey.value.name.trim(),
        algorithm: newKey.value.algorithm,
        keySize: newKey.value.keySize,
        expiresAt: newKey.value.expiryDate?.toISOString()
      };

      const generatedKey = await encryptionService.generateKey(keyData);
      
      // Update the keys list
      encryptionKeys.value.unshift(generatedKey);
      
      // Refresh logs to get the latest activity
      const logs = await encryptionService.getLogs();
      encryptionLogs.value = logs;

      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Encryption key generated successfully',
        life: 3000
      });

      resetNewKeyForm();
      showKeyDialog.value = false;
    } catch (error: unknown) {
      console.error('Error generating key:', error);
      const errorMessage = (error as any)?.response?.data?.message || 'Failed to generate encryption key';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: errorMessage,
        life: 5000
      });
    } finally {
      saving.value = false;
    }
  };

  const importKeyAction = async () => {
    if (!importKey.value.name.trim() || !importKey.value.keyMaterial.trim()) {
      toast.add({
        severity: 'warn',
        summary: 'Validation Error',
        detail: 'Please provide both key name and key material',
        life: 3000
      });
      return;
    }

    saving.value = true;
    try {
      const importData = {
        name: importKey.value.name.trim(),
        keyMaterial: importKey.value.keyMaterial.trim(),
        password: importKey.value.password || undefined
      };

      const importedKey = await encryptionService.importKey(importData);
      
      // Update the keys list
      encryptionKeys.value.unshift(importedKey);
      
      // Refresh logs to get the latest activity
      const logs = await encryptionService.getLogs();
      encryptionLogs.value = logs;

      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Encryption key imported successfully',
        life: 3000
      });

      resetImportForm();
      showImportDialog.value = false;
    } catch (error: unknown) {
      console.error('Error importing key:', error);
      const errorMessage = (error as any)?.response?.data?.message || 'Failed to import encryption key';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: errorMessage,
        life: 5000
      });
    } finally {
      saving.value = false;
    }
  };

  const viewKeyDetails = (key: EncryptionKey) => {
    if (!key) return;
    selectedKey.value = { ...key };
    showKeyDetailsDialog.value = true;
  };

  const rotateKey = async () => {
    const currentKey = selectedKey.value;
    if (!currentKey) {
      toast.add({
        severity: 'warn',
        summary: 'No Key Selected',
        detail: 'Please select a key to rotate',
        life: 3000
      });
      return;
    }
    
    const keyCopy = { ...currentKey }; // Create a copy of the current key
    
    confirm.require({
      message: `Are you sure you want to rotate the key "${keyCopy.name}"?`,
      header: 'Confirm Key Rotation',
      icon: 'pi pi-exclamation-triangle',
      accept: async () => {
        rotating.value = true;
        try {
          // Call the API to rotate the key
          const rotatedKey = await encryptionService.rotateKey(keyCopy.id);
          
          // Update the key in the list
          const keyIndex = encryptionKeys.value.findIndex(k => k.id === rotatedKey.id);
          if (keyIndex !== -1) {
            // Replace the old key with the rotated one
            encryptionKeys.value.splice(keyIndex, 1, rotatedKey);
            encryptionKeys.value = [...encryptionKeys.value]; // Trigger reactivity
          }
          
          // Update the selected key if it's the one being rotated
          if (selectedKey.value?.id === rotatedKey.id) {
            selectedKey.value = { ...rotatedKey };
          }
          
          // Refresh logs to get the latest activity
          const logs = await encryptionService.getLogs();
          encryptionLogs.value = logs;

          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Encryption key rotated successfully',
            life: 3000
          });
          
          showKeyDetailsDialog.value = false;
        } catch (error) {
          console.error('Error rotating key:', error);
          toast.add({
            severity: 'error',
            summary: 'Error',
            detail: 'Failed to rotate encryption key',
            life: 5000
          });
        } finally {
          rotating.value = false;
        }
      }
    });
  };

  const toggleKeyStatus = async () => {
    const currentKey = selectedKey.value;
    if (!currentKey) {
      toast.add({
        severity: 'warn',
        summary: 'No Key Selected',
        detail: 'Please select a key to toggle status',
        life: 3000
      });
      return;
    }
    
    const keyCopy = { ...currentKey }; // Create a copy of the current key
    const newStatus = keyCopy.status === 'active' ? 'inactive' : 'active';
    const action = newStatus === 'active' ? 'activate' : 'deactivate';
    
    togglingStatus.value = true;
    try {
      // Call the API to update the key status
      const updatedKey = await encryptionService.updateKeyStatus(keyCopy.id, newStatus);
      
      // Update key status in the list
      const keyIndex = encryptionKeys.value.findIndex(k => k.id === updatedKey.id);
      if (keyIndex !== -1) {
        encryptionKeys.value[keyIndex] = { ...encryptionKeys.value[keyIndex], ...updatedKey };
        encryptionKeys.value = [...encryptionKeys.value]; // Trigger reactivity
      }
      
      // Update selected key if it's the one being toggled
      if (selectedKey.value?.id === updatedKey.id) {
        selectedKey.value = { ...selectedKey.value, ...updatedKey };
      }
      
      // Refresh logs to get the latest activity
      const logs = await encryptionService.getLogs();
      encryptionLogs.value = logs;
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: `Key ${action}d successfully`,
        life: 3000
      });
    } catch (error) {
      console.error(`Error ${action}ing key:`, error);
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: `Failed to ${action} encryption key`,
        life: 5000
      });
    } finally {
      togglingStatus.value = false;
    }
  };

  const confirmDeleteKey = (key: EncryptionKey) => {
    if (!key) return;
    selectedKey.value = { ...key };
    showDeleteDialog.value = true;
  };

  const deleteKey = async () => {
    if (!selectedKey.value) {
      toast.add({
        severity: 'warn',
        summary: 'No Key Selected',
        detail: 'Please select a key to delete',
        life: 3000
      });
      return;
    }
    
    const keyToDelete = selectedKey.value; // Store the reference
    
    try {
      // Call the API to delete the key
      await encryptionService.deleteKey(keyToDelete.id);
      
      // Remove from the list
      const keyIndex = encryptionKeys.value.findIndex(k => k.id === keyToDelete.id);
      if (keyIndex !== -1) {
        encryptionKeys.value.splice(keyIndex, 1);
        encryptionKeys.value = [...encryptionKeys.value]; // Trigger reactivity
      }
      
      // Refresh logs to get the latest activity
      const logs = await encryptionService.getLogs();
      encryptionLogs.value = logs;
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Encryption key deleted successfully',
        life: 3000
      });
      
      showDeleteDialog.value = false;
      showKeyDetailsDialog.value = false;
    } catch (error) {
      console.error('Error deleting key:', error);
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to delete encryption key',
        life: 5000
      });
    }
  };

  const saveSettings = async () => {
    saving.value = true;
    try {
      // Call the API to update settings
      const updatedSettings = await encryptionService.updateSettings(settings.value);
      
      // Update local settings with the response
      settings.value = { ...settings.value, ...updatedSettings };
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Encryption settings saved successfully',
        life: 3000
      });
    } catch (error: unknown) {
      console.error('Error saving settings:', error);
      const errorMessage = (error as any)?.response?.data?.message || 'Failed to save encryption settings';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: errorMessage,
        life: 5000
      });
    } finally {
      saving.value = false;
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text).then(() => {
      toast.add({
        severity: 'info',
        summary: 'Copied',
        detail: 'Key material copied to clipboard',
        life: 2000
      });
    }).catch(err => {
      console.error('Failed to copy text:', err);
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to copy to clipboard',
        life: 3000
      });
    });
  };

  const resetNewKeyForm = () => {
    newKey.value = {
      name: '',
      algorithm: 'AES-256',
      keySize: 256,
      expiryDate: null
    };
  };

  const resetImportForm = () => {
    importKey.value = {
      name: '',
      keyMaterial: '',
      password: ''
    };
  };

  const cancelNewKey = () => {
    resetNewKeyForm();
    showKeyDialog.value = false;
  };

  const cancelImport = () => {
    resetImportForm();
    showImportDialog.value = false;
  };

  const formatDateTime = (date: string | Date | null | undefined): string => {
    if (!date) return 'N/A';
    try {
      return format(new Date(date), 'yyyy-MM-dd HH:mm:ss');
    } catch (error) {
      console.error('Error formatting date:', error);
      return 'Invalid Date';
    }
  };

  const getKeyStatusSeverity = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'warning';
      case 'expired': 
      case 'compromised': 
        return 'danger';
      default: return 'info';
    }
  };

  // Helper functions
  const getLogStatusSeverity = (status: string): string => {
    switch (status) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'failed': return 'danger';
      default: return 'info';
    }
  };

  const getKeyStatusLabel = (status: string): string => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  const formatDate = (date: string | Date | null): string => {
    if (!date) return 'Never';
    try {
      const dateObj = typeof date === 'string' ? new Date(date) : date;
      return format(dateObj, 'yyyy-MM-dd HH:mm:ss');
    } catch (e) {
      console.error('Error formatting date:', e);
      return 'Invalid date';
    }
  };

  // Lifecycle hooks
  onMounted(() => {
    loadData();
  });

  // Return all the necessary values and methods
  return {
    // State
    loading,
    saving,
    rotating,
    togglingStatus,
    showKeyDialog,
    showImportDialog,
    showKeyDetailsDialog,
    showDeleteDialog,
    selectedKey,
    selectedKeys,
    encryptionKeys,
    encryptionLogs,
    settings,
    newKey,
    importKey,
    
    // Constants
    keyAlgorithms,
    keySizes,
    encryptionLevels,
    
    // Methods
    loadData,
    generateKey,
    importKey: importKeyAction,
    viewKeyDetails,
    rotateKey,
    toggleKeyStatus,
    confirmDeleteKey,
    deleteKey,
    saveSettings,
    copyToClipboard,
    resetNewKeyForm,
    resetImportForm,
    cancelNewKey,
    cancelImport,
    formatDate,
    getKeyStatusSeverity,
    getLogStatusSeverity,
    getKeyStatusLabel,
    
    // Event handlers
    handleKeySelect: (event: { data: EncryptionKey | null }) => {
      selectedKey.value = event.data ? { ...event.data } : null;
    },
    handleKeyUnselect: () => {
      selectedKey.value = null;
    }
  };
