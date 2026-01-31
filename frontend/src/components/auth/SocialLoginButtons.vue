<template>
  <div class="social-login">
    <div class="divider">
      <span>Or continue with</span>
    </div>
    
    <div class="social-buttons">
      <v-btn
        variant="outlined"
        color="primary"
        class="social-button"
        prepend-icon="mdi-google"
        @click="handleSocialLogin('google')"
      >
        Google
      </v-btn>
      
      <v-btn
        variant="outlined"
        color="primary"
        class="social-button"
        prepend-icon="mdi-microsoft"
        @click="handleSocialLogin('microsoft')"
      >
        Microsoft
      </v-btn>
      
      <v-btn
        variant="outlined"
        color="primary"
        class="social-button"
        prepend-icon="mdi-apple"
        @click="handleSocialLogin('apple')"
      >
        Apple
      </v-btn>
    </div>
  </div>
</template>

<script>

/**
 * SocialLoginButtons Component
 * 
 * @component
 */

export default {
  methods: {
    handleSocialLogin(provider) {
      // In a real app, this would redirect to OAuth provider
      console.log(`Login with ${provider}`);
      this.$emit('social-login', provider);
    }
  }
}
</script>

<style scoped>
.social-login {
  margin-top: 20px;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 20px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #ddd;
}

.divider span {
  padding: 0 10px;
  color: #777;
  font-size: 14px;
}

.social-buttons {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

.social-button {
  flex: 1;
  min-width: 100px;
}
</style>