<template>
  <Card>
    <template #header>
      <div class="flex justify-content-between align-items-center p-4">
        <h3 class="m-0">User Management</h3>
        <Button label="Add User" icon="pi pi-plus" @click="showAddUser = true" />
      </div>
    </template>
    <template #content>
      <DataTable :value="users" responsiveLayout="scroll">
        <Column field="name" header="Name"></Column>
        <Column field="email" header="Email"></Column>
        <Column field="role" header="Role">
          <template #body="{ data }">
            <Tag :value="data.role" :severity="getRoleSeverity(data.role)" />
          </template>
        </Column>
        <Column field="status" header="Status">
          <template #body="{ data }">
            <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
          </template>
        </Column>
        <Column header="Actions">
          <template #body="{ data }">
            <Button icon="pi pi-pencil" class="p-button-text p-button-sm mr-2" />
            <Button icon="pi pi-trash" class="p-button-text p-button-sm p-button-danger" />
          </template>
        </Column>
      </DataTable>
    </template>
  </Card>

  <Dialog v-model:visible="showAddUser" header="Add User" :style="{ width: '500px' }" :modal="true">
    <div class="grid">
      <div class="col-12">
        <div class="field">
          <label for="userName">Name</label>
          <InputText id="userName" v-model="newUser.name" class="w-full" />
        </div>
      </div>
      
      <div class="col-12">
        <div class="field">
          <label for="userEmail">Email</label>
          <InputText id="userEmail" v-model="newUser.email" class="w-full" />
        </div>
      </div>
      
      <div class="col-12">
        <div class="field">
          <label for="userRole">Role</label>
          <Dropdown 
            id="userRole" 
            v-model="newUser.role" 
            :options="roles" 
            optionLabel="label" 
            optionValue="value"
            class="w-full" 
          />
        </div>
      </div>
    </div>
    
    <template #footer>
      <Button label="Cancel" @click="showAddUser = false" class="p-button-text" />
      <Button label="Save" @click="addUser" />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showAddUser = ref(false)

const users = ref([
  { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin', status: 'Active' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User', status: 'Active' },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'Manager', status: 'Inactive' }
])

const newUser = ref({
  name: '',
  email: '',
  role: ''
})

const roles = [
  { label: 'Admin', value: 'Admin' },
  { label: 'Manager', value: 'Manager' },
  { label: 'User', value: 'User' }
]

const getRoleSeverity = (role: string) => {
  switch (role) {
    case 'Admin': return 'danger'
    case 'Manager': return 'warning'
    case 'User': return 'info'
    default: return 'secondary'
  }
}

const getStatusSeverity = (status: string) => {
  return status === 'Active' ? 'success' : 'secondary'
}

const addUser = () => {
  users.value.push({
    id: users.value.length + 1,
    ...newUser.value,
    status: 'Active'
  })
  newUser.value = { name: '', email: '', role: '' }
  showAddUser.value = false
}
</script>