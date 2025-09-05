<template>
  <div class="verify-email-container">
    <Card class="verify-email-card">
      <template #header>
        <div class="verify-email-header">
          <img src="/logo.svg" alt="Paksa Financial" class="logo" />
          <h2>Email Verification</h2>
        </div>
      </template>
      
      <template #content>
        <div class="verify-email-content">
          <div v-if="loading" class="loading-state">
            <ProgressSpinner />
            <p>Verifying your email...</p>
          </div>
          
          <div v-else-if="verified" class="success-state">
            <i class="pi pi-check-circle success-icon"></i>
            <h3>Email Verified Successfully!</h3>
            <p>Your email has been verified. You can now access your account.</p>
            <Button 
              label="Continue to Login" 
              class="w-full verify-btn"
              @click="$router.push('/auth/login')"
            />
          </div>
          
          <div v-else class="error-state">
            <i class="pi pi-times-circle error-icon"></i>
            <h3>Verification Failed</h3>
            <p>{{ errorMessage }}</p>
            <div class="error-actions">
              <Button 
                label="Resend Verification" 
                class="w-full verify-btn mb-2"
                @click="resendVerification"
                :loading="resending"
              />
              <Button 
                label="Back to Login" 
                class="w-full p-button-text"
                @click="$router.push('/auth/login')"
              />
            </div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'

const route = useRoute()
const toast = useToast()

const loading = ref(true)
const verified = ref(false)
const resending = ref(false)
const errorMessage = ref('')

const verifyEmail = async () => {
  try {
    const token = route.params.token
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Simulate random success/failure for demo
    const success = Math.random() > 0.3
    
    if (success) {
      verified.value = true
    } else {
      throw new Error('Invalid or expired verification token')
    }
  } catch (error: any) {
    verified.value = false
    errorMessage.value = error.message || 'Verification failed'
  } finally {
    loading.value = false
  }
}

const resendVerification = async () => {
  resending.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Verification email sent successfully', 
      life: 5000 
    })
  } catch (error: any) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to send verification email', 
      life: 5000 
    })
  } finally {
    resending.value = false
  }
}

onMounted(() => {
  verifyEmail()
})
</script>

<style scoped>
.verify-email-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.verify-email-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.verify-email-header {
  text-align: center;
  padding: 2rem 2rem 0;
}

.logo {
  height: 60px;
  margin-bottom: 1rem;
}

.verify-email-header h2 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.75rem;
  font-weight: 600;
}

.verify-email-content {
  padding: 2rem;
  text-align: center;
}

.loading-state p {
  margin-top: 1rem;
  color: var(--text-color-secondary);
}

.success-icon {
  font-size: 4rem;
  color: var(--green-500);
  margin-bottom: 1rem;
}

.error-icon {
  font-size: 4rem;
  color: var(--red-500);
  margin-bottom: 1rem;
}

.success-state h3,
.error-state h3 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
}

.success-state p,
.error-state p {
  margin-bottom: 2rem;
  color: var(--text-color-secondary);
  line-height: 1.6;
}

.verify-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 0.75rem;
  font-weight: 600;
}

.error-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>