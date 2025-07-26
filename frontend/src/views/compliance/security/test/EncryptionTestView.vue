<template>
  <div class="encryption-test-view">
    <div class="card">
      <h2>Encryption Management Test</h2>
      
      <!-- Test Controls -->
      <div class="test-controls">
        <Button 
          label="Test Get Keys" 
          @click="testGetKeys" 
          :loading="loading.getKeys"
          class="p-button-outlined"
        />
        <Button 
          label="Test Generate Key" 
          @click="testGenerateKey" 
          :loading="loading.generateKey"
          class="p-button-outlined"
        />
        <Button 
          label="Test Get Logs" 
          @click="testGetLogs" 
          :loading="loading.getLogs"
          class="p-button-outlined"
        />
        <Button 
          label="Test Get Settings" 
          @click="testGetSettings" 
          :loading="loading.getSettings"
          class="p-button-outlined"
        />
      </div>

      <!-- Results -->
      <div class="test-results">
        <h3>Test Results</h3>
        <div v-if="error" class="error-message">
          <Message severity="error" :closable="false">
            {{ error }}
          </Message>
        </div>
        
        <div v-if="success" class="success-message">
          <Message severity="success" :closable="false">
            {{ success }}
          </Message>
        </div>

        <div v-if="results" class="results-data">
          <pre>{{ JSON.stringify(results, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { encryptionService } from '@/services/encryptionService';
import { useToast } from 'vue/usetoast';

export default defineComponent({
  name: 'EncryptionTestView',
  setup() {
    const toast = useToast();
    const loading = ref({
      getKeys: false,
      generateKey: false,
      getLogs: false,
      getSettings: false
    });
    const error = ref('');
    const success = ref('');
    const results = ref<any>(null);

    const resetMessages = () => {
      error.value = '';
      success.value = '';
      results.value = null;
    };

    const testGetKeys = async () => {
      resetMessages();
      loading.value.getKeys = true;
      try {
        const keys = await encryptionService.getKeys();
        results.value = keys;
        success.value = 'Successfully fetched encryption keys';
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Fetched encryption keys successfully',
          life: 3000
        });
      } catch (err) {
        error.value = err instanceof Error ? err.message : 'Failed to fetch encryption keys';
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: error.value,
          life: 5000
        });
      } finally {
        loading.value.getKeys = false;
      }
    };

    const testGenerateKey = async () => {
      resetMessages();
      loading.value.generateKey = true;
      try {
        const keyData = {
          name: 'Test Key ' + new Date().toISOString(),
          algorithm: 'AES-256',
          keySize: 256,
          expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() // 30 days from now
        };
        
        const key = await encryptionService.generateKey(keyData);
        results.value = key;
        success.value = 'Successfully generated encryption key';
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Generated encryption key successfully',
          life: 3000
        });
      } catch (err) {
        error.value = err instanceof Error ? err.message : 'Failed to generate encryption key';
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: error.value,
          life: 5000
        });
      } finally {
        loading.value.generateKey = false;
      }
    };

    const testGetLogs = async () => {
      resetMessages();
      loading.value.getLogs = true;
      try {
        const logs = await encryptionService.getLogs();
        results.value = logs;
        success.value = 'Successfully fetched encryption logs';
      } catch (err) {
        error.value = err instanceof Error ? err.message : 'Failed to fetch encryption logs';
      } finally {
        loading.value.getLogs = false;
      }
    };

    const testGetSettings = async () => {
      resetMessages();
      loading.value.getSettings = true;
      try {
        const settings = await encryptionService.getSettings();
        results.value = settings;
        success.value = 'Successfully fetched encryption settings';
      } catch (err) {
        error.value = err instanceof Error ? err.message : 'Failed to fetch encryption settings';
      } finally {
        loading.value.getSettings = false;
      }
    };

    return {
      loading,
      error,
      success,
      results,
      testGetKeys,
      testGenerateKey,
      testGetLogs,
      testGetSettings
    };
  }
});
</script>

<style scoped>
.encryption-test-view {
  padding: 20px;
}

.test-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.test-results {
  margin-top: 20px;
  padding: 20px;
  background-color: var(--surface-card);
  border-radius: 6px;
  border: 1px solid var(--surface-border);
}

.results-data {
  margin-top: 20px;
  padding: 15px;
  background-color: var(--surface-ground);
  border-radius: 4px;
  max-height: 400px;
  overflow: auto;
}

.error-message,
.success-message {
  margin-bottom: 20px;
}
</style>
