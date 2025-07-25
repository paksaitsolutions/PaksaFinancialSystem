<template>
  <div class="mobile-data-table">
    <v-data-table
      v-if="!isMobile"
      :headers="headers"
      :items="items"
      :loading="loading"
      v-bind="$attrs"
    >
      <template v-for="(_, slot) of $slots" v-slot:[slot]="scope">
        <slot :name="slot" v-bind="scope" />
      </template>
    </v-data-table>
    
    <div v-else class="mobile-cards">
      <v-skeleton-loader
        v-if="loading"
        v-for="n in 3"
        :key="n"
        type="card"
        class="mb-2"
      />
      
      <v-card
        v-else
        v-for="(item, index) in items"
        :key="index"
        class="mb-2 mobile-card"
        @click="$emit('click:row', { item, index })"
      >
        <v-card-text>
          <div
            v-for="header in visibleHeaders"
            :key="header.key"
            class="mobile-field"
          >
            <span class="field-label">{{ header.title }}:</span>
            <span class="field-value">
              <slot
                v-if="$slots[`item.${header.key}`]"
                :name="`item.${header.key}`"
                :item="item"
                :value="item[header.key]"
              />
              <span v-else>{{ item[header.key] }}</span>
            </span>
          </div>
          
          <div v-if="$slots.actions" class="mobile-actions mt-2">
            <slot name="actions" :item="item" :index="index" />
          </div>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useMobile } from '@/composables/useMobile'

const props = defineProps({
  headers: Array,
  items: Array,
  loading: Boolean,
  mobileFields: {
    type: Array,
    default: () => []
  }
})

defineEmits(['click:row'])

const { isMobile } = useMobile()

const visibleHeaders = computed(() => {
  if (props.mobileFields.length > 0) {
    return props.headers.filter(h => props.mobileFields.includes(h.key))
  }
  return props.headers.filter(h => !h.hideOnMobile)
})
</script>

<style scoped>
.mobile-field {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid #f0f0f0;
}

.field-label {
  font-weight: 500;
  color: #666;
  min-width: 100px;
}

.field-value {
  flex: 1;
  text-align: right;
}

.mobile-card {
  cursor: pointer;
}
</style>