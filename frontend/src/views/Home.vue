<template>
  <div class="home-page">
    <v-container>
      <v-row>
        <v-col cols="12">
          <div class="d-flex align-center mb-6">
            <h1 class="text-h4 font-weight-bold">Paksa Financial System</h1>
            <v-spacer></v-spacer>
            <v-btn color="primary" prepend-icon="mdi-refresh" @click="refreshData">
              Refresh
            </v-btn>
          </div>
          
          <v-fade-transition group>
            <v-alert
              v-if="showWelcome"
              color="primary"
              icon="mdi-information"
              variant="tonal"
              closable
              class="mb-6"
              @click:close="showWelcome = false"
            >
              Welcome to Paksa Financial System. Select a module below to get started.
            </v-alert>
          </v-fade-transition>
        </v-col>
      </v-row>
      
      <v-row>
        <v-col 
          v-for="module in menuStore.visibleModules" 
          :key="module.id"
          cols="12" sm="6" md="4" lg="4"
          class="mb-4"
        >
          <module-card :module="module" />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useMenuStore } from '@/stores/menu';
import ModuleCard from '@/components/home/ModuleCard.vue';

const menuStore = useMenuStore();
const showWelcome = ref(true);

const refreshData = () => {
  // In a real app, this would refresh data from the server
  showWelcome.value = true;
};
</script>

<style scoped>
.home-page {
  padding: 20px 0;
  min-height: 100vh;
  background-color: #f9fafc;
}
</style>