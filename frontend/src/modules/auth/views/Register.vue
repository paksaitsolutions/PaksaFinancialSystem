<template>
  <div class="register-form">
    <form @submit.prevent="handleRegister">
      <div class="field">
        <label for="fullName">Full Name</label>
        <InputText 
          id="fullName"
          v-model="form.fullName" 
          placeholder="Enter your full name"
          required
        />
      </div>

      <div class="field">
        <label for="email">Email</label>
        <InputText 
          id="email"
          v-model="form.email" 
          type="email"
          placeholder="Enter your email"
          required
        />
      </div>

      <div class="field">
        <label for="company">Company</label>
        <InputText 
          id="company"
          v-model="form.company" 
          placeholder="Enter your company name"
          required
        />
      </div>

      <div class="field">
        <label for="password">Password</label>
        <Password 
          id="password"
          v-model="form.password" 
          placeholder="Enter your password"
          :feedback="false"
          toggleMask
          required
        />
      </div>

      <Button 
        type="submit" 
        label="Create Account" 
        class="w-full"
        :loading="loading"
      />

      <div class="register-links">
        <router-link to="/auth/login" class="text-primary">
          Already have an account? Sign in
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
  fullName: '',
  email: '',
  company: '',
  password: ''
})

const handleRegister = async () => {
  loading.value = true
  try {
    // Mock registration
    await new Promise(resolve => setTimeout(resolve, 1000))
    router.push('/auth/login')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-form {
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

.register-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
  text-align: center;
}

.register-links a {
  text-decoration: none;
  font-size: 0.875rem;
}

.w-full {
  width: 100%;
}
</style>