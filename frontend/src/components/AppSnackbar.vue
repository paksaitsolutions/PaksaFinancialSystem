<template>
  <v-snackbar
    v-model="isVisible"
    :timeout="currentTimeout"
    :color="currentType"
    location="bottom right"
    class="app-snackbar"
  >
    <div class="d-flex align-center">
      <v-icon v-if="currentType === 'success'" class="me-2">mdi-check-circle</v-icon>
      <v-icon v-else-if="currentType === 'error'" class="me-2">mdi-alert-circle</v-icon>
      <v-icon v-else-if="currentType === 'warning'" class="me-2">mdi-alert</v-icon>
      <v-icon v-else class="me-2">mdi-information</v-icon>
      
      <span class="text-body-2">{{ currentMessage }}</span>
    </div>

    <template v-slot:actions>
      <v-btn
        icon
        variant="text"
        @click="close"
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';

export default {
  name: 'AppSnackbar',
  
  setup() {
    const isVisible = ref(false);
    const currentMessage = ref('');
    const currentType = ref('info');
    const currentTimeout = ref(6000);

    function show({ message, type = 'info', timeout = 6000 }) {
      currentMessage.value = message;
      currentType.value = type;
      currentTimeout.value = timeout;
      isVisible.value = true;
    }

    function close() {
      isVisible.value = false;
    }

    // Register global event listeners
    onMounted(() => {
      const app = document.querySelector('#app');
      if (app && app.__vue_app__) {
        app.__vue_app__.config.globalProperties.$root.$on('show-snackbar', show);
      }
    });

    // Clean up event listeners
    onUnmounted(() => {
      const app = document.querySelector('#app');
      if (app && app.__vue_app__) {
        app.__vue_app__.config.globalProperties.$root.$off('show-snackbar', show);
      }
    });

    return {
      isVisible,
      currentMessage,
      currentType,
      currentTimeout,
      close
    };
  }
};
</script>

<style scoped>
.app-snackbar {
  margin-bottom: 16px;
  margin-right: 16px;
}

.app-snackbar :deep(.v-snackbar__content) {
  padding: 8px 0;
}
</style>
