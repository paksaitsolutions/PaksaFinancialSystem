<template>
  <v-dialog v-model="dialog" max-width="500">
    <template v-slot:activator="{ props }">
      <v-btn icon v-bind="props">
        <v-icon>mdi-keyboard</v-icon>
      </v-btn>
    </template>
    
    <v-card>
      <v-card-title>Keyboard Shortcuts</v-card-title>
      <v-card-text>
        <v-list>
          <v-list-item>
            <v-list-item-title>Ctrl + K</v-list-item-title>
            <v-list-item-subtitle>Search</v-list-item-subtitle>
          </v-list-item>
          <v-list-item>
            <v-list-item-title>Ctrl + /</v-list-item-title>
            <v-list-item-subtitle>Show shortcuts</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="dialog = false">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref } from 'vue'

const dialog = ref(false)
</script>