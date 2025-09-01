<template>
  <div class="reset-password-form">
    <form @submit.prevent="handleResetPassword">
      <div class="field">
        <label for="password">New Password</label>
        <Password 
          id="password"
          v-model="form.password" 
          placeholder="Enter new password"
          :feedback="false"
          toggleMask
          required
        />
      </div>

      <div class="field">
        <label for="confirmPassword">Confirm Password</label>
        <Password 
          id="confirmPassword"
          v-model="form.confirmPassword" 
          placeholder="Confirm new password"
          :feedback="false"
          toggleMask
          required
        />
      </div>

      <Button 
        type="submit" 
        label="Reset Password" 
        class="w-full"
        :loading="loading"
      />
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)

const form = reactive({
  password: '',
  confirmPassword: ''
})

const handleResetPassword = async () => {
  loading.value = true
  try {
    // Mock reset password
    await new Promise(resolve => setTimeout(resolve, 1000))
    router.push('/auth/login')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.reset-password-form {
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

.w-full {
  width: 100%;
}
</style>