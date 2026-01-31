<template>
  <div class="user-management">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2 class="text-2xl font-semibold text-900 m-0">User Management</h2>
      <div class="flex gap-2">
        <Button 
          label="Import Users" 
          icon="pi pi-upload" 
          severity="secondary" 
          outlined 
          @click="importUsers"
        />
        <Button 
          label="Add User" 
          icon="pi pi-plus" 
          @click="showAddUser = true"
        />
      </div>
    </div>

    <!-- User Statistics -->
    <div class="grid mb-4">
      <div class="col-12 md:col-3">
        <Card class="text-center">
          <template #content>
            <div class="text-2xl font-bold text-blue-600">{{ stats.totalUsers }}</div>
            <div class="text-sm text-600">Total Users</div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card class="text-center">
          <template #content>
            <div class="text-2xl font-bold text-green-600">{{ stats.activeUsers }}</div>
            <div class="text-sm text-600">Active Users</div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card class="text-center">
          <template #content>
            <div class="text-2xl font-bold text-orange-600">{{ stats.pendingUsers }}</div>
            <div class="text-sm text-600">Pending Approval</div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-3">
        <Card class="text-center">
          <template #content>
            <div class="text-2xl font-bold text-red-600">{{ stats.inactiveUsers }}</div>
            <div class="text-sm text-600">Inactive Users</div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Users Table -->
    <Card>
      <template #header>
        <div class="flex justify-content-between align-items-center p-4">
          <h3 class="m-0">Users</h3>
          <div class="flex gap-2">
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText v-model="searchTerm" placeholder="Search users..." />
            </span>
            <Dropdown 
              v-model="filterRole" 
              :options="roleFilterOptions" 
              optionLabel="label" 
              optionValue="value"
              placeholder="Filter by role"
              @change="filterUsers"
            />
          </div>
        </div>
      </template>
      <template #content>
        <DataTable 
          :value="filteredUsers" 
          :loading="loading"
          :paginator="true" 
          :rows="10"
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <template #empty>No users found.</template>
          <Column field="firstName" header="Name" sortable>
            <template #body="{ data }">
              <div class="flex align-items-center gap-2">
                <Avatar 
                  :label="getInitials(data.firstName, data.lastName)" 
                  class="mr-2" 
                  size="normal" 
                  shape="circle"
                />
                <div>
                  <div class="font-medium">{{ data.firstName }} {{ data.lastName }}</div>
                  <div class="text-sm text-600">{{ data.email }}</div>
                </div>
              </div>
            </template>
          </Column>
          <Column field="role" header="Role" sortable>
            <template #body="{ data }">
              <Tag :value="data.role" :severity="getRoleSeverity(data.role)" />
            </template>
          </Column>
          <Column field="department" header="Department" sortable />
          <Column field="lastLogin" header="Last Login" sortable>
            <template #body="{ data }">
              {{ data.lastLogin ? formatDate(data.lastLogin) : 'Never' }}
            </template>
          </Column>
          <Column field="isActive" header="Status" sortable>
            <template #body="{ data }">
              <Tag 
                :value="data.isActive ? 'Active' : 'Inactive'" 
                :severity="data.isActive ? 'success' : 'secondary'" 
              />
            </template>
          </Column>
          <Column header="Actions" style="width: 120px">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-text p-button-sm" 
                  @click="viewUser(data)"
                  v-tooltip.top="'View Details'"
                />
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-sm p-button-warning" 
                  @click="editUser(data)"
                  v-tooltip.top="'Edit User'"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-danger" 
                  @click="confirmDeleteUser(data)"
                  v-tooltip.top="'Delete User'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Add/Edit User Dialog -->
    <Dialog 
      v-model:visible="showAddUser" 
      :header="editingUser ? 'Edit User' : 'Add User'" 
      :style="{ width: '600px' }" 
      :modal="true"
      class="p-fluid"
    >
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="firstName">First Name <span class="text-red-500">*</span></label>
            <InputText 
              id="firstName" 
              v-model="newUser.firstName" 
              class="w-full" 
              :class="{ 'p-invalid': submitted && !newUser.firstName }"
            />
            <small class="p-error" v-if="submitted && !newUser.firstName">First name is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="lastName">Last Name <span class="text-red-500">*</span></label>
            <InputText 
              id="lastName" 
              v-model="newUser.lastName" 
              class="w-full" 
              :class="{ 'p-invalid': submitted && !newUser.lastName }"
            />
            <small class="p-error" v-if="submitted && !newUser.lastName">Last name is required.</small>
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="email">Email <span class="text-red-500">*</span></label>
            <InputText 
              id="email" 
              v-model="newUser.email" 
              type="email"
              class="w-full" 
              :class="{ 'p-invalid': submitted && !newUser.email }"
            />
            <small class="p-error" v-if="submitted && !newUser.email">Email is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="role">Role <span class="text-red-500">*</span></label>
            <Dropdown 
              id="role" 
              v-model="newUser.role" 
              :options="roles" 
              optionLabel="label" 
              optionValue="value"
              class="w-full" 
              :class="{ 'p-invalid': submitted && !newUser.role }"
            />
            <small class="p-error" v-if="submitted && !newUser.role">Role is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="department">Department</label>
            <Dropdown 
              id="department" 
              v-model="newUser.department" 
              :options="departments" 
              optionLabel="label" 
              optionValue="value"
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12" v-if="!editingUser">
          <div class="field">
            <label for="password">Password <span class="text-red-500">*</span></label>
            <Password 
              id="password" 
              v-model="newUser.password" 
              class="w-full" 
              :class="{ 'p-invalid': submitted && !newUser.password }"
              toggleMask
            />
            <small class="p-error" v-if="submitted && !newUser.password">Password is required.</small>
          </div>
        </div>
        <div class="col-12">
          <div class="field-checkbox">
            <Checkbox id="isActive" v-model="newUser.isActive" :binary="true" />
            <label for="isActive" class="ml-2">Active User</label>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          @click="hideUserDialog" 
          class="p-button-text" 
          :disabled="saving"
        />
        <Button 
          :label="editingUser ? 'Update' : 'Create'" 
          @click="saveUser" 
          :loading="saving"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="showDeleteDialog" 
      header="Confirm Delete" 
      :style="{ width: '450px' }" 
      :modal="true"
    >
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="userToDelete">
          Are you sure you want to delete user <b>{{ userToDelete.firstName }} {{ userToDelete.lastName }}</b>?
        </span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="showDeleteDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="deleteUser"
          :loading="deleting"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

