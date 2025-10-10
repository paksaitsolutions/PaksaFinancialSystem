<template>
  <div class="security-settings">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2 class="text-2xl font-semibold text-900 m-0">Security Settings</h2>
      <Button 
        label="Save All Changes" 
        icon="pi pi-save" 
        :loading="saving" 
        @click="saveSecuritySettings"
      />
    </div>

    <div class="grid">
      <!-- Password Policy -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-lock text-primary"></i>
              <span>Password Policy</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="minPasswordLength" class="font-semibold">Minimum Password Length</label>
                  <InputNumber 
                    id="minPasswordLength" 
                    v-model="security.minPasswordLength" 
                    :min="6" 
                    :max="20" 
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="passwordExpiry" class="font-semibold">Password Expiry (days)</label>
                  <InputNumber 
                    id="passwordExpiry" 
                    v-model="security.passwordExpiry" 
                    :min="0" 
                    :max="365" 
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="grid">
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="requireUppercase" v-model="security.requireUppercase" :binary="true" />
                      <label for="requireUppercase" class="font-semibold ml-2">Require uppercase letters</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="requireNumbers" v-model="security.requireNumbers" :binary="true" />
                      <label for="requireNumbers" class="font-semibold ml-2">Require numbers</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="requireSpecialChars" v-model="security.requireSpecialChars" :binary="true" />
                      <label for="requireSpecialChars" class="font-semibold ml-2">Require special characters</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="preventPasswordReuse" v-model="security.preventPasswordReuse" :binary="true" />
                      <label for="preventPasswordReuse" class="font-semibold ml-2">Prevent password reuse</label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Session Management -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-clock text-primary"></i>
              <span>Session Management</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="sessionTimeout" class="font-semibold">Session Timeout (minutes)</label>
                  <InputNumber 
                    id="sessionTimeout" 
                    v-model="security.sessionTimeout" 
                    :min="15" 
                    :max="480" 
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="maxConcurrentSessions" class="font-semibold">Max Concurrent Sessions</label>
                  <InputNumber 
                    id="maxConcurrentSessions" 
                    v-model="security.maxConcurrentSessions" 
                    :min="1" 
                    :max="10" 
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="grid">
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="enableMFA" v-model="security.enableMFA" :binary="true" />
                      <label for="enableMFA" class="font-semibold ml-2">Enable Multi-Factor Authentication</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="rememberDevice" v-model="security.rememberDevice" :binary="true" />
                      <label for="rememberDevice" class="font-semibold ml-2">Remember trusted devices</label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Login Security -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-shield text-primary"></i>
              <span>Login Security</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="maxLoginAttempts" class="font-semibold">Max Login Attempts</label>
                  <InputNumber 
                    id="maxLoginAttempts" 
                    v-model="security.maxLoginAttempts" 
                    :min="3" 
                    :max="10" 
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="lockoutDuration" class="font-semibold">Lockout Duration (minutes)</label>
                  <InputNumber 
                    id="lockoutDuration" 
                    v-model="security.lockoutDuration" 
                    :min="5" 
                    :max="60" 
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="grid">
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="enableCaptcha" v-model="security.enableCaptcha" :binary="true" />
                      <label for="enableCaptcha" class="font-semibold ml-2">Enable CAPTCHA after failed attempts</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="logFailedAttempts" v-model="security.logFailedAttempts" :binary="true" />
                      <label for="logFailedAttempts" class="font-semibold ml-2">Log failed login attempts</label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Data Protection -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-key text-primary"></i>
              <span>Data Protection</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="encryptionLevel" class="font-semibold">Encryption Level</label>
                  <Dropdown 
                    id="encryptionLevel" 
                    v-model="security.encryptionLevel" 
                    :options="encryptionLevels" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="backupEncryption" class="font-semibold">Backup Encryption</label>
                  <Dropdown 
                    id="backupEncryption" 
                    v-model="security.backupEncryption" 
                    :options="encryptionLevels" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="grid">
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="enableAuditLog" v-model="security.enableAuditLog" :binary="true" />
                      <label for="enableAuditLog" class="font-semibold ml-2">Enable audit logging</label>
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field-checkbox">
                      <Checkbox id="enableDataMasking" v-model="security.enableDataMasking" :binary="true" />
                      <label for="enableDataMasking" class="font-semibold ml-2">Enable sensitive data masking</label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import settingsService from '@/api/settingsService'

const toast = useToast()
const saving = ref(false)

const security = ref({
  minPasswordLength: 8,
  passwordExpiry: 90,
  requireUppercase: true,
  requireNumbers: true,
  requireSpecialChars: false,
  preventPasswordReuse: true,
  sessionTimeout: 60,
  maxConcurrentSessions: 3,
  enableMFA: false,
  rememberDevice: true,
  maxLoginAttempts: 5,
  lockoutDuration: 15,
  enableCaptcha: true,
  logFailedAttempts: true,
  encryptionLevel: 'AES256',
  backupEncryption: 'AES256',
  enableAuditLog: true,
  enableDataMasking: true
})

const encryptionLevels = [
  { label: 'AES-128', value: 'AES128' },
  { label: 'AES-256', value: 'AES256' },
  { label: 'RSA-2048', value: 'RSA2048' },
  { label: 'RSA-4096', value: 'RSA4096' }
]

const loadSecuritySettings = async () => {
  try {
    const systemSettings = await settingsService.getSystemSettings()
    
    // Map system settings to security settings
    systemSettings.forEach(setting => {
      if (setting.setting_key.startsWith('security_')) {
        const key = setting.setting_key.replace('security_', '')
        if (key in security.value) {
          const value = setting.setting_value
          if (typeof security.value[key] === 'boolean') {
            security.value[key] = value === 'true'
          } else if (typeof security.value[key] === 'number') {
            security.value[key] = parseInt(value)
          } else {
            security.value[key] = value
          }
        }
      }
    })
  } catch (error) {
    console.error('Error loading security settings:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load security settings',
      life: 3000
    })
  }
}

const saveSecuritySettings = async () => {
  saving.value = true
  try {
    // Save each security setting as a system setting
    const promises = Object.entries(security.value).map(([key, value]) => {
      return settingsService.updateSystemSetting(
        `security_${key}`,
        String(value),
        `Security setting: ${key}`
      )
    })
    
    await Promise.all(promises)
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Security settings saved successfully',
      life: 3000
    })
  } catch (error) {
    console.error('Error saving security settings:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save security settings',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadSecuritySettings()
})
</script>

<style scoped>
.security-settings {
  max-width: 1200px;
  margin: 0 auto;
}

.field {
  margin-bottom: 1rem;
}

.field-checkbox {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.text-primary {
  color: var(--primary-color) !important;
}
</style>