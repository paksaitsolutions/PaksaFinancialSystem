<template>
  <div class="forgot-password-form">
    <form @submit.prevent="handleForgotPassword">
      <div class="field">
        <label for="email">Email</label>
        <InputText 
          id="email"
          v-model="form.email" 
          type="email"
          placeholder="Enter your email address"
          required
        />
      </div>

      <Button 
        type="submit" 
        label="Send Reset Link" 
        class="w-full"
        :loading="loading"
      />

      <div class="forgot-links">
        <router-link to="/auth/login" class="text-primary">
          Back to Sign In
        </router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  email: ''
})

const handleForgotPassword = async () => {
  loading.value = true
  try {
    // Mock forgot password
    await new Promise(resolve => setTimeout(resolve, 1000))
    router.push('/auth/login')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forgot-password-form {
  width: 100%;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.forgot-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
  text-align: center;
}

.forgot-links a {
  text-decoration: none;
  font-size: 0.875rem;
}

.w-full {
  width: 100%;
}
</style>