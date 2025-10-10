<template>
  <div class="system-configuration">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2 class="text-2xl font-semibold text-900 m-0">System Configuration</h2>
      <Button 
        label="Save All Changes" 
        icon="pi pi-save" 
        :loading="saving" 
        @click="saveAllConfiguration"
      />
    </div>

    <div class="grid">
      <!-- Database Configuration -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-database text-primary"></i>
              <span>Database Configuration</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="dbHost" class="font-semibold">Database Host</label>
                  <InputText 
                    id="dbHost" 
                    v-model="config.database.host" 
                    class="w-full" 
                    placeholder="localhost"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="dbPort" class="font-semibold">Database Port</label>
                  <InputNumber 
                    id="dbPort" 
                    v-model="config.database.port" 
                    class="w-full" 
                    :min="1" 
                    :max="65535"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="dbName" class="font-semibold">Database Name</label>
                  <InputText 
                    id="dbName" 
                    v-model="config.database.name" 
                    class="w-full" 
                    placeholder="paksa_financial"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="dbMaxConnections" class="font-semibold">Max Connections</label>
                  <InputNumber 
                    id="dbMaxConnections" 
                    v-model="config.database.maxConnections" 
                    class="w-full" 
                    :min="1" 
                    :max="1000"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="flex gap-4">
                  <div class="field-checkbox">
                    <Checkbox id="dbSslEnabled" v-model="config.database.sslEnabled" :binary="true" />
                    <label for="dbSslEnabled" class="font-semibold ml-2">Enable SSL Connection</label>
                  </div>
                  <div class="field-checkbox">
                    <Checkbox id="dbLogging" v-model="config.database.logging" :binary="true" />
                    <label for="dbLogging" class="font-semibold ml-2">Enable Query Logging</label>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Email Configuration -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-envelope text-primary"></i>
              <span>Email Configuration</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="smtpHost" class="font-semibold">SMTP Host</label>
                  <InputText 
                    id="smtpHost" 
                    v-model="config.email.smtpHost" 
                    class="w-full" 
                    placeholder="smtp.gmail.com"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="smtpPort" class="font-semibold">SMTP Port</label>
                  <InputNumber 
                    id="smtpPort" 
                    v-model="config.email.smtpPort" 
                    class="w-full" 
                    :min="1" 
                    :max="65535"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="smtpUsername" class="font-semibold">SMTP Username</label>
                  <InputText 
                    id="smtpUsername" 
                    v-model="config.email.smtpUsername" 
                    class="w-full" 
                    placeholder="your-email@domain.com"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="smtpPassword" class="font-semibold">SMTP Password</label>
                  <Password 
                    id="smtpPassword" 
                    v-model="config.email.smtpPassword" 
                    class="w-full" 
                    toggleMask
                    :feedback="false"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="fromEmail" class="font-semibold">From Email</label>
                  <InputText 
                    id="fromEmail" 
                    v-model="config.email.fromEmail" 
                    class="w-full" 
                    placeholder="noreply@paksa.com"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="fromName" class="font-semibold">From Name</label>
                  <InputText 
                    id="fromName" 
                    v-model="config.email.fromName" 
                    class="w-full" 
                    placeholder="Paksa Financial System"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="flex gap-4">
                  <div class="field-checkbox">
                    <Checkbox id="emailSslEnabled" v-model="config.email.sslEnabled" :binary="true" />
                    <label for="emailSslEnabled" class="font-semibold ml-2">Enable SSL/TLS</label>
                  </div>
                  <div class="field-checkbox">
                    <Checkbox id="emailEnabled" v-model="config.email.enabled" :binary="true" />
                    <label for="emailEnabled" class="font-semibold ml-2">Enable Email Notifications</label>
                  </div>
                </div>
              </div>
              <div class="col-12">
                <Button 
                  label="Test Email Configuration" 
                  icon="pi pi-send" 
                  severity="secondary" 
                  outlined 
                  @click="testEmailConfiguration"
                  :loading="testingEmail"
                />
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- File Storage Configuration -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-folder text-primary"></i>
              <span>File Storage Configuration</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="storageType" class="font-semibold">Storage Type</label>
                  <Dropdown 
                    id="storageType" 
                    v-model="config.storage.type" 
                    :options="storageTypes" 
                    optionLabel="label" 
                    optionValue="value"
                    class="w-full"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="maxFileSize" class="font-semibold">Max File Size (MB)</label>
                  <InputNumber 
                    id="maxFileSize" 
                    v-model="config.storage.maxFileSize" 
                    class="w-full" 
                    :min="1" 
                    :max="1024"
                  />
                </div>
              </div>
              <div class="col-12" v-if="config.storage.type === 'local'">
                <div class="field">
                  <label for="localPath" class="font-semibold">Local Storage Path</label>
                  <InputText 
                    id="localPath" 
                    v-model="config.storage.localPath" 
                    class="w-full" 
                    placeholder="/var/www/uploads"
                  />
                </div>
              </div>
              <div class="col-12" v-if="config.storage.type === 's3'">
                <div class="grid">
                  <div class="col-12 md:col-6">
                    <div class="field">
                      <label for="s3Bucket" class="font-semibold">S3 Bucket</label>
                      <InputText 
                        id="s3Bucket" 
                        v-model="config.storage.s3Bucket" 
                        class="w-full" 
                        placeholder="paksa-files"
                      />
                    </div>
                  </div>
                  <div class="col-12 md:col-6">
                    <div class="field">
                      <label for="s3Region" class="font-semibold">S3 Region</label>
                      <InputText 
                        id="s3Region" 
                        v-model="config.storage.s3Region" 
                        class="w-full" 
                        placeholder="us-east-1"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Performance Configuration -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-chart-line text-primary"></i>
              <span>Performance Configuration</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="cacheTimeout" class="font-semibold">Cache Timeout (minutes)</label>
                  <InputNumber 
                    id="cacheTimeout" 
                    v-model="config.performance.cacheTimeout" 
                    class="w-full" 
                    :min="1" 
                    :max="1440"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="maxRequestSize" class="font-semibold">Max Request Size (MB)</label>
                  <InputNumber 
                    id="maxRequestSize" 
                    v-model="config.performance.maxRequestSize" 
                    class="w-full" 
                    :min="1" 
                    :max="100"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="requestTimeout" class="font-semibold">Request Timeout (seconds)</label>
                  <InputNumber 
                    id="requestTimeout" 
                    v-model="config.performance.requestTimeout" 
                    class="w-full" 
                    :min="5" 
                    :max="300"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="field">
                  <label for="workerProcesses" class="font-semibold">Worker Processes</label>
                  <InputNumber 
                    id="workerProcesses" 
                    v-model="config.performance.workerProcesses" 
                    class="w-full" 
                    :min="1" 
                    :max="16"
                  />
                </div>
              </div>
              <div class="col-12">
                <div class="flex gap-4">
                  <div class="field-checkbox">
                    <Checkbox id="enableCaching" v-model="config.performance.enableCaching" :binary="true" />
                    <label for="enableCaching" class="font-semibold ml-2">Enable Caching</label>
                  </div>
                  <div class="field-checkbox">
                    <Checkbox id="enableCompression" v-model="config.performance.enableCompression" :binary="true" />
                    <label for="enableCompression" class="font-semibold ml-2">Enable Response Compression</label>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Maintenance Mode -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-wrench text-primary"></i>
              <span>Maintenance Mode</span>
            </div>
          </template>
          <template #content>
            <div class="grid">
              <div class="col-12">
                <div class="field-checkbox">
                  <Checkbox id="maintenanceMode" v-model="config.maintenance.enabled" :binary="true" />
                  <label for="maintenanceMode" class="font-semibold ml-2">Enable Maintenance Mode</label>
                </div>
              </div>
              <div class="col-12" v-if="config.maintenance.enabled">
                <div class="field">
                  <label for="maintenanceMessage" class="font-semibold">Maintenance Message</label>
                  <Textarea 
                    id="maintenanceMessage" 
                    v-model="config.maintenance.message" 
                    class="w-full" 
                    rows="3"
                    placeholder="System is under maintenance. Please try again later."
                  />
                </div>
              </div>
              <div class="col-12 md:col-6" v-if="config.maintenance.enabled">
                <div class="field">
                  <label for="maintenanceStart" class="font-semibold">Maintenance Start</label>
                  <Calendar 
                    id="maintenanceStart" 
                    v-model="config.maintenance.startTime" 
                    class="w-full" 
                    showTime 
                    hourFormat="24"
                  />
                </div>
              </div>
              <div class="col-12 md:col-6" v-if="config.maintenance.enabled">
                <div class="field">
                  <label for="maintenanceEnd" class="font-semibold">Maintenance End</label>
                  <Calendar 
                    id="maintenanceEnd" 
                    v-model="config.maintenance.endTime" 
                    class="w-full" 
                    showTime 
                    hourFormat="24"
                  />
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
const testingEmail = ref(false)

