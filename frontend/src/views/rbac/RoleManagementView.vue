<template>
  <AppLayout title="User Management - Roles">
    <div class="card">
      <div class="flex justify-content-between align-items-center mb-4">
        <h2>Role Management</h2>
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
      
      <div class="card">
        <DataTable 
          :value="roles" 
          :loading="loading"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[5,10,25,50]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Showing {first} to {last} of {totalRecords} roles"
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
          
          <Column field="permissions" header="Permissions">
            <template #body="{ data }">
              <div class="flex flex-wrap gap-1">
                <Chip 
                  v-for="permission in data.permissions.slice(0, 3)"
                  :key="permission.id"
                  :label="permission.code"
                  class="text-xs"
                />
                <Chip 
                  v-if="data.permissions.length > 3"
                  :label="'+' + (data.permissions.length - 3) + ' more'"
                  class="text-xs"
                />
              </div>
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
      </div>
    </div>
    
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
          
          <div class="col-12">
            <h4 class="mb-4">Permissions</h4>
            <div class="grid">
              <div 
                v-for="permission in permissions"
                :key="permission.id"
                class="col-12 md:col-4"
              >
                <div class="field-checkbox">
                  <Checkbox
                    :id="'perm_' + permission.id"
                    :value="permission.id"
                    v-model="editedRole.permission_ids"
                  />
                  <label :for="'perm_' + permission.id">{{ permission.name }}</label>
                </div>
              </div>
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
    
    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deleteDialog" 
      header="Confirm Delete" 
      :modal="true"
      :style="{ width: '450px' }"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="selectedRole">
          Are you sure you want to delete <b>{{ selectedRole.name }}</b>?
        </span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          @click="deleteDialog = false" 
          class="p-button-text"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          @click="deleteRole" 
          class="p-button-danger"
          autofocus
        />
      </template>
    </Dialog>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import AppLayout from '@/layouts/AppLayout.vue'
import { FilterMatchMode } from 'primevue/api'
import roleService from '@/services/roleService'

const confirm = useConfirm()
const toast = useToast()

// State
const loading = ref(false)
const saving = ref(false)
const roleDialog = ref(false)
const deleteDialog = ref(false)
const editMode = ref(false)
const viewMode = ref(false)
const submitted = ref(false)
const roles = ref([])
const permissions = ref([])
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
  is_active: true,
  permission_ids: []
})

const defaultRole = () => ({
  id: null,
  name: '',
  code: '',
  description: '',
  is_active: true,
  permission_ids: []
})

const fetchRoles = async () => {
  loading.value = true
  try {
    const response = await roleService.getRoles()
    roles.value = response.data
  } catch (error) {
    console.error('Error fetching roles:', error)
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to fetch roles. Please try again.',
      life: 3000 
    })
  } finally {
    loading.value = false
  }
}

const fetchPermissions = async () => {
  try {
    const response = await roleService.getPermissions()
    permissions.value = response.data
  } catch (error) {
    console.error('Error fetching permissions:', error)
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to fetch permissions. Please try again.',
      life: 3000 
    })
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
      // Update existing role
      await roleService.updateRole(editedRole.value.id, editedRole.value)
      // Update local state
      const index = roles.value.findIndex(r => r.id === editedRole.value.id)
      if (index !== -1) {
        roles.value[index] = { ...editedRole.value }
      }
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Role updated successfully',
        life: 3000 
      })
    } else {
      // Create new role
      const newRole = await roleService.createRole(editedRole.value)
      roles.value.unshift(newRole)
      toast.add({ 
        severity: 'success', 
        summary: 'Success', 
        detail: 'Role created successfully',
        life: 3000 
      })
    }
    
    closeRoleDialog()
  } catch (error) {
    console.error('Error saving role:', error)
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to save role. Please try again.',
      life: 3000 
    })
  } finally {
    saving.value = false
  }
}

const openRoleDialog = (role = null) => {
  if (role) {
    editedRole.value = { 
      ...role, 
      permission_ids: role.permissions ? role.permissions.map(p => p.id) : [] 
    }
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
  editedRole.value = { 
    ...role, 
    permission_ids: role.permissions ? role.permissions.map(p => p.id) : [] 
  }
  editMode.value = true
  viewMode.value = true
  roleDialog.value = true
}

const editRole = (role) => {
  editedRole.value = { 
    ...role, 
    permission_ids: role.permissions ? role.permissions.map(p => p.id) : [] 
  }
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
    accept: deleteRole,
    reject: () => {
      selectedRole.value = null
    }
  })
}

const deleteRole = async () => {
  if (!selectedRole.value) return
  
  try {
    await roleService.deleteRole(selectedRole.value.id)
    roles.value = roles.value.filter(r => r.id !== selectedRole.value.id)
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Role deleted successfully',
      life: 3000 
    })
  } catch (error) {
    console.error('Error deleting role:', error)
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to delete role. Please try again.',
      life: 3000 
    })
  } finally {
    selectedRole.value = null
  }
}

const initializeRBAC = async () => {
  try {
    loading.value = true
    const response = await roleService.initializeRBAC()
    await Promise.all([fetchRoles(), fetchPermissions()])
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: response.data?.message || 'RBAC initialized successfully',
      life: 3000 
    })
  } catch (error) {
    console.error('Error initializing RBAC:', error)
    const errorMessage = error.response?.data?.detail || 'Failed to initialize RBAC'
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: errorMessage,
      life: 3000 
    })
  } finally {
    loading.value = false
  }
}

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Toggle role status
const toggleRoleStatus = async (role) => {
  try {
    const newStatus = !role.is_active
    await roleService.updateRole(role.id, { is_active: newStatus })
    
    // Update local state
    const index = roles.value.findIndex(r => r.id === role.id)
    if (index !== -1) {
      roles.value[index].is_active = newStatus
    }
    
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: `Role ${newStatus ? 'activated' : 'deactivated'} successfully`,
      life: 3000 
    })
  } catch (error) {
    console.error('Error toggling role status:', error)
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to update role status. Please try again.',
      life: 3000 
    })
  }
}

// Export roles to different formats
const exportRoles = (format) => {
  // This would typically call an API endpoint to generate the export
  // For now, we'll just show a toast
  toast.add({
    severity: 'info',
    summary: 'Export Started',
    detail: `Exporting roles to ${format.toUpperCase()} format...`,
    life: 3000
  })
  
  // In a real implementation, you would:
  // 1. Call an API endpoint to generate the export
  // 2. Handle the file download
  // 3. Show success/error toast based on the result
}

// Lifecycle Hooks
onMounted(() => {
  fetchRoles()
  fetchPermissions()
})
</script>