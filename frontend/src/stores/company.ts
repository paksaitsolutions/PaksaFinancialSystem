import { defineStore } from 'pinia';
import { ref } from 'vue';

interface CompanyProfile {
  name: string;
  taxId: string;
  registrationDate: string;
  address: string;
  phone: string;
  email: string;
}

export const useCompanyStore = defineStore('company', () => {
  const profile = ref<CompanyProfile>({
    name: 'Paksa IT Solutions',
    taxId: 'TAX-123456789',
    registrationDate: '2020-01-01',
    address: '123 Business Street, City, State 12345',
    phone: '+1-555-0123',
    email: 'info@paksa.com.pk'
  });

  const getCompanyProfile = async (): Promise<CompanyProfile> => {
    // Mock implementation - replace with actual API call
    return profile.value;
  };

  const updateCompanyProfile = async (updates: Partial<CompanyProfile>): Promise<CompanyProfile> => {
    profile.value = { ...profile.value, ...updates };
    return profile.value;
  };

  return {
    profile,
    getCompanyProfile,
    updateCompanyProfile
  };
});