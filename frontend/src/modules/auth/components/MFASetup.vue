<template>
  <div class="mfa-setup">
    <v-card max-width="500" class="mx-auto">
      <v-card-title>Multi-Factor Authentication Setup</v-card-title>
      
      <v-card-text>
        <v-stepper v-model="step" vertical>
          <v-stepper-step :complete="step > 1" step="1">
            Choose Authentication Method
          </v-stepper-step>
          <v-stepper-content step="1">
            <v-radio-group v-model="selectedMethod">
              <v-radio label="Authenticator App (TOTP)" value="totp"></v-radio>
            </v-radio-group>
            
            <v-text-field
              v-model="deviceName"
              label="Device Name"
              placeholder="e.g., My Phone"
              :rules="[v => !!v || 'Device name is required']"
            ></v-text-field>
            
            <v-btn
              color="primary"
              :disabled="!selectedMethod || !deviceName"
              @click="setupDevice"
              :loading="loading"
            >
              Continue
            </v-btn>
          </v-stepper-content>
          
          <v-stepper-step :complete="step > 2" step="2">
            Scan QR Code
          </v-stepper-step>
          <v-stepper-content step="2">
            <div class="text-center">
              <p>Scan this QR code with your authenticator app:</p>
              <div v-if="qrCode" class="my-4">
                <img :src="`data:image/png;base64,${qrCode}`" alt="QR Code" />
              </div>
              
              <p class="text-caption">Or enter this secret key manually:</p>
              <v-text-field
                :value="secretKey"
                readonly
                density="compact"
                append-inner-icon="mdi-content-copy"
                @click:append-inner="copySecret"
              ></v-text-field>
            </div>
            
            <v-btn color="primary" @click="step = 3">
              I've Added the Account
            </v-btn>
          </v-stepper-content>
          
          <v-stepper-step :complete="step > 3" step="3">
            Verify Setup
          </v-stepper-step>
          <v-stepper-content step="3">
            <p>Enter the 6-digit code from your authenticator app:</p>
            
            <v-text-field
              v-model="verificationCode"
              label="Verification Code"
              placeholder="123456"
              maxlength="6"
              @keyup.enter="verifyCode"
            ></v-text-field>
            
            <v-btn
              color="primary"
              :disabled="!verificationCode || verificationCode.length !== 6"
              @click="verifyCode"
              :loading="verifying"
            >
              Verify & Enable
            </v-btn>
          </v-stepper-content>
          
          <v-stepper-step :complete="step > 4" step="4">
            Save Backup Codes
          </v-stepper-step>
          <v-stepper-content step="4">
            <v-alert type="warning" class="mb-4">
              Save these backup codes in a secure location.
            </v-alert>
            
            <v-card variant="outlined" class="pa-4 mb-4">
              <div class="backup-codes">
                <div
                  v-for="(code, index) in backupCodes"
                  :key="index"
                  class="backup-code"
                >
                  {{ code }}
                </div>
              </div>
            </v-card>
            
            <v-checkbox
              v-model="codesAcknowledged"
              label="I have saved these backup codes"
            ></v-checkbox>
            
            <v-btn
              color="success"
              :disabled="!codesAcknowledged"
              @click="completeMFASetup"
              block
            >
              Complete MFA Setup
            </v-btn>
          </v-stepper-content>
        </v-stepper>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

const { showSnackbar } = useSnackbar();
const emit = defineEmits(['completed']);

const step = ref(1);
const selectedMethod = ref('totp');
const deviceName = ref('');
const loading = ref(false);
const verifying = ref(false);
const verificationCode = ref('');
const codesAcknowledged = ref(false);

const setupData = reactive({
  deviceId: null,
  secretKey: '',
  qrCode: '',
  backupCodes: []
});

const { deviceId, secretKey, qrCode, backupCodes } = setupData;

const setupDevice = async () => {
  loading.value = true;
  try {
    const response = await apiClient.post('/api/v1/auth/mfa/setup', {
      device_type: selectedMethod.value,
      device_name: deviceName.value
    });
    
    Object.assign(setupData, response.data);
    step.value = 2;
    showSnackbar('MFA device setup initiated', 'success');
  } catch (error) {
    showSnackbar('Failed to setup MFA device', 'error');
  } finally {
    loading.value = false;
  }
};

const verifyCode = async () => {
  verifying.value = true;
  try {
    await apiClient.post('/api/v1/auth/mfa/verify', {
      device_id: deviceId,
      code: verificationCode.value
    });
    
    step.value = 4;
    showSnackbar('MFA device verified successfully', 'success');
  } catch (error) {
    showSnackbar('Invalid verification code', 'error');
  } finally {
    verifying.value = false;
  }
};

const copySecret = async () => {
  try {
    await navigator.clipboard.writeText(secretKey);
    showSnackbar('Secret key copied', 'success');
  } catch (error) {
    showSnackbar('Failed to copy', 'error');
  }
};

const completeMFASetup = () => {
  showSnackbar('MFA setup completed', 'success');
  emit('completed');
};
</script>

<style scoped>
.backup-codes {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  font-family: monospace;
}

.backup-code {
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
  text-align: center;
  font-weight: bold;
}
</style>