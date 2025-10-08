<template>
  <div class="role-management p-4">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Role Management</h1>
        <Breadcrumb :home="home" :model="breadcrumbItems" />
      </div>
      <div class="flex gap-2">
        <Button 
          label="New Role" 
          icon="pi pi-plus" 
          @click="openRoleDialog()"
          class="p-button-sm"
        />
        <Button 
          label="Initialize RBAC" 
          icon="pi pi-cog" 
          @click="initializeRBAC"
          class="p-button-secondary p-button-sm"
        />
      </div>
    </div>
    
    <Card>
      <template #content>
        <DataTable 
          :value="roles" 
          :loading="loading"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[5,10,25,50]"
          class="p-datatable-sm"
          :globalFilterFields="['name', 'code']"
          responsiveLayout="scroll"
        >
          <template #header>
            <div class="flex justify-content-between">
              <span class="p-input-icon-left">
                <i class="pi pi-search" />
                <InputText v-model="filters['global'].value" placeholder="Search..." class="w-full" />
              </span>
            </div>
          </template>
          
          <Column field="name" header="Name" :sortable="true">
            <template #body="{ data }">
              <span class="font-medium">{{ data.name }}</span>
            </template>
          </Column>
          
          <Column field="code" header="Code" :sortable="true"></Column>
          
          <Column field="is_active" header="Status" :sortable="true" style="width: 120px">
            <template #body="{ data }">
              <Tag 
                :value="data.is_active ? 'ACTIVE' : 'INACTIVE'" 
                :severity="data.is_active ? 'success' : 'danger'"
                class="text-xs"
              />
            </template>
          </Column>
          
          <Column header="Actions" style="width: 100px">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-text p-button-sm p-button-rounded" 
                  @click="viewRole(data)"
                  v-tooltip.top="'View Role'"
                />
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-sm p-button-rounded p-button-warning" 
                  @click="editRole(data)"
                  v-tooltip.top="'Edit Role'"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-rounded p-button-danger" 
                  @click="confirmDeleteRole(data)"
                  v-tooltip.top="'Delete Role'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
    
    <!-- Role Dialog -->
    <Dialog 
      v-model:visible="roleDialog" 
      :header="editMode ? (viewMode ? 'View Role' : 'Edit Role') : 'New Role'"
      :modal="true"
      :style="{ width: '800px' }"
      :closable="!saving"
    >
      <form @submit.prevent="saveRole" class="p-fluid">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="name">Role Name <span class="text-red-500">*</span></label>
              <InputText
                id="name"
                v-model="editedRole.name"
                required
                :class="{ 'p-invalid': !editedRole.name && submitted }"
              />
              <small v-if="!editedRole.name && submitted" class="p-error">Name is required</small>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="code">Role Code <span class="text-red-500">*</span></label>
              <InputText
                id="code"
                v-model="editedRole.code"
                required
                :class="{ 'p-invalid': !editedRole.code && submitted }"
              />
              <small v-if="!editedRole.code && submitted" class="p-error">Code is required</small>
            </div>
          </div>
          
          <div class="col-12">
            <div class="field">
              <label for="description">Description</label>
              <Textarea
                id="description"
                v-model="editedRole.description"
                rows="2"
                autoResize
              />
            </div>
          </div>
          
          <div class="col-12">
            <div class="field-checkbox">
              <Checkbox
                id="is_active"
                v-model="editedRole.is_active"
                :binary="true"
              />
              <label for="is_active">Active</label>
            </div>
          </div>
        </div>
      </form>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          @click="closeRoleDialog" 
          class="p-button-text"
          :disabled="saving"
        />
        <Button 
          v-if="!viewMode"
          label="Save" 
          icon="pi pi-check" 
          @click="saveRole" 
          :loading="saving"
          autofocus
        />
        <Button 
          v-else
          label="Edit" 
          icon="pi pi-pencil" 
          @click="editMode = true; viewMode = false" 
          class="p-button-warning"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { FilterMatchMode } from 'primevue/api'

const confirm = useConfirm()
const toast = useToast()

const home = ref({ icon: 'pi pi-home', to: '/' })
const breadcrumbItems = ref([
  { label: 'RBAC', to: '/rbac' },
  { label: 'Roles' }
])

// State
const loading = ref(false)
const saving = ref(false)
const roleDialog = ref(false)
const editMode = ref(false)
const viewMode = ref(false)
const submitted = ref(false)
const roles = ref([])
const selectedRole = ref(null)

// Filters
const filters = reactive({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
})

// Form data
const editedRole = ref({
  id: null,
  name: '',
  code: '',
  description: '',
  is_active: true
})

const defaultRole = () => ({
  id: null,
  name: '',
  code: '',
  description: '',
  is_active: true
})

const fetchRoles = async () => {
  loading.value = true
  try {
    // Mock data
    roles.value = [
      { id: 1, name: 'Administrator', code: 'admin', description: 'Full system access', is_active: true },
      { id: 2, name: 'Manager', code: 'manager', description: 'Management access', is_active: true },
      { id: 3, name: 'User', code: 'user', description: 'Basic user access', is_active: true }
    ]
  } catch (error) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to fetch roles',
      life: 3000 
    })
  } finally {
    loading.value = false
  }
}

const saveRole = async () => {
  submitted.value = true
  
  if (!editedRole.value.name || !editedRole.value.code) {
    return
  }
  
  saving.value = true
  
  try {
    if (editMode.value) {
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Role updated successfully',
        life: 3000 
      })
    } else {
      editedRole.value.id = Date.now()
      roles.value.unshift({ ...editedRole.value })
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Role created successfully',
        life: 3000 
      })
    }
    
    closeRoleDialog()
  } catch (error) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to save role',
      life: 3000 
    })
  } finally {
    saving.value = false
  }
}

const openRoleDialog = (role = null) => {
  if (role) {
    editedRole.value = { ...role }
    editMode.value = true
    viewMode.value = true
  } else {
    editedRole.value = defaultRole()
    editMode.value = false
    viewMode.value = false
  }
  submitted.value = false
  roleDialog.value = true
}

const closeRoleDialog = () => {
  roleDialog.value = false
  viewMode.value = false
  setTimeout(() => {
    editedRole.value = defaultRole()
    submitted.value = false
  }, 300)
}

const viewRole = (role) => {
  editedRole.value = { ...role }
  editMode.value = true
  viewMode.value = true
  roleDialog.value = true
}

const editRole = (role) => {
  editedRole.value = { ...role }
  editMode.value = true
  viewMode.value = false
  roleDialog.value = true
}

const confirmDeleteRole = (role) => {
  selectedRole.value = role
  confirm.require({
    message: `Are you sure you want to delete ${role.name}?`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: deleteRole
  })
}

const deleteRole = async () => {
  if (!selectedRole.value) return
  
  try {
    roles.value = roles.value.filter(r => r.id !== selectedRole.value.id)
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Role deleted successfully',
      life: 3000 
    })
  } catch (error) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to delete role',
      life: 3000 
    })
  } finally {
    selectedRole.value = null
  }
}

const initializeRBAC = async () => {
  try {
    loading.value = true
    await fetchRoles()
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'RBAC initialized successfully',
      life: 3000 
    })
  } catch (error) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to initialize RBAC',
      life: 3000 
    })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRoles()
})
</script>