<template>
  <div class="regions-view">
    <div class="page-header">
      <h1>Region Management</h1>
      <Button label="Add Region" icon="pi pi-plus" @click="showAddDialog = true" />
    </div>

    <Card>
      <template #title>Regions</template>
      <template #content>
        <DataTable :value="regions" :loading="loading" paginator :rows="10" dataKey="id">
          <Column field="code" header="Code" sortable />
          <Column field="name" header="Name" sortable />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status ? 'Active' : 'Inactive'" :severity="data.status ? 'success' : 'danger'" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button icon="pi pi-pencil" size="small" @click="editRegion(data)" />
                <Button icon="pi pi-trash" size="small" severity="danger" @click="deleteRegion(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="showAddDialog" modal header="Add Region" :style="{ width: '25rem' }">
      <div class="grid">
        <div class="col-12">
          <label>Region Code</label>
          <InputText v-model="newRegion.code" class="w-full" placeholder="NA" />
        </div>
        <div class="col-12">
          <label>Region Name</label>
          <InputText v-model="newRegion.name" class="w-full" placeholder="North America" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showAddDialog = false" />
        <Button label="Add Region" @click="addRegion" :loading="saving" />
      </template>
    </Dialog>

    <Dialog v-model:visible="showEditDialog" modal header="Edit Region" :style="{ width: '25rem' }">
      <div class="grid">
        <div class="col-12">
          <label>Region Code</label>
          <InputText v-model="editedRegion.code" class="w-full" disabled />
        </div>
        <div class="col-12">
          <label>Region Name</label>
          <InputText v-model="editedRegion.name" class="w-full" />
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox id="regionActive" v-model="editedRegion.status" :binary="true" />
            <label for="regionActive">Active</label>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showEditDialog = false" />
        <Button label="Update Region" @click="updateRegion" :loading="saving" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { regionService, type Region } from '@/api/regionService'

const toast = useToast()
const confirm = useConfirm()

const loading = ref(false)
const saving = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)

const regions = ref<Region[]>([])

const newRegion = ref({
  code: '',
  name: ''
})

const editedRegion = ref({
  id: '',
  code: '',
  name: '',
  status: true
})

const loadRegions = async () => {
  loading.value = true
  try {
    regions.value = await regionService.getRegions(true)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load regions' })
  } finally {
    loading.value = false
  }
}

const editRegion = (region: Region) => {
  editedRegion.value = { ...region }
  showEditDialog.value = true
}

const addRegion = async () => {
  saving.value = true
  try {
    await regionService.createRegion({ ...newRegion.value, status: true })
    toast.add({ severity: 'success', summary: 'Success', detail: 'Region added successfully' })
    showAddDialog.value = false
    newRegion.value = { code: '', name: '' }
    await loadRegions()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to add region' })
  } finally {
    saving.value = false
  }
}

const updateRegion = async () => {
  saving.value = true
  try {
    await regionService.updateRegion(editedRegion.value.id, editedRegion.value)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Region updated successfully' })
    showEditDialog.value = false
    await loadRegions()
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to update region' })
  } finally {
    saving.value = false
  }
}

const deleteRegion = (region: Region) => {
  confirm.require({
    message: `Are you sure you want to delete region "${region.name}"?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try {
        await regionService.deleteRegion(region.id)
        toast.add({ severity: 'success', summary: 'Success', detail: 'Region deleted successfully' })
        await loadRegions()
      } catch (error) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete region' })
      }
    }
  })
}

onMounted(() => {
  loadRegions()
})
</script>

<style scoped>
.regions-view {
  padding: 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
</style>