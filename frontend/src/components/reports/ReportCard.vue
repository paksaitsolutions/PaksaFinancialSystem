<template>
  <Card class="report-card h-full" :pt="{
    root: { class: 'h-full flex flex-column' },
    body: { class: 'flex-grow-1' },
    content: { class: 'h-full flex flex-column' }
  }">
    <template #header>
      <div class="flex justify-content-between align-items-center p-3 border-bottom-1 surface-border">
        <div class="flex align-items-center gap-2">
          <i :class="[report.icon, 'text-primary text-xl']"></i>
          <span class="font-semibold text-lg">{{ report.name }}</span>
        </div>
        <Button 
          icon="pi pi-star-fill" 
          class="p-button-text p-button-rounded p-button-plain" 
          :class="{ 'text-yellow-500': isFavorite }"
          @click.stop="$emit('favorite')"
          v-tooltip.top="isFavorite ? 'Remove from favorites' : 'Add to favorites'"
        />
      </div>
    </template>
    
    <div class="p-3 flex-grow-1 flex flex-column">
      <p class="text-color-secondary line-height-3 mb-3 flex-grow-1">{{ report.description }}</p>
      
      <div v-if="report.lastRun" class="text-sm text-500 mb-3">
        <i class="pi pi-clock mr-1"></i>
        Last run: {{ formatDate(report.lastRun) }}
      </div>
      
      <div v-if="report.tags && report.tags.length > 0" class="flex flex-wrap gap-1 mb-3">
        <Chip 
          v-for="tag in report.tags.slice(0, 3)" 
          :key="tag" 
          :label="tag" 
          class="text-xs"
        />
        <Chip 
          v-if="report.tags.length > 3" 
          :label="`+${report.tags.length - 3}`" 
          class="text-xs"
        />
      </div>
    </div>
    
    <template #footer>
      <div class="flex justify-content-between align-items-center p-3 border-top-1 surface-border">
        <Button 
          label="Run Report" 
          icon="pi pi-play" 
          class="p-button-sm p-button-outlined"
          @click="$emit('run')"
        />
        <Button 
          icon="pi pi-ellipsis-v" 
          class="p-button-text p-button-sm p-button-rounded"
          @click="toggleMenu"
          v-tooltip.top="'More options'"
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
  </Card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import type { MenuItem } from 'vue/menuitem';

const props = defineProps<{
  report: {
    id: string;
    name: string;
    description: string;
    icon: string;
    category: string;
    lastRun?: string;
    tags?: string[];
  };
  isFavorite: boolean;
}>();

const emit = defineEmits(['favorite', 'run']);
const router = useRouter();
const toast = useToast();
const menu = ref();

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const toggleMenu = (event: Event) => {
  menu.value.toggle(event);
};

const menuItems = computed<MenuItem[]>(() => [
  {
    label: 'Schedule',
    icon: 'pi pi-calendar',
    command: () => {
      toast.add({ 
        severity: 'info', 
        summary: 'Schedule Report', 
        detail: `Scheduling ${props.report.name}`, 
        life: 3000 
      });
    }
  },
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
    label: 'Edit',
    icon: 'pi pi-pencil',
    command: () => {
      router.push({ name: 'ReportBuilder', params: { id: props.report.id } });
    }
  },
  { separator: true },
  {
    label: 'Duplicate',
    icon: 'pi pi-copy',
    command: () => {
      toast.add({ 
        severity: 'success', 
        summary: 'Duplicate', 
        detail: `Creating a copy of ${props.report.name}`, 
        life: 3000 
      });
    }
  },
  {
    label: 'Share',
    icon: 'pi pi-share-alt',
    command: () => {
      toast.add({ 
        severity: 'info', 
        summary: 'Share', 
        detail: `Sharing options for ${props.report.name}`, 
        life: 3000 
      });
    }
  },
  { separator: true },
  {
    label: 'Delete',
    icon: 'pi pi-trash',
    class: 'text-red-500',
    command: () => {
      toast.add({ 
        severity: 'warn', 
        summary: 'Delete', 
        detail: `Are you sure you want to delete ${props.report.name}?`, 
        life: 3000 
      });
    }
  }
]);

const exportReport = (format: string) => {
  toast.add({ 
    severity: 'success', 
    summary: 'Export', 
    detail: `Exporting ${props.report.name} as ${format.toUpperCase()}`, 
    life: 3000 
  });
};
</script>

<style scoped>
.report-card {
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  overflow: hidden;
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

:deep(.p-card-body) {
  display: flex;
  flex-direction: column;
  height: 100%;
}

:deep(.p-card-content) {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
