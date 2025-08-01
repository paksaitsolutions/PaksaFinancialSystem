<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">Coming Soon</h1>
      <p class="text-xl text-gray-600 mb-8">{{ moduleName }} module is under development</p>
      <router-link 
        to="/" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        Go back home
      </router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue';
import { useRoute } from 'vue-router';

export default defineComponent({
  name: 'PlaceholderView',
  setup() {
    const route = useRoute();
    
    const moduleName = computed(() => {
      // Extract module name from the path
      const path = route.path.split('/')[1];
      return path ? path.toUpperCase() : 'This';
    });

    return {
      moduleName
    };
  }
});
</script>
