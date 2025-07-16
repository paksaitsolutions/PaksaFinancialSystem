<template>
  <Card class="h-full flex flex-column">
    <template #header>
      <div class="flex justify-content-between align-items-center p-3 pb-0">
        <div class="flex align-items-center gap-2">
          <i :class="['pi', report.icon || 'pi-file', 'text-primary text-xl']" />
          <span class="font-medium">{{ report.name }}</span>
        </div>
        <Button 
          icon="pi pi-ellipsis-v" 
          class="p-button-text p-button-rounded p-button-plain"
          @click="toggleMenu"
          aria-haspopup="true"
          aria-controls="overlay_menu"
        />
        <Menu 
          id="overlay_menu" 
          ref="menu" 
          :model="menuItems" 
          :popup="true"
        />
      </div>
    </template>
    
    <template #content>
      <div class="text-500 text-sm mb-3 line-clamp-2" style="min-height: 2.5rem;">
        {{ report.description || 'No description provided' }}
      </div>
      
      <div class="flex flex-wrap gap-2 mb-3">
        <Tag :value="reportType" class="text-xs" />
        <Tag :value="reportCategory" :severity="categorySeverity" class="text-xs" />
      </div>
      
      <div v-if="report.tags && report.tags.length > 0" class="flex flex-wrap gap-1 mb-3">
        <Chip 
          v-for="(tag, index) in report.tags.slice(0, 3)" 
          :key="index" 
          :label="tag" 
          class="text-xs"
        />
        <Chip 
          v-if="report.tags.length > 3" 
          :label="`+${report.tags.length - 3}`" 
          class="text-xs"
        />
      </div>
      
      <div class="text-500 text-sm mt-auto">
        <div class="flex justify-content-between">
          <span>Last Run</span>
          <span class="font-medium">{{ lastRun }}</span>
        </div>
      </div>
    </template>
    
    <template #footer>
      <div class="flex justify-content-between align-items-center">
        <Button 
          icon="pi pi-play" 
          label="Run" 
          class="p-button-sm p-button-text"
          @click="$emit('run', report)"
        />
        <div class="flex gap-1">
          <Button 
            :icon="isFavorite ? 'pi pi-star-fill' : 'pi pi-star'" 
            :class="['p-button-rounded p-button-text p-button-sm', { 'p-button-warning': isFavorite }]"
            @click="$emit('favorite', report.id)"
            v-tooltip.top="isFavorite ? 'Remove from Favorites' : 'Add to Favorites'"
          />
          <Button 
            icon="pi pi-pencil" 
            class="p-button-rounded p-button-text p-button-sm"
            @click="$emit('edit', report)"
            v-tooltip.top="'Edit Report'"
          />
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useConfirm } from 'primevue/useconfirm';
import type { MenuItem } from 'primevue/menuitem';
import type { Report } from '@/types/reports';

const props = defineProps<{
  report: Report;
  isFavorite: boolean;
}>();

const emit = defineEmits<{
  (e: 'favorite', id: string): void;
  (e: 'run', report: Report): void;
  (e: 'edit', report: Report): void;
  (e: 'delete', report: Report): void;
}>();

const confirm = useConfirm();
const menu = ref();

// Computed
const reportType = computed(() => {
  if (!props.report.type) return 'Unknown';
  return props.report.type.charAt(0).toUpperCase() + props.report.type.slice(1);
});

const reportCategory = computed(() => {
  // This should come from a store or props
  const categories: Record<string, string> = {
    'financial': 'Financial',
    'operational': 'Operational',
    'sales': 'Sales',
    'inventory': 'Inventory',
    'hr': 'HR',
  };
  return props.report.categoryId ? categories[props.report.categoryId] || 'Uncategorized' : 'Uncategorized';
});

const categorySeverity = computed(() => {
  const severities: Record<string, string> = {
    'financial': 'success',
    'operational': 'info',
    'sales': 'warning',
    'inventory': 'danger',
    'hr': 'help',
  };
  return props.report.categoryId ? severities[props.report.categoryId] || 'info' : 'info';
});

const lastRun = computed(() => {
  if (!props.report.lastRun) return 'Never';
  const date = new Date(props.report.lastRun);
  return date.toLocaleDateString();
});

const menuItems = computed<MenuItem[]>(() => [
  {
    label: 'Run',
    icon: 'pi pi-play',
    command: () => emit('run', props.report)
  },
  {
    label: isFavorite.value ? 'Remove from Favorites' : 'Add to Favorites',
    icon: isFavorite.value ? 'pi pi-star-fill' : 'pi pi-star',
    command: () => emit('favorite', props.report.id)
  },
  { separator: true },
  {
    label: 'Edit',
    icon: 'pi pi-pencil',
    command: () => emit('edit', props.report)
  },
  {
    label: 'Duplicate',
    icon: 'pi pi-copy',
    command: () => duplicateReport()
  },
  { separator: true },
  {
    label: 'Export',
    icon: 'pi pi-download',
    items: [
      { label: 'PDF', icon: 'pi pi-file-pdf', command: () => exportReport('pdf') },
      { label: 'Excel', icon: 'pi pi-file-excel', command: () => exportReport('excel') },
      { label: 'CSV', icon: 'pi pi-file', command: () => exportReport('csv') }
    ]
  },
  {
    label: 'Schedule',
    icon: 'pi pi-calendar',
    command: () => scheduleReport()
  },
  { separator: true },
  {
    label: 'Delete',
    icon: 'pi pi-trash',
    class: 'text-red-500',
    command: () => confirmDelete()
  }
]);

// Methods
const toggleMenu = (event: Event) => {
  menu.value.toggle(event);
};

const confirmDelete = () => {
  emit('delete', props.report);
};

const duplicateReport = () => {
  // Implementation would go here
  console.log('Duplicate report:', props.report.id);
};

const exportReport = (format: string) => {
  // Implementation would go here
  console.log(`Exporting report ${props.report.id} as ${format}`);
};

const scheduleReport = () => {
  // Implementation would go here
  console.log('Scheduling report:', props.report.id);
};
</script>

<style scoped>
:deep(.p-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.p-card-content) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
