<template>
  <v-card class="module-card h-100" :color="module.color + '10'" elevation="2" rounded="lg">
    <v-card-item>
      <template v-slot:prepend>
        <v-avatar :color="module.color" size="large" class="elevation-1">
          <v-icon :icon="module.icon" size="large" color="white"></v-icon>
        </v-avatar>
      </template>
      <v-card-title class="font-weight-bold">{{ module.title }}</v-card-title>
      <v-card-subtitle>{{ module.description }}</v-card-subtitle>
    </v-card-item>

    <v-card-text>
      <v-divider class="mb-4"></v-divider>
      <div class="d-flex flex-wrap gap-2">
        <v-btn
          v-for="action in module.primaryActions"
          :key="action.route"
          :to="action.route"
          :color="module.color"
          variant="tonal"
          class="flex-grow-1 text-none action-button"
          rounded="lg"
        >
          <v-icon :icon="action.icon" start></v-icon>
          {{ action.name }}
        </v-btn>
      </div>
    </v-card-text>

    <v-card-actions>
      <v-btn
        variant="text"
        :color="module.color"
        :to="module.route"
        class="text-none"
      >
        View All
        <v-icon end icon="mdi-chevron-right"></v-icon>
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
defineProps({
  module: {
    type: Object,
    required: true
  }
});
</script>

<style>
.module-card {
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
}

.action-button {
  margin: 4px;
  white-space: nowrap;
}

.action-button .v-icon {
  margin-right: 4px;
}
</style>