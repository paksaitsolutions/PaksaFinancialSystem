<template>
  <v-btn
    v-bind="$attrs"
    :data-shortcut="shortcut"
    @click="handleClick"
  >
    <slot />
    <v-tooltip
      v-if="showTooltip && shortcutText"
      activator="parent"
      location="bottom"
    >
      {{ tooltipText }}
    </v-tooltip>
  </v-btn>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  shortcut: {
    type: String,
    default: ''
  },
  shortcutKey: {
    type: String,
    default: ''
  },
  showTooltip: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])

const shortcutText = computed(() => {
  if (!props.shortcutKey) return ''
  
  const parts = props.shortcutKey.split('+')
  return parts.map(part => {
    switch (part.toLowerCase()) {
      case 'ctrl': return 'Ctrl'
      case 'alt': return 'Alt'
      case 'shift': return 'Shift'
      case 'meta': return 'Cmd'
      default: return part.toUpperCase()
    }
  }).join('+')
})

const tooltipText = computed(() => {
  const slot = document.querySelector(`[data-shortcut="${props.shortcut}"]`)?.textContent?.trim()
  return shortcutText.value ? `${slot} (${shortcutText.value})` : slot
})

const handleClick = (event) => {
  emit('click', event)
}
</script>