<template>
  <v-container fluid class="fill-height pa-0">
    <v-row no-gutters class="fill-height">
      <!-- Left side - Content -->
      <v-col cols="12" md="6" class="d-flex align-center justify-center">
        <v-card width="400" class="pa-6 elevation-0">
          <div class="text-center mb-6">
            <img src="/src/assets/logo.svg" alt="Paksa Financial System" height="60" class="mb-4">
            <slot name="header">
              <h1 class="text-h4 font-weight-bold">Welcome</h1>
              <p class="text-body-1 text-medium-emphasis">Sign in to your account</p>
            </slot>
          </div>

          <slot></slot>
        </v-card>
      </v-col>

      <!-- Right side - Background image -->
      <v-col cols="12" md="6" class="d-none d-md-flex">
        <v-img
          src="/src/assets/login-bg.svg"
          cover
          class="h-100"
        >
          <div class="d-flex flex-column justify-center align-center fill-height text-white px-8">
            <h2 class="text-h3 font-weight-bold mb-4">Paksa Financial System</h2>
            <p class="text-h6 text-center">
              A comprehensive enterprise financial management solution
            </p>
            <div class="mt-8">
              <v-chip color="primary" size="large">Secure Login</v-chip>
              <v-chip color="primary" variant="outlined" size="large" class="ml-2">Enterprise Ready</v-chip>
            </div>
          </div>
        </v-img>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
// No additional logic needed
</script>