const config = ref({
  database: {
    host: 'localhost',
    port: 5432,
    name: 'paksa_financial',
    maxConnections: 20,
    sslEnabled: false,
    logging: false
  },
  email: {
    smtpHost: '',
    smtpPort: 587,
    smtpUsername: '',
    smtpPassword: '',
    fromEmail: '',
    fromName: 'Paksa Financial System',
    sslEnabled: true,
    enabled: true
  },
  storage: {
    type: 'local',
    maxFileSize: 10,
    localPath: '/var/www/uploads',
    s3Bucket: '',
    s3Region: 'us-east-1'
  },
  performance: {
    cacheTimeout: 60,
    maxRequestSize: 10,
    requestTimeout: 30,
    workerProcesses: 4,
    enableCaching: true,
    enableCompression: true
  },
  maintenance: {
    enabled: false,
    message: 'System is under maintenance. Please try again later.',
    startTime: null,
    endTime: null
  }
})

const storageTypes = [
  { label: 'Local Storage', value: 'local' },
  { label: 'Amazon S3', value: 's3' },
  { label: 'Google Cloud Storage', value: 'gcs' },
  { label: 'Azure Blob Storage', value: 'azure' }
]

const loadConfiguration = async () => {
  try {
    const systemSettings = await settingsService.getSystemSettings()
    
    // Map system settings to configuration
    systemSettings.forEach(setting => {
      const keys = setting.setting_key.split('_')
      if (keys.length >= 2) {
        const section = keys[0]
        const key = keys.slice(1).join('_')
        
        if (section in config.value && key in config.value[section]) {
          const value = setting.setting_value
          if (typeof config.value[section][key] === 'boolean') {
            config.value[section][key] = value === 'true'
          } else if (typeof config.value[section][key] === 'number') {
            config.value[section][key] = parseInt(value)
          } else {
            config.value[section][key] = value
          }
        }
      }
    })
  } catch (error) {
    console.error('Error loading configuration:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load system configuration',
      life: 3000
    })
  }
}

const saveAllConfiguration = async () => {
  saving.value = true
  try {
    const promises: Promise<any>[] = []
    
    // Save each configuration section as system settings
    Object.entries(config.value).forEach(([section, settings]) => {
      Object.entries(settings).forEach(([key, value]) => {
        const settingKey = `${section}_${key}`
        promises.push(
          settingsService.updateSystemSetting(
            settingKey,
            String(value),
            `System configuration: ${section}.${key}`
          )
        )
      })
    })
    
    await Promise.all(promises)
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'System configuration saved successfully',
      life: 3000
    })
  } catch (error) {
    console.error('Error saving configuration:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save system configuration',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

const testEmailConfiguration = async () => {
  testingEmail.value = true
  try {
    // Mock email test - replace with real API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    toast.add({
      severity: 'success',
      summary: 'Email Test',
      detail: 'Test email sent successfully',
      life: 3000
    })
  } catch (error) {
    console.error('Error testing email:', error)
    toast.add({
      severity: 'error',
      summary: 'Email Test Failed',
      detail: 'Failed to send test email. Please check your configuration.',
      life: 3000
    })
  } finally {
    testingEmail.value = false
  }
}

onMounted(() => {
  loadConfiguration()
})
</script>

<style scoped>
.system-configuration {
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