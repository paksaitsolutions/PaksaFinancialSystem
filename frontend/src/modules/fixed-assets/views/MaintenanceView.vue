<template>
  <v-container>
    <h1>Asset Maintenance</h1>
    <MaintenanceSchedule />
    <MaintenanceForm />
  </v-container>
</template>

<script setup>
import MaintenanceSchedule from '../components/MaintenanceSchedule.vue'
import MaintenanceForm from '../components/MaintenanceForm.vue'
</script>