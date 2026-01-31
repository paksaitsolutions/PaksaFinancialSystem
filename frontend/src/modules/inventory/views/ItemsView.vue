<template>
  <div class="inventory-items-view">
    <div v-if="!showForm">
      <InventoryList @create="showCreateForm" @view="viewItem" />
    </div>
    <div v-else>
      <ItemForm :item="selectedItem" @save="handleSave" @cancel="hideForm" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const showForm = ref(false)
const selectedItem = ref(null)

const showCreateForm = () => {
  selectedItem.value = null
  showForm.value = true
}

const viewItem = (item) => {
  selectedItem.value = item
  showForm.value = true
}

const handleSave = (itemData) => {
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: selectedItem.value ? 'Item updated successfully' : 'Item created successfully'
  })
  hideForm()
}

const hideForm = () => {
  showForm.value = false
  selectedItem.value = null
}
</script>

<style scoped>
.inventory-items-view {
  padding: 1rem;
}

@media (max-width: 768px) {
  .inventory-items-view {
    padding: 0.5rem;
  }
}
</style>