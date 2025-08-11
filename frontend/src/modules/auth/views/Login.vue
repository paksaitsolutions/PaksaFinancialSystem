<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="avatar-placeholder"></div>
        <h2>Welcome Back</h2>
        <p>Sign in to continue to Paksa Financial System</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="field">
          <label for="email">Email Address</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="Enter your email"
            :class="{ 'error': errors.email }"
            required
          />
          <small v-if="errors.email" class="error-text">{{ errors.email }}</small>
        </div>
        
        <div class="field">
          <div class="password-header">
            <label for="password">Password</label>
            <router-link to="/auth/forgot-password" class="forgot-link">
              Forgot password?
            </router-link>
          </div>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="Enter your password"
            :class="{ 'error': errors.password }"
            required
          />
          <small v-if="errors.password" class="error-text">{{ errors.password }}</small>
        </div>
        
        <div class="field-checkbox">
          <input
            id="remember"
            v-model="form.remember"
            type="checkbox"
          />
          <label for="remember">Remember me for 30 days</label>
        </div>
        
        <button
          type="submit"
          :disabled="!isFormValid || loading"
          class="submit-btn"
        >
          {{ loading ? 'Signing In...' : 'Sign In' }}
        </button>
        
        <div class="signup-link">
          <span>Don't have an account? </span>
          <router-link to="/auth/register">Create account</router-link>
        </div>
      </form>
      
      <div v-if="message" class="message" :class="messageType">
        {{ message }}
      <template>
        <Card>
          <template #header>
            <div class="login-header">
              <Avatar icon="pi pi-user" size="xlarge" />
              <h2>Welcome Back</h2>
              <p>Sign in to continue to Paksa Financial System</p>
            </div>
          </template>
          <template #content>
            <form @submit.prevent="handleLogin" class="login-form">
              <div class="field">
                <label for="email">Email Address</label>
                <InputText
                  id="email"
                  v-model="form.email"
                  type="email"
                  placeholder="Enter your email"
                  :class="{ 'p-invalid': errors.email }"
                  required
                />
                <small v-if="errors.email" class="p-error">{{ errors.email }}</small>
              </div>
              <div class="field">
                <div class="password-header">
                  <label for="password">Password</label>
                  <router-link to="/auth/forgot-password" class="forgot-link">
                    Forgot password?
                  </router-link>
                </div>
                <Password
                  id="password"
                  v-model="form.password"
                  placeholder="Enter your password"
                  :feedback="false"
                  toggleMask
                  :class="{ 'p-invalid': errors.password }"
                  required
                />
                <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
              </div>
              <div class="field-checkbox">
                <Checkbox
                  v-model="form.remember"
                  :binary="true"
                />
                <label for="remember">Remember me for 30 days</label>
              </div>
              <Button
                type="submit"
                label="Sign In"
                icon="pi pi-sign-in"
                :loading="loading"
                :disabled="!isFormValid || loading"
                class="submit-btn"
              />
              <div class="signup-link">
                <span>Don't have an account? </span>
                <router-link to="/auth/register">Create account</router-link>
              </div>
            </form>
          </template>
        </Card>
        <Toast />
      new URLSearchParams({
        username: form.email.trim(),
        password: form.password
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )

    if (response.data.access_token) {
      localStorage.setItem('auth_token', response.data.access_token)
      if (form.remember) {
        localStorage.setItem('rememberedEmail', form.email)
      } else {
        localStorage.removeItem('rememberedEmail')
      }
      message.value = 'Login successful! Redirecting...'
      messageType.value = 'success'
      setTimeout(() => {
        router.push('/')
      }, 1000)
    }
  } catch (error) {
    console.error('Login error:', error)
    message.value = 'Login failed. Please check your credentials.'
    messageType.value = 'error'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const rememberedEmail = localStorage.getItem('rememberedEmail')
  if (rememberedEmail) {
    form.email = rememberedEmail
    form.remember = true
  }
})
</script>

<style scoped>
.login-container {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.login-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.login-header {
  text-align: center;
  padding: 2rem 2rem 1rem;
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  background: var(--primary-color);
  border-radius: 50%;
  margin: 0 auto 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
}

.login-header h2 {
  margin: 0 0 0.5rem;
  color: var(--text-color);
}

.login-header p {
  margin: 0;
  color: var(--text-color-secondary);
}

.login-form {
  padding: 0 2rem 2rem;
}

.field {
  margin-bottom: 1.5rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.password-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.forgot-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 0.875rem;
}

.forgot-link:hover {
  text-decoration: underline;
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.field-checkbox label {
  margin: 0;
  font-size: 0.875rem;
}

.submit-btn {
  width: 100%;
  padding: 0.75rem;
  background: var(--primary-color, #007bff);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-bottom: 1rem;
  transition: background-color 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: var(--primary-color-dark, #0056b3);
}

.submit-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.signup-link {
  text-align: center;
  font-size: 0.875rem;
}

.signup-link a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.signup-link a:hover {
  text-decoration: underline;
}

input[type="email"], input[type="password"] {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input[type="email"]:focus, input[type="password"]:focus {
  outline: none;
  border-color: var(--primary-color);
}

input.error {
  border-color: #e74c3c;
}

.error-text {
  color: #e74c3c;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  display: block;
}

.message {
  padding: 0.75rem;
  margin: 1rem 2rem;
  border-radius: 4px;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>