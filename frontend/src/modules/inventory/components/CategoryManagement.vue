<template>
  <div class="category-management">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h3>Inventory Categories</h3>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
          Add Category
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <!-- Search -->
        <v-row>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="searchQuery"
              label="Search categories"
              prepend-inner-icon="mdi-magnify"
              density="compact"
              hide-details
              @update:model-value="debouncedFetchCategories"
            ></v-text-field>
          </v-col>
        </v-row>
      </v-card-text>
      
      <!-- Data table -->
      <v-data-table
        :headers="headers"
        :items="categories"
        :loading="loading"
        class="elevation-1"
      >
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            variant="text"
            size="small"
            color="warning"
            @click="editCategory(item)"
          >
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn
            icon
            variant="text"
            size="small"
            color="error"
            @click="confirmDelete(item)"
          >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>
    
    <!-- Create/Edit Dialog -->
    <v-dialog v-model="dialog.show" max-width="600px">
      <v-card>
        <v-card-title>{{ dialog.isEdit ? 'Edit' : 'Add' }} Category</v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="dialog.valid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="dialog.formData.code"
                  label="Code*"
                  :rules="[v => !!v || 'Code is required']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="dialog.formData.name"
                  label="Name*"
                  :rules="[v => !!v || 'Name is required']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="dialog.formData.description"
                  label="Description"
                  rows="3"
                  auto-grow
                ></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="dialog.show = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="dialog.saving"
            :disabled="!dialog.valid"
            @click="saveCategory"
          >
            {{ dialog.isEdit ? 'Update' : 'Create' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog.show" max-width="500px">
      <v-card>
        <v-card-title>Delete Category</v-card-title>
        <v-card-text>
          Are you sure you want to delete category "{{ deleteDialog.category?.name }}"?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="deleteDialog.show = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteCategory">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { debounce } from '@/utils/debounce';
import { apiClient } from '@/utils/apiClient';

// Composables
const { showSnackbar } = useSnackbar();

// Data
const categories = ref([]);
const loading = ref(false);
const searchQuery = ref('');

// Dialog state
const dialog = reactive({
  show: false,
  isEdit: false,
  valid: false,
  saving: false,
  formData: {
    code: '',
    name: '',
    description: '',
  },
  editId: null,
});

const deleteDialog = reactive({
  show: false,
  category: null,
});

// Table headers
const headers = [
  { title: 'Code', key: 'code', sortable: true },
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Description', key: 'description', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

// Methods
const fetchCategories = async () => {
  loading.value = true;
  try {
    const params = {};
    if (searchQuery.value) {
      params.name = searchQuery.value;
    }
    
    const response = await apiClient.get('/api/v1/inventory/categories', { params });
    categories.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load categories', 'error');
    console.error('Error fetching categories:', error);
  } finally {
    loading.value = false;
  }
};

const debouncedFetchCategories = debounce(fetchCategories, 300);

const openCreateDialog = () => {
  dialog.isEdit = false;
  dialog.editId = null;
  dialog.formData = {
    code: '',
    name: '',
    description: '',
  };
  dialog.show = true;
};

const editCategory = (category) => {
  dialog.isEdit = true;
  dialog.editId = category.id;
  dialog.formData = {
    code: category.code,
    name: category.name,
    description: category.description || '',
  };
  dialog.show = true;
};

const saveCategory = async () => {
  if (!dialog.valid) return;
  
  dialog.saving = true;
  try {
    if (dialog.isEdit) {
      await apiClient.put(`/api/v1/inventory/categories/${dialog.editId}`, dialog.formData);
      showSnackbar('Category updated successfully', 'success');
    } else {
      await apiClient.post('/api/v1/inventory/categories', dialog.formData);
      showSnackbar('Category created successfully', 'success');
    }
    
    dialog.show = false;
    fetchCategories();
  } catch (error) {
    showSnackbar(error.response?.data?.message || 'Failed to save category', 'error');
    console.error('Error saving category:', error);
  } finally {
    dialog.saving = false;
  }
};

const confirmDelete = (category) => {
  deleteDialog.category = category;
  deleteDialog.show = true;
};

const deleteCategory = async () => {
  if (!deleteDialog.category) return;
  
  try {
    await apiClient.delete(`/api/v1/inventory/categories/${deleteDialog.category.id}`);
    showSnackbar('Category deleted successfully', 'success');
    fetchCategories();
  } catch (error) {
    showSnackbar(error.response?.data?.message || 'Failed to delete category', 'error');
    console.error('Error deleting category:', error);
  } finally {
    deleteDialog.show = false;
    deleteDialog.category = null;
  }
};

// Lifecycle hooks
onMounted(() => {
  fetchCategories();
});
</script>

<style scoped>
.category-management {
  padding: 16px;
}
</style>