<template>
  <div class="skills-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Skills Management</h1>
        <p class="text-color-secondary">Manage employee skills and competencies</p>
      </div>
      <Button label="Add Skill" icon="pi pi-plus" @click="showDialog" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="skills" :loading="loading" paginator :rows="10">
          <Column field="name" header="Skill Name" sortable />
          <Column field="category" header="Category" sortable />
          <Column field="level" header="Level" sortable>
            <template #body="{ data }">
              <Tag :value="data.level" :severity="getLevelSeverity(data.level)" />
            </template>
          </Column>
          <Column field="employeeCount" header="Employees" sortable />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editSkill(data)" />
              <Button icon="pi pi-eye" class="p-button-text" @click="viewSkill(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="Skill Details" :modal="true" :style="{width: '500px'}">
      <div class="field">
        <label>Skill Name</label>
        <InputText v-model="newSkill.name" class="w-full" />
      </div>
      <div class="field">
        <label>Category</label>
        <Dropdown v-model="newSkill.category" :options="categories" placeholder="Select Category" class="w-full" />
      </div>
      <div class="field">
        <label>Level</label>
        <Dropdown v-model="newSkill.level" :options="levels" placeholder="Select Level" class="w-full" />
      </div>
      <div class="field">
        <label>Description</label>
        <Textarea v-model="newSkill.description" rows="3" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Save" @click="saveSkill" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface Skill {
  id: number;
  name: string;
  category: string;
  level: string;
  employeeCount: number;
  status: string;
  description: string;
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);

const skills = ref<Skill[]>([]);
const categories = ref(['Technical', 'Soft Skills', 'Leadership', 'Communication', 'Problem Solving', 'Other']);
const levels = ref(['Beginner', 'Intermediate', 'Advanced', 'Expert']);

const newSkill = ref({
  name: '',
  category: '',
  level: '',
  description: ''
});

const showDialog = () => {
  newSkill.value = {
    name: '',
    category: '',
    level: '',
    description: ''
  };
  dialogVisible.value = true;
};

const saveSkill = () => {
  if (newSkill.value.name && newSkill.value.category) {
    const skill: Skill = {
      id: Date.now(),
      name: newSkill.value.name,
      category: newSkill.value.category,
      level: newSkill.value.level,
      employeeCount: 0,
      status: 'Active',
      description: newSkill.value.description
    };
    
    skills.value.push(skill);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Skill created', life: 3000 });
  }
};

const editSkill = (skill: Skill) => {
  toast.add({ severity: 'info', summary: 'Edit Skill', detail: `Editing ${skill.name}`, life: 3000 });
};

const viewSkill = (skill: Skill) => {
  toast.add({ severity: 'info', summary: 'View Skill', detail: `Viewing ${skill.name}`, life: 3000 });
};

const getLevelSeverity = (level: string) => {
  switch (level.toLowerCase()) {
    case 'expert': return 'success';
    case 'advanced': return 'info';
    case 'intermediate': return 'warning';
    case 'beginner': return 'danger';
    default: return 'info';
  }
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'active': return 'success';
    case 'inactive': return 'danger';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    skills.value = [
      { id: 1, name: 'JavaScript', category: 'Technical', level: 'Advanced', employeeCount: 15, status: 'Active', description: 'JavaScript programming language' },
      { id: 2, name: 'Leadership', category: 'Leadership', level: 'Intermediate', employeeCount: 8, status: 'Active', description: 'Team leadership and management' },
      { id: 3, name: 'Communication', category: 'Soft Skills', level: 'Advanced', employeeCount: 25, status: 'Active', description: 'Effective communication skills' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.skills-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>