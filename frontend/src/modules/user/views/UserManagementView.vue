<template>
  <v-container>
    <h1>User Management</h1>
    <p>Manage system users and permissions</p>
    <UserInviteDialog />
  </v-container>
</template>

<script setup>
import UserInviteDialog from '../components/UserInviteDialog.vue'
</script>