<template>
  <div class="virtual-list" :style="{ height: containerHeight + 'px' }">
    <div class="virtual-list-phantom" :style="{ height: totalHeight + 'px' }"></div>
    <div class="virtual-list-content" :style="{ transform: `translateY(${offsetY}px)` }">
      <div
        v-for="item in visibleItems"
        :key="item.index"
        class="virtual-list-item"
        :style="{ height: itemHeight + 'px' }"
      >
        <slot :item="item.data" :index="item.index"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  items: any[]
  itemHeight: number
  containerHeight: number
  bufferSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  bufferSize: 5
})

const scrollTop = ref(0)

const totalHeight = computed(() => props.items.length * props.itemHeight)

const visibleCount = computed(() => Math.ceil(props.containerHeight / props.itemHeight))

const startIndex = computed(() => {
  const index = Math.floor(scrollTop.value / props.itemHeight)
  return Math.max(0, index - props.bufferSize)
})

const endIndex = computed(() => {
  const index = startIndex.value + visibleCount.value
  return Math.min(props.items.length, index + props.bufferSize)
})

const visibleItems = computed(() => {
  const items = []
  for (let i = startIndex.value; i < endIndex.value; i++) {
    items.push({
      index: i,
      data: props.items[i]
    })
  }
  return items
})

const offsetY = computed(() => startIndex.value * props.itemHeight)

const handleScroll = (e: Event) => {
  scrollTop.value = (e.target as HTMLElement).scrollTop
}

onMounted(() => {
  const container = document.querySelector('.virtual-list')
  container?.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  const container = document.querySelector('.virtual-list')
  container?.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.virtual-list {
  overflow-y: auto;
  position: relative;
}

.virtual-list-phantom {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  z-index: -1;
}

.virtual-list-content {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}

.virtual-list-item {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #eee;
}
</style>