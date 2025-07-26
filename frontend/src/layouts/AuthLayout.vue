<template>
  <v-app>
    <v-container fluid class="fill-height pa-0">
      <v-row no-gutters class="fill-height">
        <!-- Left side - Content -->
        <v-col cols="12" lg="6" class="d-flex align-center justify-center pa-4">
          <div class="auth-form" style="width: 100%; max-width: 400px;">
            <div class="text-center mb-6">
              <v-img src="/logo.png" alt="Paksa Financial System" height="60" class="mb-4 mx-auto" style="max-width: 60px;"></v-img>
              <slot name="header">
                <h1 class="text-h4 font-weight-bold">Welcome</h1>
                <p class="text-body-1 text-medium-emphasis">Sign in to your account</p>
              </slot>
            </div>

            <slot></slot>
          </div>
        </v-col>

        <!-- Right side - Background image -->
        <v-col cols="12" lg="6" class="d-none d-lg-flex">
          <v-img
            src="https://images.unsplash.com/photo-1551434678-e076c223a692?ixlib=rb-1.2.1&auto=format&fit=crop&w=2850&q=80"
            cover
            class="h-100"
            gradient="to top right, rgba(25,32,72,.7), rgba(25,32,72,.8)"
          >
            <div class="d-flex flex-column justify-center align-center fill-height text-white px-8">
              <h2 class="text-h3 font-weight-bold mb-4 text-center">Paksa Financial System</h2>
              <p class="text-h6 text-center mb-8">
                A comprehensive enterprise financial management solution
              </p>
              <div class="d-flex flex-wrap justify-center gap-2">
                <v-chip color="primary" size="large">Secure Login</v-chip>
                <v-chip color="primary" variant="outlined" size="large">Enterprise Ready</v-chip>
              </div>
            </div>
          </v-img>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<script setup>
// No additional logic needed
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}

.auth-form {
  width: 100%;
  max-width: 400px;
}

.gap-2 {
  gap: 0.5rem;
}

@media (max-width: 1264px) {
  .auth-form {
    max-width: 500px;
  }
}

@media (max-width: 600px) {
  .auth-form {
    max-width: 100%;
  }
}
</style>