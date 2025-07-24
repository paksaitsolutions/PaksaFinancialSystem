<template>
  <div class="mfa-login">
    <v-card max-width="400" class="mx-auto">
      <v-card-title class="text-center">
        <v-icon color="primary" size="48" class="mb-2">mdi-shield-check</v-icon>
        <div>Two-Factor Authentication</div>
      </v-card-title>
      
      <v-card-text>
        <p class="text-center mb-4">
          Enter the 6-digit code from your authenticator app or use a backup code.
        </p>
        
        <v-form @submit.prevent="authenticate">
          <v-text-field
            v-model="code"
            label="Authentication Code"
            placeholder="123456"
            maxlength="10"
            :rules="[v => !!v || 'Code is required']"
            autofocus
            @keyup.enter="authenticate"
          ></v-text-field>
          
          <v-btn
            color="primary"
            :loading="loading"
            :disabled="!code"
            @click="authenticate"
            block
            class="mb-3"
          >
            Verify
          </v-btn>
          
          <div class="text-center">
            <v-btn
              variant="text"
              size="small"
              @click="showBackupCodeInput = !showBackupCodeInput"
            >
              Use backup code instead
            </v-btn>
          </div>
          
          <v-expand-transition>
            <div v-if="showBackupCodeInput" class="mt-3">
              <v-text-field
                v-model="backupCode"
                label="Backup Code"
                placeholder="ABCD-1234"
                maxlength="9"
                @keyup.enter="authenticateWithBackup"
              ></v-text-field>
              
              <v-btn
                color="secondary"
                :loading="loading"
                :disabled="!backupCode"
                @click="authenticateWithBackup"
                block
              >
                Use Backup Code
              </v-btn>
            </div>
          </v-expand-transition>
        </v-form>
        
        <div class="text-center mt-4">
          <v-btn variant="text" size="small" @click="$emit('cancel')">
            Cancel
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

const { showSnackbar } = useSnackbar();

const props = defineProps({
  userId: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['success', 'cancel']);

const code = ref('');
const backupCode = ref('');
const loading = ref(false);
const showBackupCodeInput = ref(false);

const authenticate = async () => {
  loading.value = true;
  try {
    await apiClient.post('/api/v1/auth/mfa/authenticate', {
      user_id: props.userId,
      code: code.value
    });
    
    showSnackbar('Authentication successful', 'success');
    emit('success');
  } catch (error) {
    showSnackbar('Invalid authentication code', 'error');
  } finally {
    loading.value = false;
  }
};

const authenticateWithBackup = async () => {
  loading.value = true;
  try {
    await apiClient.post('/api/v1/auth/mfa/authenticate', {
      user_id: props.userId,
      code: backupCode.value
    });
    
    showSnackbar('Authentication successful', 'success');
    emit('success');
  } catch (error) {
    showSnackbar('Invalid backup code', 'error');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.mfa-login {
  padding: 20px;
}
</style>