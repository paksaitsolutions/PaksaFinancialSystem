import { ref, computed } from 'vue';
import { useApi } from '@/composables/useApi';
import { useAuthStore } from '@/stores/auth';

interface AIService {
  generateInsights: (data: any) => Promise<any>;
  getPredictions: (modelId: string, data: any) => Promise<any>;
  getModelVersions: (modelId: string) => Promise<any>;
  getActiveDeployment: (modelId: string) => Promise<any>;
}

export const useAI = (): AIService => {
  const api = useApi();
  const authStore = useAuthStore();
  const loading = ref(false);
  const error = ref(null);

  const generateInsights = async (data: any): Promise<any> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.post('/api/ai/insights', {
        data,
        context: {
          userId: authStore.user.id,
          role: authStore.user.role,
          company: authStore.user.company
        }
      });

      return response.data;
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to generate insights';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getPredictions = async (modelId: string, data: any): Promise<any> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.post(`/api/ai/models/${modelId}/predict`, {
        data,
        context: {
          userId: authStore.user.id,
          role: authStore.user.role,
          company: authStore.user.company
        }
      });

      return response.data;
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to get predictions';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getModelVersions = async (modelId: string): Promise<any> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.get(`/api/ai/models/${modelId}/versions`);
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch model versions';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getActiveDeployment = async (modelId: string): Promise<any> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.get(`/api/ai/models/${modelId}/deployments/active`);
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.message || 'Failed to fetch active deployment';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    generateInsights,
    getPredictions,
    getModelVersions,
    getActiveDeployment
  };
};
