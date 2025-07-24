<template>
  <v-dialog v-model="dialog" max-width="600px">
    <template v-slot:activator="{ props }">
      <v-btn
        v-bind="props"
        icon="mdi-keyboard"
        variant="text"
        title="Keyboard Shortcuts (Ctrl+?)"
      />
    </template>
    
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-keyboard</v-icon>
        Keyboard Shortcuts
        <v-spacer></v-spacer>
        <v-btn icon="mdi-close" variant="text" @click="dialog = false" />
      </v-card-title>
      
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <h3 class="mb-3">Navigation</h3>
            <div v-for="shortcut in navigationShortcuts" :key="shortcut.key" class="shortcut-item">
              <div class="shortcut-keys">
                <kbd v-if="shortcut.ctrl">Ctrl</kbd>
                <kbd v-if="shortcut.alt">Alt</kbd>
                <kbd v-if="shortcut.shift">Shift</kbd>
                <kbd>{{ shortcut.key.toUpperCase() }}</kbd>
              </div>
              <span class="shortcut-description">{{ shortcut.description }}</span>
            </div>
          </v-col>
          
          <v-col cols="12" md="6">
            <h3 class="mb-3">Actions</h3>
            <div v-for="shortcut in actionShortcuts" :key="shortcut.key" class="shortcut-item">
              <div class="shortcut-keys">
                <kbd v-if="shortcut.ctrl">Ctrl</kbd>
                <kbd v-if="shortcut.alt">Alt</kbd>
                <kbd v-if="shortcut.shift">Shift</kbd>
                <kbd>{{ shortcut.key === 'Escape' ? 'Esc' : shortcut.key.toUpperCase() }}</kbd>
              </div>
              <span class="shortcut-description">{{ shortcut.description }}</span>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
      
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="dialog = false">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useKeyboardShortcuts } from '@/composables/useKeyboardShortcuts'

const dialog = ref(false)
const { shortcuts } = useKeyboardShortcuts()

const navigationShortcuts = computed(() => 
  shortcuts.filter(s => s.description.includes('Go to'))
)

const actionShortcuts = computed(() => 
  shortcuts.filter(s => !s.description.includes('Go to'))
)

// Listen for Ctrl+? to open help
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === '?') {
    e.preventDefault()
    dialog.value = true
  }
})
</script>

<style scoped>
.shortcut-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 12px;
}

.shortcut-keys {
  display: flex;
  gap: 4px;
  min-width: 120px;
}

kbd {
  background: #f5f5f5;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 11px;
  font-family: monospace;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

[data-theme="dark"] kbd {
  background: #333;
  border-color: #555;
  color: #fff;
}

.shortcut-description {
  flex: 1;
  font-size: 14px;
}
</style>