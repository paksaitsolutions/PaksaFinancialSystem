<template>
  <div class="bg-white rounded-lg shadow-md overflow-hidden transition-all duration-300 hover:shadow-lg">
    <div class="p-6">
      <!-- Icon -->
      <div 
        class="flex items-center justify-center h-12 w-12 rounded-full mb-4"
        :class="`bg-${color}-100 text-${color}-600`"
      >
        <svg 
          class="h-6 w-6" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            :d="icon" 
          />
        </svg>
      </div>
      
      <!-- Title & Description -->
      <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ title }}</h3>
      <p class="text-gray-600 text-sm mb-4">{{ description }}</p>
      
      <!-- Actions -->
      <div class="flex flex-col space-y-2">
        <router-link
          v-for="(action, index) in actions"
          :key="index"
          :to="action.to"
          class="text-sm font-medium text-center px-4 py-2 rounded-md transition-colors"
          :class="[
            index === 0 
              ? `bg-${color}-600 text-white hover:bg-${color}-700`
              : `text-${color}-600 hover:bg-${color}-50`
          ]"
        >
          {{ action.label }}
        </router-link>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';


/**
 * ModuleCard Component
 * 
 * @component
 */

export interface ModuleAction {
  label: string;
  to: string;
}

export default defineComponent({
  name: 'ModuleCard',
  
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      required: true
    },
    color: {
      type: String,
      default: 'blue',
      validator: (value: string) => {
        return [
          'blue', 'green', 'purple', 'yellow', 
          'indigo', 'pink', 'red', 'teal', 'orange'
        ].includes(value);
      }
    },
    actions: {
      type: Array as PropType<ModuleAction[]>,
      required: true,
      validator: (actions: ModuleAction[]) => {
        return actions.length > 0 && actions.length <= 2;
      }
    }
  },
  
  setup() {
    return {};
  }
});
</script>
