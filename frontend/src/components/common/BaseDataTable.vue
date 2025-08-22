<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <v-icon :icon="icon" class="me-2"></v-icon>
      {{ title }}
      <v-spacer></v-spacer>
      <v-btn color="primary" @click="$emit('create')" v-if="showCreate">
        <v-icon start>mdi-plus</v-icon>
        Add {{ entityName }}
      </v-btn>
    </v-card-title>
    
    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="items"
        :loading="loading"
        :search="search"
        class="elevation-1"
      >
        <template v-slot:top>
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search"
            single-line
            hide-details
            class="mb-4"
          ></v-text-field>
        </template>
        
        <template v-slot:item.actions="{ item }">
          <v-btn icon size="small" @click="$emit('edit', item)" class="me-2">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn icon size="small" @click="$emit('delete', item)" color="error">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
        
        <template v-slot:no-data>
          <div class="text-center py-4">
            <v-icon size="64" color="grey-lighten-1">{{ icon }}</v-icon>
            <p class="text-h6 mt-2">No {{ entityName.toLowerCase() }}s found</p>
            <v-btn color="primary" @click="$emit('create')" v-if="showCreate">
              Create your first {{ entityName.toLowerCase() }}
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  title: string
  icon: string
  entityName: string
  headers: any[]
  items: any[]
  loading?: boolean
  showCreate?: boolean
}

defineProps<Props>()
defineEmits<{
  create: []
  edit: [item: any]
  delete: [item: any]
}>()

const search = ref('')
</script>