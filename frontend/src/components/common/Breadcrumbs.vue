<template>
  <v-breadcrumbs :items="breadcrumbs" class="pa-0">
    <template v-slot:item="{ item }">
      <v-breadcrumbs-item
        :to="item.to"
        :disabled="item.disabled"
      >
        {{ item.title }}
      </v-breadcrumbs-item>
    </template>
  </v-breadcrumbs>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.breadcrumb)
  
  return matched.map((item, index) => ({
    title: item.meta.breadcrumb,
    to: index === matched.length - 1 ? undefined : item.path,
    disabled: index === matched.length - 1
  }))
})
</script>