<!--
  Paksa Financial System - Data Table Component
  Copyright (c) 2025 Paksa IT Solutions. All rights reserved.
-->
<template>
  <DataTable
    :value="data"
    :loading="loading"
    :paginator="paginator"
    :rows="rows"
    :totalRecords="totalRecords"
    :lazy="lazy"
    @page="onPage"
    @sort="onSort"
    @filter="onFilter"
    :filters="filters"
    filterDisplay="row"
    :globalFilterFields="globalFilterFields"
    responsiveLayout="scroll"
    :rowHover="true"
    :stripedRows="true"
    :showGridlines="showGridlines"
  >
    <template #header>
      <div class="table-header">
        <h3 v-if="title">{{ title }}</h3>
        <div class="header-actions">
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText v-model="globalFilter" placeholder="Search..." @input="onGlobalFilter" />
          </span>
          <Button v-if="showExport" icon="pi pi-download" label="Export" @click="exportData" />
          <Button v-if="showAdd" icon="pi pi-plus" label="Add" @click="$emit('add')" />
        </div>
      </div>
    </template>

    <Column v-if="selectionMode" selectionMode="multiple" style="width: 3rem" />
    
    <Column
      v-for="col in columns"
      :key="col.field"
      :field="col.field"
      :header="col.header"
      :sortable="col.sortable !== false"
      :filterMatchMode="col.filterMatchMode || 'contains'"
    >
      <template #body="{ data }" v-if="col.template">
        <slot :name="`body-${col.field}`" :data="data" />
      </template>
    </Column>

    <Column v-if="showActions" header="Actions" :exportable="false">
      <template #body="{ data }">
        <Button icon="pi pi-pencil" text @click="$emit('edit', data)" />
        <Button icon="pi pi-trash" text severity="danger" @click="$emit('delete', data)" />
      </template>
    </Column>
  </DataTable>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface Column {
  field: string;
  header: string;
  sortable?: boolean;
  filterMatchMode?: string;
  template?: boolean;
}

interface Props {
  data: any[];
  columns: Column[];
  loading?: boolean;
  paginator?: boolean;
  rows?: number;
  totalRecords?: number;
  lazy?: boolean;
  title?: string;
  showExport?: boolean;
  showAdd?: boolean;
  showActions?: boolean;
  selectionMode?: boolean;
  globalFilterFields?: string[];
  showGridlines?: boolean;
}

withDefaults(defineProps<Props>(), {
  loading: false,
  paginator: true,
  rows: 10,
  lazy: false,
  showExport: true,
  showAdd: true,
  showActions: true,
  selectionMode: false,
  showGridlines: false
});

const emit = defineEmits(['page', 'sort', 'filter', 'add', 'edit', 'delete', 'export']);

const globalFilter = ref('');
const filters = ref({});

const onPage = (event: any) => emit('page', event);
const onSort = (event: any) => emit('sort', event);
const onFilter = (event: any) => emit('filter', event);
const onGlobalFilter = () => emit('filter', { global: globalFilter.value });
const exportData = () => emit('export');
</script>

<style scoped>
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}
</style>