interface User {
  id?: string
  firstName: string
  lastName: string
  email: string
  role: string
  department?: string
  isActive: boolean
  lastLogin?: string
  password?: string
}

const toast = useToast()
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)
const submitted = ref(false)
const showAddUser = ref(false)
const showDeleteDialog = ref(false)
const editingUser = ref(false)
const searchTerm = ref('')
const filterRole = ref('')

const users = ref<User[]>([])
const userToDelete = ref<User | null>(null)

const newUser = ref<User>({
  firstName: '',
  lastName: '',
  email: '',
  role: '',
  department: '',
  isActive: true,
  password: ''
})

const stats = ref({
  totalUsers: 0,
  activeUsers: 0,
  pendingUsers: 0,
  inactiveUsers: 0
})

const roles = [
  { label: 'Super Admin', value: 'super_admin' },
  { label: 'Admin', value: 'admin' },
  { label: 'Manager', value: 'manager' },
  { label: 'Accountant', value: 'accountant' },
  { label: 'User', value: 'user' }
]

const roleFilterOptions = [
  { label: 'All Roles', value: '' },
  ...roles
]

const departments = [
  { label: 'Accounting', value: 'accounting' },
  { label: 'Finance', value: 'finance' },
  { label: 'HR', value: 'hr' },
  { label: 'IT', value: 'it' },
  { label: 'Operations', value: 'operations' },
  { label: 'Sales', value: 'sales' }
]

const filteredUsers = computed(() => {
  let filtered = users.value
  
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    filtered = filtered.filter(user => 
      user.firstName.toLowerCase().includes(search) ||
      user.lastName.toLowerCase().includes(search) ||
      user.email.toLowerCase().includes(search)
    )
  }
  
  if (filterRole.value) {
    filtered = filtered.filter(user => user.role === filterRole.value)
  }
  
  return filtered
})

