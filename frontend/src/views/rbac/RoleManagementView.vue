<template>
  <AppLayout title="User Management - Roles">
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <h2>Role Management</h2>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              @click="openRoleDialog()"
            >
              New Role
            </v-btn>
            <v-btn
              color="secondary"
              prepend-icon="mdi-cog"
              @click="initializeRBAC"
              class="ml-2"
            >
              Initialize RBAC
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-data-table
              :headers="roleHeaders"
              :items="roles"
              :loading="loading"
              class="elevation-1"
            >
              <template v-slot:item.is_active="{ item }">
                <v-chip
                  :color="item.is_active ? 'success' : 'error'"
                  size="small"
                >
                  {{ item.is_active ? 'ACTIVE' : 'INACTIVE' }}
                </v-chip>
              </template>
              
              <template v-slot:item.permissions="{ item }">
                <v-chip-group>
                  <v-chip
                    v-for="permission in item.permissions.slice(0, 3)"
                    :key="permission.id"
                    size="small"
                    color="info"
                  >
                    {{ permission.code }}
                  </v-chip>
                  <v-chip
                    v-if="item.permissions.length > 3"
                    size="small"
                    color="grey"
                  >
                    +{{ item.permissions.length - 3 }} more
                  </v-chip>
                </v-chip-group>
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  variant="text"
                  @click="viewRole(item)"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Role Dialog -->
    <v-dialog v-model="roleDialog" max-width="800px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ editMode ? 'View Role' : 'New Role' }}</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="roleForm">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedRole.name"
                  label="Role Name"
                  :rules="[v => !!v || 'Role name is required']"
                  :disabled="editMode"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedRole.code"
                  label="Role Code"
                  :rules="[v => !!v || 'Role code is required']"
                  :disabled="editMode"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="editedRole.description"
                  label="Description"
                  rows="2"
                  :disabled="editMode"
                ></v-textarea>
              </v-col>
              
              <v-col cols="12">
                <v-switch
                  v-model="editedRole.is_active"
                  label="Active"
                  :disabled="editMode"
                ></v-switch>
              </v-col>
              
              <v-col cols="12">
                <h3>Permissions</h3>
                <v-row>
                  <v-col
                    v-for="permission in permissions"
                    :key="permission.id"
                    cols="12" md="6" lg="4"
                  >
                    <v-checkbox
                      v-model="editedRole.permission_ids"
                      :value="permission.id"
                      :disabled="editMode"
                      density="compact"
                    >
                      <template v-slot:label>
                        <div>
                          <strong>{{ permission.name }}</strong>
                          <div class="text-caption">{{ permission.code }}</div>
                        </div>
                      </template>
                    </v-checkbox>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="blue-darken-1"
            variant="text"
            @click="closeRoleDialog"
          >
            {{ editMode ? 'Close' : 'Cancel' }}
          </v-btn>
          <v-btn
            v-if="!editMode"
            color="blue-darken-1"
            variant="text"
            @click="saveRole"
            :loading="saving"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </AppLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
// import rbacService from '@/services/rbacService'
// import { useSnackbar } from '@/composables/useSnackbar'

export default {
  name: 'RoleManagementView',
  components: {
    AppLayout
  },
  
  setup() {
    // const { showSnackbar } = useSnackbar()
    const showSnackbar = (msg, type) => console.log(msg, type)
    
    const roleHeaders = [
      { title: 'Role Name', key: 'name', sortable: true },
      { title: 'Code', key: 'code', sortable: true },
      { title: 'Description', key: 'description', sortable: false },
      { title: 'Status', key: 'is_active', sortable: true },
      { title: 'Permissions', key: 'permissions', sortable: false },
      { title: 'Actions', key: 'actions', sortable: false }
    ];
    
    const roles = ref([]);
    const permissions = ref([]);
    const loading = ref(false);
    const saving = ref(false);
    
    const roleDialog = ref(false);
    const editMode = ref(false);
    const editedRole = ref({
      name: '',
      code: '',
      description: '',
      is_active: true,
      permission_ids: []
    });
    const roleForm = ref(null);
    
    const loadRoles = async () => {
      loading.value = true
      // Mock data
      roles.value = [
        { id: 1, name: 'Admin', code: 'ADMIN', description: 'Full system access', is_active: true, permissions: [{ id: 1, code: 'ALL' }] },
        { id: 2, name: 'Manager', code: 'MANAGER', description: 'Management access', is_active: true, permissions: [{ id: 2, code: 'READ' }, { id: 3, code: 'WRITE' }] },
        { id: 3, name: 'User', code: 'USER', description: 'Basic user access', is_active: true, permissions: [{ id: 2, code: 'READ' }] }
      ]
      loading.value = false
    }
    
    const loadPermissions = async () => {
      // Mock data
      permissions.value = [
        { id: 1, name: 'All Permissions', code: 'ALL' },
        { id: 2, name: 'Read Access', code: 'READ' },
        { id: 3, name: 'Write Access', code: 'WRITE' },
        { id: 4, name: 'Delete Access', code: 'DELETE' }
      ]
    }
    
    const openRoleDialog = (role = null) => {
      if (role) {
        editMode.value = true;
        editedRole.value = {
          ...role,
          permission_ids: role.permissions.map(p => p.id)
        };
      } else {
        editMode.value = false;
        editedRole.value = {
          name: '',
          code: '',
          description: '',
          is_active: true,
          permission_ids: []
        };
      }
      roleDialog.value = true;
    };
    
    const closeRoleDialog = () => {
      roleDialog.value = false;
    };
    
    const saveRole = async () => {
      saving.value = true
      // Mock save
      setTimeout(() => {
        showSnackbar('Role created successfully', 'success')
        closeRoleDialog()
        loadRoles()
        saving.value = false
      }, 1000)
    }
    
    const viewRole = (role) => {
      openRoleDialog(role)
    }
    
    const initializeRBAC = async () => {
      showSnackbar('RBAC initialized successfully', 'success')
      loadRoles()
      loadPermissions()
    }
    
    onMounted(() => {
      loadRoles()
      loadPermissions()
    })
    
    return {
      roleHeaders,
      roles,
      permissions,
      loading,
      saving,
      roleDialog,
      editMode,
      editedRole,
      roleForm,
      loadRoles,
      loadPermissions,
      openRoleDialog,
      closeRoleDialog,
      saveRole,
      viewRole,
      initializeRBAC
    }
  }
}
</script>