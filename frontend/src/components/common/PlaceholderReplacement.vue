<template>
  <div class="placeholder-replacement">
    <div class="content">
      <i :class="icon" class="feature-icon"></i>
      <h2>{{ title }}</h2>
      <p>{{ description }}</p>
      <div v-if="showComingSoon" class="coming-soon">
        <Tag value="Coming Soon" severity="info" />
      </div>
      <div v-if="actions.length > 0" class="actions">
        <Button 
          v-for="action in actions" 
          :key="action.label"
          :label="action.label"
          :icon="action.icon"
          :class="action.class"
          @click="action.handler"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Action {
  label: string;
  icon?: string;
  class?: string;
  handler: () => void;
}

interface Props {
  title: string;
  description: string;
  icon?: string;
  showComingSoon?: boolean;
  actions?: Action[];
}

withDefaults(defineProps<Props>(), {
  icon: 'pi pi-cog',
  showComingSoon: true,
  actions: () => []
});
</script>

<style scoped>
.placeholder-replacement {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 2rem;
  background: var(--surface-ground);
}

.content {
  text-align: center;
  max-width: 500px;
}

.feature-icon {
  font-size: 4rem;
  color: var(--primary-color);
  margin-bottom: 1.5rem;
}

.content h2 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
  font-size: 1.5rem;
}

.content p {
  margin: 0 0 2rem 0;
  color: var(--text-color-secondary);
  line-height: 1.6;
}

.coming-soon {
  margin-bottom: 2rem;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}
</style>