import { ref } from 'vue';

interface Department {
  id: number;
  name: string;
}

interface StatusOption {
  label: string;
  value: string;
}

// Department options
export const departments = ref<Department[]>([
  { id: 1, name: "Engineering" },
  { id: 2, name: "HR" },
  { id: 3, name: "Finance" },
  { id: 4, name: "Marketing" },
  { id: 5, name: "Sales" },
  { id: 6, name: "Operations" },
]);

// Status options
export const statuses = ref<StatusOption[]>([
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'On Leave', value: 'on_leave' },
  { label: 'Terminated', value: 'terminated' }
]);
