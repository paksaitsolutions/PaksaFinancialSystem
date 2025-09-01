<template>
  <Card>
    <template #header>
      <h3 class="p-4 m-0">Security Settings</h3>
    </template>
    <template #content>
      <div class="grid">
        <div class="col-12">
          <h4>Password Policy</h4>
          <div class="field-checkbox">
            <Checkbox id="requireUppercase" v-model="security.requireUppercase" :binary="true" />
            <label for="requireUppercase">Require uppercase letters</label>
          </div>
          
          <div class="field-checkbox">
            <Checkbox id="requireNumbers" v-model="security.requireNumbers" :binary="true" />
            <label for="requireNumbers">Require numbers</label>
          </div>
          
          <div class="field-checkbox">
            <Checkbox id="requireSpecialChars" v-model="security.requireSpecialChars" :binary="true" />
            <label for="requireSpecialChars">Require special characters</label>
          </div>
          
          <div class="field">
            <label for="minPasswordLength">Minimum password length</label>
            <InputNumber id="minPasswordLength" v-model="security.minPasswordLength" :min="6" :max="20" />
          </div>
        </div>
        
        <div class="col-12">
          <h4>Session Management</h4>
          <div class="field">
            <label for="sessionTimeout">Session timeout (minutes)</label>
            <InputNumber id="sessionTimeout" v-model="security.sessionTimeout" :min="15" :max="480" />
          </div>
          
          <div class="field-checkbox">
            <Checkbox id="enableMFA" v-model="security.enableMFA" :binary="true" />
            <label for="enableMFA">Enable Multi-Factor Authentication</label>
          </div>
        </div>
        
        <div class="col-12">
          <h4>Login Security</h4>
          <div class="field">
            <label for="maxLoginAttempts">Max login attempts</label>
            <InputNumber id="maxLoginAttempts" v-model="security.maxLoginAttempts" :min="3" :max="10" />
          </div>
          
          <div class="field">
            <label for="lockoutDuration">Lockout duration (minutes)</label>
            <InputNumber id="lockoutDuration" v-model="security.lockoutDuration" :min="5" :max="60" />
          </div>
        </div>
      </div>
      
      <div class="flex justify-content-end mt-4">
        <Button label="Save Security Settings" @click="saveSecuritySettings" />
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const security = ref({
  requireUppercase: true,
  requireNumbers: true,
  requireSpecialChars: false,
  minPasswordLength: 8,
  sessionTimeout: 60,
  enableMFA: false,
  maxLoginAttempts: 5,
  lockoutDuration: 15
})

const saveSecuritySettings = () => {
  console.log('Saving security settings:', security.value)
}
</script>