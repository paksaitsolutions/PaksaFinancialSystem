<template>
  <div class="data-table">
    <div class="data-table__header">
      <slot name="header">
        <div class="data-table__title" v-if="title">{{ title }}</div>
      </slot>
    </div>
    
    <div class="data-table__toolbar">
      <slot name="toolbar"></slot>
    </div>
    
    <div class="data-table__content">
      <table class="data-table__table">
        <thead>
          <tr>
            <th 
              v-for="header in headers" 
              :key="header.key"
              @click="handleSort(header.key)"
              :class="{ 'sortable': header.sortable, 'active': sortBy === header.key }"
            >
              {{ header.title }}
              <span v-if="header.sortable" class="sort-icon">
                {{ sortBy === header.key ? (sortDesc ? '▼' : '▲') : '↕' }}
              </span>
            </th>
            <th v-if="hasActions">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="headers.length + (hasActions ? 1 : 0)" class="loading-cell">
              Loading...
            </td>
          </tr>
          <tr v-else-if="!items.length">
            <td :colspan="headers.length + (hasActions ? 1 : 0)" class="empty-cell">
              No items found
            </td>
          </tr>
          <tr v-else v-for="(item, index) in paginatedItems" :key="item.id || index">
            <td v-for="header in headers" :key="header.key">
              <slot :name="`item.${header.key}`" :item="item">
                {{ item[header.key] }}
              </slot>
            </td>
            <td v-if="hasActions" class="actions-cell">
              <slot name="item.actions" :item="item"></slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div class="data-table__pagination">
      <div class="pagination-info">
        Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to 
        {{ Math.min(currentPage * itemsPerPage, items.length) }} of {{ items.length }} entries
      </div>
      <div class="pagination-controls">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="pagination-button"
        >
          Previous
        </button>
        <span class="pagination-page">Page {{ currentPage }} of {{ totalPages }}</span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage >= totalPages"
          class="pagination-button"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref, watch } from 'vue';

export interface DataTableHeader {
  key: string;
  title: string;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

export default defineComponent({
  name: 'DataTable',
  
  props: {
    headers: {
      type: Array as () => DataTableHeader[],
      required: true,
    },
    items: {
      type: Array as () => any[],
      required: true,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    itemsPerPage: {
      type: Number,
      default: 10,
    },
    title: {
      type: String,
      default: '',
    },
  },
  
  emits: ['sort', 'update:items-per-page', 'update:page'],
  
  setup(props, { slots, emit }) {
    const currentPage = ref(1);
    const sortBy = ref('');
    const sortDesc = ref(false);
    
    const hasActions = computed(() => !!slots['item.actions']);
    
    const totalPages = computed(() => {
      return Math.ceil(props.items.length / props.itemsPerPage);
    });
    
    const paginatedItems = computed(() => {
      const start = (currentPage.value - 1) * props.itemsPerPage;
      const end = start + props.itemsPerPage;
      return [...props.items].slice(start, end);
    });
    
    const handleSort = (key: string) => {
      const header = props.headers.find(h => h.key === key);
      if (!header?.sortable) return;
      
      if (sortBy.value === key) {
        sortDesc.value = !sortDesc.value;
      } else {
        sortBy.value = key;
        sortDesc.value = false;
      }
      
      emit('sort', { sortBy: sortBy.value, sortDesc: sortDesc.value });
    };
    
    watch(() => props.items, () => {
      // Reset to first page when items change
      currentPage.value = 1;
    });
    
    return {
      currentPage,
      sortBy,
      sortDesc,
      hasActions,
      totalPages,
      paginatedItems,
      handleSort,
    };
  },
});
</script>

<style scoped>
.data-table {
  width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.data-table__header {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f5f5f5;
}

.data-table__title {
  font-size: 1.25rem;
  font-weight: 500;
}

.data-table__toolbar {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fafafa;
}

.data-table__content {
  overflow-x: auto;
}

.data-table__table {
  width: 100%;
  border-collapse: collapse;
}

.data-table__table th,
.data-table__table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.data-table__table th {
  background-color: #f5f5f5;
  font-weight: 500;
  white-space: nowrap;
}

.data-table__table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table__table th.sortable:hover {
  background-color: #eeeeee;
}

.data-table__table th.active {
  background-color: #e0e0e0;
}

.sort-icon {
  margin-left: 4px;
  font-size: 0.8em;
}

.loading-cell,
.empty-cell {
  text-align: center;
  padding: 24px !important;
  color: #757575;
}

.actions-cell {
  white-space: nowrap;
  text-align: right;
}

.data-table__pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-top: 1px solid #e0e0e0;
  background-color: #fafafa;
}

.pagination-info {
  color: #757575;
  font-size: 0.875rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-button {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  background-color: white;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background-color: #f5f5f5;
}

.pagination-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.pagination-page {
  margin: 0 8px;
  font-size: 0.875rem;
}
</style>
