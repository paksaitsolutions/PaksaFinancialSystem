<template>
  <div class="module-view">
    <v-container>
      <v-row>
        <v-col cols="12">
          <div class="d-flex align-center mb-6">
            <v-avatar :color="color || 'primary'" size="large" class="mr-3">
              <v-icon :icon="getModuleIcon()" size="large" color="white"></v-icon>
            </v-avatar>
            <h1 class="text-h4 font-weight-bold">{{ title }}</h1>
            <v-spacer></v-spacer>
            <v-btn :color="color || 'primary'" prepend-icon="mdi-refresh" @click="refreshData">
              Refresh
            </v-btn>
          </div>
          
          <v-card :color="(color || 'primary') + '10'" rounded="lg" elevation="1" class="mb-6">
            <v-card-text>
              <div class="d-flex align-center">
                <v-icon icon="mdi-information" :color="color || 'primary'" class="mr-2"></v-icon>
                <span>This is a placeholder for the {{ title }} view. In a real implementation, this would contain the actual module content.</span>
              </div>
            </v-card-text>
          </v-card>
          
          <v-card rounded="lg" elevation="2">
            <v-card-title class="d-flex align-center">
              <span>{{ title }} Content</span>
              <v-spacer></v-spacer>
              <v-btn-group variant="outlined" :color="color || 'primary'">
                <v-btn prepend-icon="mdi-view-grid">Grid</v-btn>
                <v-btn prepend-icon="mdi-view-list">List</v-btn>
              </v-btn-group>
            </v-card-title>
            
            <v-divider></v-divider>
            
            <v-card-text class="pa-6">
              <v-skeleton-loader
                v-if="loading"
                type="table"
              ></v-skeleton-loader>
              
              <div v-else>
                <v-table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Description</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="i in 5" :key="i">
                      <td>{{ 1000 + i }}</td>
                      <td>Item {{ i }}</td>
                      <td>Description for item {{ i }}</td>
                      <td>
                        <v-chip
                          :color="i % 2 === 0 ? 'success' : 'warning'"
                          size="small"
                          variant="tonal"
                        >
                          {{ i % 2 === 0 ? 'Active' : 'Pending' }}
                        </v-chip>
                      </td>
                      <td>
                        <v-btn
                          icon="mdi-pencil"
                          :color="color || 'primary'"
                          variant="text"
                          size="small"
                        ></v-btn>
                        <v-btn
                          icon="mdi-delete"
                          color="error"
                          variant="text"
                          size="small"
                        ></v-btn>
                      </td>
                    </tr>
                  </tbody>
                </v-table>
                
                <div class="d-flex justify-end mt-4">
                  <v-pagination
                    v-model="page"
                    :length="5"
                    :color="color || 'primary'"
                    rounded="circle"
                  ></v-pagination>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useMenuStore } from '@/stores/menu';

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: null
  }
});

const menuStore = useMenuStore();
const loading = ref(true);
const page = ref(1);

onMounted(() => {
  // Simulate loading data
  setTimeout(() => {
    loading.value = false;
  }, 1000);
});

const refreshData = () => {
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 1000);
};

const getModuleIcon = () => {
  // Find the module that matches the current title
  const module = menuStore.modules.find(m => m.title === props.title);
  if (module) {
    return module.icon;
  }
  
  // Check if this is a subpage
  for (const module of menuStore.modules) {
    const subItem = module.subItems.find(s => s.name === props.title);
    if (subItem) {
      return subItem.icon;
    }
  }
  
  // Default icon
  return 'mdi-view-dashboard';
};
</script>

<style>
.module-view {
  padding: 20px 0;
  min-height: 100vh;
  background-color: #f9fafc;
}
</style>