<template>
  <div class="placeholder-view">
    <Card>
      <template #content>
        <div class="text-center p-6">
          <i class="pi pi-cog text-6xl text-gray-400 mb-4"></i>
          <h2 class="text-2xl font-semibold mb-2">{{ title }}</h2>
          <p class="text-gray-600 mb-4">{{ description }}</p>
          <Button label="Go Back" icon="pi pi-arrow-left" @click="$router.go(-1)" />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  description?: string
}

withDefaults(defineProps<Props>(), {
  title: 'Coming Soon',
  description: 'This feature is under development and will be available soon.'
})
</script>

<style scoped>
.placeholder-view {
  padding: 2rem;
  max-width: 600px;
  margin: 0 auto;
}
</style>