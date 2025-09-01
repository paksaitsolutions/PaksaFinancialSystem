<template>
  <div class="verify-email-view">
    <Card class="text-center">
      <template #content>
        <div v-if="verifying" class="verification-loading">
          <ProgressSpinner />
          <h3 class="mt-3">Verifying your email...</h3>
          <p class="text-500">Please wait while we verify your email address.</p>
        </div>
        
        <div v-else-if="verificationSuccess" class="verification-success">
          <i class="pi pi-check-circle text-6xl text-green-500 mb-3"></i>
          <h3 class="text-green-600">Email Verified Successfully!</h3>
          <p class="text-500 mb-4">Your email address has been verified. You can now access all features of your account.</p>
          <Button 
            label="Continue to Login"
            icon="pi pi-sign-in"
            @click="$router.push('/auth/login')"
          />
        </div>
        
        <div v-else class="verification-error">
          <i class="pi pi-times-circle text-6xl text-red-500 mb-3"></i>
          <h3 class="text-red-600">Verification Failed</h3>
          <p class="text-500 mb-4">{{ errorMessage }}</p>
          <div class="flex gap-2 justify-content-center">
            <Button 
              label="Resend Verification"
              icon="pi pi-refresh"
              class="p-button-outlined"
              @click="resendVerification"
              :loading="resending"
            />
            <Button 
              label="Back to Login"
              icon="pi pi-arrow-left"
              @click="$router.push('/auth/login')"
            />
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const verifying = ref(true)
const verificationSuccess = ref(false)
const resending = ref(false)
const errorMessage = ref('The verification link is invalid or has expired.')

const verifyEmail = async () => {
  const token = route.params.token as string
  
  if (!token) {
    verifying.value = false
    errorMessage.value = 'No verification token provided.'
    return
  }
  
  try {
    // Mock email verification
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Simulate verification result
    const isValid = Math.random() > 0.3 // 70% success rate for demo
    
    if (isValid) {
      verificationSuccess.value = true
    } else {
      errorMessage.value = 'The verification link is invalid or has expired.'
    }
  } catch (error) {
    console.error('Email verification failed:', error)
    errorMessage.value = 'An error occurred during verification. Please try again.'
  } finally {
    verifying.value = false
  }
}

const resendVerification = async () => {
  resending.value = true
  try {
    // Mock resend verification
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Show success message or redirect
    router.push('/auth/login?message=verification-resent')
  } catch (error) {
    console.error('Failed to resend verification:', error)
  } finally {
    resending.value = false
  }
}

onMounted(() => {
  verifyEmail()
})
</script>

<style scoped>
.verify-email-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 2rem;
}

.verify-email-view .p-card {
  max-width: 500px;
  width: 100%;
}
</style>