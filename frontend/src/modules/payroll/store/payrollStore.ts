import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { 
  payrollApiService, 
  type Employee, 
  type PayrollRecord, 
  type PayrollDeduction,
  type DeductionBenefit 
} from '../services/payrollApiService';
import { useToast } from 'primevue/usetoast';

export const usePayrollStore = defineStore('payroll', () => {
  const toast = useToast();
  
  // State
  const employees = ref<Employee[]>([]);
  const currentEmployee = ref<Employee | null>(null);
  const payrollRecords = ref<PayrollRecord[]>([]);
  const currentPayrollRecord = ref<PayrollRecord | null>(null);
  const deductionsBenefits = ref<DeductionBenefit[]>([]);
  const currentDeductionBenefit = ref<DeductionBenefit | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const activeEmployees = computed(() => 
    employees.value.filter(emp => emp.is_active)
  );

  const draftPayrolls = computed(() => 
    payrollRecords.value.filter(record => record.status === 'draft')
  );

  const processedPayrolls = computed(() => 
    payrollRecords.value.filter(record => ['processing', 'completed', 'paid'].includes(record.status))
  );

  // Deductions & Benefits Getters
  const activeDeductions = computed(() => 
    deductionsBenefits.value.filter(item => item.active && item.type === 'deduction')
  );

  const activeBenefits = computed(() => 
    deductionsBenefits.value.filter(item => item.active && item.type === 'benefit')
  );

  const deductionBenefitTypes = computed(() => [
    { label: 'Deduction', value: 'deduction' },
    { label: 'Benefit', value: 'benefit' },
    { label: 'Garnishment', value: 'garnishment' },
    { label: 'Loan', value: 'loan' },
    { label: 'Other', value: 'other' },
  ]);

  // Actions
  const fetchEmployees = async () => {
    try {
      isLoading.value = true;
      error.value = null;
      employees.value = await payrollApiService.getEmployees({ active_only: true });
    } catch (err) {
      error.value = 'Failed to fetch employees';
      console.error('Error fetching employees:', err);
    } finally {
      isLoading.value = false;
    }
  };

  const fetchEmployee = async (id: number) => {
    try {
      isLoading.value = true;
      error.value = null;
      currentEmployee.value = await payrollApiService.getEmployee(id);
    } catch (err) {
      error.value = `Failed to fetch employee ${id}`;
      console.error(`Error fetching employee ${id}:`, err);
    } finally {
      isLoading.value = false;
    }
  };

  const createEmployee = async (employeeData: Omit<Employee, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      isLoading.value = true;
      error.value = null;
      const newEmployee = await payrollApiService.createEmployee(employeeData);
      employees.value.push(newEmployee);
      return newEmployee;
    } catch (err) {
      error.value = 'Failed to create employee';
      console.error('Error creating employee:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const updateEmployee = async (id: number, updates: Partial<Employee>) => {
    try {
      isLoading.value = true;
      error.value = null;
      const updatedEmployee = await payrollApiService.updateEmployee(id, updates);
      
      // Update in the employees array
      const index = employees.value.findIndex(emp => emp.id === id);
      if (index !== -1) {
        employees.value[index] = { ...employees.value[index], ...updatedEmployee };
      }
      
      // Update current employee if it's the one being updated
      if (currentEmployee.value?.id === id) {
        currentEmployee.value = { ...currentEmployee.value, ...updatedEmployee };
      }
      
      return updatedEmployee;
    } catch (err) {
      error.value = `Failed to update employee ${id}`;
      console.error(`Error updating employee ${id}:`, err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchPayrollRecords = async (params: {
    status?: string;
    employee_id?: number;
    start_date?: string;
    end_date?: string;
  } = {}) => {
    try {
      isLoading.value = true;
      error.value = null;
      payrollRecords.value = await payrollApiService.getPayrollRecords(params);
    } catch (err) {
      error.value = 'Failed to fetch payroll records';
      console.error('Error fetching payroll records:', err);
    } finally {
      isLoading.value = false;
    }
  };

  const fetchPayrollRecord = async (id: number) => {
    try {
      isLoading.value = true;
      error.value = null;
      currentPayrollRecord.value = await payrollApiService.getPayrollRecord(id);
    } catch (err) {
      error.value = `Failed to fetch payroll record ${id}`;
      console.error(`Error fetching payroll record ${id}:`, err);
    } finally {
      isLoading.value = false;
    }
  };

  const createPayrollRecord = async (recordData: Omit<PayrollRecord, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      isLoading.value = true;
      error.value = null;
      const newRecord = await payrollApiService.createPayrollRecord(recordData);
      payrollRecords.value.push(newRecord);
      return newRecord;
    } catch (err) {
      error.value = 'Failed to create payroll record';
      console.error('Error creating payroll record:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const updatePayrollRecord = async (id: number, updates: Partial<PayrollRecord>) => {
    try {
      isLoading.value = true;
      error.value = null;
      const updatedRecord = await payrollApiService.updatePayrollRecord(id, updates);
      
      // Update in the records array
      const index = payrollRecords.value.findIndex(record => record.id === id);
      if (index !== -1) {
        payrollRecords.value[index] = { ...payrollRecords.value[index], ...updatedRecord };
      }
      
      // Update current record if it's the one being updated
      if (currentPayrollRecord.value?.id === id) {
        currentPayrollRecord.value = { ...currentPayrollRecord.value, ...updatedRecord };
      }
      
      return updatedRecord;
    } catch (err) {
      error.value = `Failed to update payroll record ${id}`;
      console.error(`Error updating payroll record ${id}:`, err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const processPayrollRecord = async (id: number) => {
    try {
      isLoading.value = true;
      error.value = null;
      const processedRecord = await payrollApiService.processPayrollRecord(id);
      
      // Update in the records array
      const index = payrollRecords.value.findIndex(record => record.id === id);
      if (index !== -1) {
        payrollRecords.value[index] = processedRecord;
      }
      
      // Update current record if it's the one being processed
      if (currentPayrollRecord.value?.id === id) {
        currentPayrollRecord.value = processedRecord;
      }
      
      return processedRecord;
    } catch (err) {
      error.value = `Failed to process payroll record ${id}`;
      console.error(`Error processing payroll record ${id}:`, err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const calculateTaxes = async (grossPay: number, employeeId: number) => {
    try {
      isLoading.value = true;
      error.value = null;
      return await payrollApiService.calculatePayrollTaxes(grossPay, employeeId);
    } catch (err) {
      error.value = 'Failed to calculate taxes';
      console.error('Error calculating taxes:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  // Reset store state
  // Deductions & Benefits Actions
  const fetchDeductionsBenefits = async (params: { active_only?: boolean } = {}) => {
    try {
      isLoading.value = true;
      error.value = null;
      // TODO: Replace with actual API call
      // deductionsBenefits.value = await payrollApiService.getDeductionsBenefits(params);
      
      // Mock data for now
      deductionsBenefits.value = [
        {
          id: 1,
          type: 'deduction',
          name: 'Health Insurance',
          description: 'Monthly health insurance premium',
          amount_type: 'fixed',
          amount: 200.0,
          taxable: false,
          active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 2,
          type: 'benefit',
          name: 'Retirement Match',
          description: 'Company 401k match',
          amount_type: 'percentage',
          amount: 5.0,
          taxable: false,
          active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];
    } catch (err) {
      error.value = 'Failed to fetch deductions and benefits';
      console.error('Error fetching deductions and benefits:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchDeductionBenefit = async (id: number) => {
    try {
      isLoading.value = true;
      error.value = null;
      // TODO: Replace with actual API call
      // currentDeductionBenefit.value = await payrollApiService.getDeductionBenefit(id);
      
      // Mock data for now
      const item = deductionsBenefits.value.find(item => item.id === id);
      if (item) {
        currentDeductionBenefit.value = { ...item };
      } else {
        throw new Error('Deduction/Benefit not found');
      }
    } catch (err) {
      error.value = `Failed to fetch deduction/benefit ${id}`;
      console.error(`Error fetching deduction/benefit ${id}:`, err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const createDeductionBenefit = async (data: Omit<DeductionBenefit, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      // TODO: Replace with actual API call
      // const newItem = await payrollApiService.createDeductionBenefit(data);
      
      // Mock response
      const newItem: DeductionBenefit = {
        ...data,
        id: Math.max(0, ...deductionsBenefits.value.map(i => i.id)) + 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      
      deductionsBenefits.value.push(newItem);
      return newItem;
    } catch (err) {
      error.value = 'Failed to create deduction/benefit';
      console.error('Error creating deduction/benefit:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const updateDeductionBenefit = async (id: number, updates: Partial<DeductionBenefit>) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      // TODO: Replace with actual API call
      // const updatedItem = await payrollApiService.updateDeductionBenefit(id, updates);
      
      // Mock response
      const index = deductionsBenefits.value.findIndex(item => item.id === id);
      if (index === -1) throw new Error('Deduction/Benefit not found');
      
      const updatedItem = {
        ...deductionsBenefits.value[index],
        ...updates,
        updated_at: new Date().toISOString(),
      };
      
      deductionsBenefits.value[index] = updatedItem;
      
      // Update current item if it's the one being updated
      if (currentDeductionBenefit.value?.id === id) {
        currentDeductionBenefit.value = updatedItem;
      }
      
      return updatedItem;
    } catch (err) {
      error.value = `Failed to update deduction/benefit ${id}`;
      console.error(`Error updating deduction/benefit ${id}:`, err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteDeductionBenefit = async (id: number) => {
    try {
      isLoading.value = true;
      error.value = null;
      
      // TODO: Replace with actual API call
      // await payrollApiService.deleteDeductionBenefit(id);
      
      // Mock response
      const index = deductionsBenefits.value.findIndex(item => item.id === id);
      if (index !== -1) {
        deductionsBenefits.value.splice(index, 1);
      }
      
      // Clear current item if it's the one being deleted
      if (currentDeductionBenefit.value?.id === id) {
        currentDeductionBenefit.value = null;
      }
    } catch (err) {
      error.value = `Failed to delete deduction/benefit ${id}`;
      console.error(`Error deleting deduction/benefit ${id}:`, err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const $reset = () => {
    employees.value = [];
    currentEmployee.value = null;
    payrollRecords.value = [];
    currentPayrollRecord.value = null;
    deductionsBenefits.value = [];
    currentDeductionBenefit.value = null;
    isLoading.value = false;
    error.value = null;
  };

  return {
    // State
    employees,
    currentEmployee,
    payrollRecords,
    currentPayrollRecord,
    deductionsBenefits,
    currentDeductionBenefit,
    isLoading,
    error,
    
    // Getters
    activeEmployees,
    draftPayrolls,
    processedPayrolls,
    activeDeductions,
    activeBenefits,
    deductionBenefitTypes,
    
    // Actions
    fetchEmployees,
    fetchEmployee,
    createEmployee,
    updateEmployee,
    fetchPayrollRecords,
    fetchPayrollRecord,
    createPayrollRecord,
    updatePayrollRecord,
    processPayrollRecord,
    calculateTaxes,
    fetchDeductionsBenefits,
    fetchDeductionBenefit,
    createDeductionBenefit,
    updateDeductionBenefit,
    deleteDeductionBenefit,
    $reset
  };
});

export default usePayrollStore;