const loadUsers = async () => {
  loading.value = true
  try {
    // Mock API call - replace with real API
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    users.value = [
      {
        id: '1',
        firstName: 'John',
        lastName: 'Doe',
        email: 'john@paksa.com',
        role: 'admin',
        department: 'it',
        isActive: true,
        lastLogin: '2024-01-15T10:30:00Z'
      },
      {
        id: '2',
        firstName: 'Jane',
        lastName: 'Smith',
        email: 'jane@paksa.com',
        role: 'manager',
        department: 'accounting',
        isActive: true,
        lastLogin: '2024-01-14T15:45:00Z'
      },
      {
        id: '3',
        firstName: 'Bob',
        lastName: 'Johnson',
        email: 'bob@paksa.com',
        role: 'user',
        department: 'finance',
        isActive: false,
        lastLogin: '2024-01-10T09:15:00Z'
      }
    ]
    
    updateStats()
  } catch (error) {
    console.error('Error loading users:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load users',
      life: 3000
    })
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  stats.value = {
    totalUsers: users.value.length,
    activeUsers: users.value.filter(u => u.isActive).length,
    pendingUsers: 0, // Would come from API
    inactiveUsers: users.value.filter(u => !u.isActive).length
  }
}

const saveUser = async () => {
  submitted.value = true
  
  if (!newUser.value.firstName || !newUser.value.lastName || !newUser.value.email || !newUser.value.role) {
    return
  }
  
  if (!editingUser.value && !newUser.value.password) {
    return
  }
  
  saving.value = true
  try {
    // Mock API call - replace with real API
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (editingUser.value) {
      const index = users.value.findIndex(u => u.id === newUser.value.id)
      if (index !== -1) {
        users.value[index] = { ...newUser.value }
      }
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'User updated successfully',
        life: 3000
      })
    } else {
      const user = {
        ...newUser.value,
        id: Date.now().toString()
      }
      users.value.push(user)
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'User created successfully',
        life: 3000
      })
    }
    
    updateStats()
    hideUserDialog()
  } catch (error) {
    console.error('Error saving user:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save user',
      life: 3000
    })
  } finally {
    saving.value = false
  }
}

const editUser = (user: User) => {
  newUser.value = { ...user }
  editingUser.value = true
  showAddUser.value = true
}

const viewUser = (user: User) => {
  toast.add({
    severity: 'info',
    summary: 'View User',
    detail: `Viewing details for ${user.firstName} ${user.lastName}`,
    life: 3000
  })
}

const confirmDeleteUser = (user: User) => {
  userToDelete.value = user
  showDeleteDialog.value = true
}

const deleteUser = async () => {
  if (!userToDelete.value) return
  
  deleting.value = true
  try {
    // Mock API call - replace with real API
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    users.value = users.value.filter(u => u.id !== userToDelete.value?.id)
    updateStats()
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'User deleted successfully',
      life: 3000
    })
    
    showDeleteDialog.value = false
    userToDelete.value = null
  } catch (error) {
    console.error('Error deleting user:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete user',
      life: 3000
    })
  } finally {
    deleting.value = false
  }
}

const hideUserDialog = () => {
  showAddUser.value = false
  editingUser.value = false
  submitted.value = false
  newUser.value = {
    firstName: '',
    lastName: '',
    email: '',
    role: '',
    department: '',
    isActive: true,
    password: ''
  }
}

const importUsers = () => {
  toast.add({
    severity: 'info',
    summary: 'Import Users',
    detail: 'Import functionality would be implemented here',
    life: 3000
  })
}

const filterUsers = () => {
  // Filtering is handled by computed property
}

const getRoleSeverity = (role: string) => {
  switch (role) {
    case 'super_admin': return 'danger'
    case 'admin': return 'warning'
    case 'manager': return 'info'
    case 'accountant': return 'success'
    case 'user': return 'secondary'
    default: return 'secondary'
  }
}

const getInitials = (firstName: string, lastName: string) => {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase()
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-management {
  max-width: 1200px;
  margin: 0 auto;
}

.field {
  margin-bottom: 1rem;
}

.field-checkbox {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.p-invalid {
  border-color: var(--red-500) !important;
}
</style>