import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAI } from '@/services/analytics/aiService';
import { formatCurrency, formatDate } from '@/utils/formatters';

interface AIState {
  insights: {
    compliance: string;
    optimization: string;
    risk: string;
  };
  loading: boolean;
  error: string | null;
}

export const useAIStore = defineStore('ai', () => {
  const aiService = useAI();
  const state = ref<AIState>({
    insights: {
      compliance: '',
      optimization: '',
      risk: ''
    },
    loading: false,
    error: null
  });

  const insights = computed(() => state.value.insights);
  const loading = computed(() => state.value.loading);
  const error = computed(() => state.value.error);

  async function generateInsights(data: any) {
    try {
      state.value.loading = true;
      state.value.error = null;

      const response = await aiService.generateInsights(data);
      state.value.insights = response;

      return response;
    } catch (err) {
      state.value.error = err instanceof Error ? err.message : 'Failed to generate insights';
      throw err;
    } finally {
      state.value.loading = false;
    }
  }

  async function getPredictions(modelId: string, data: any) {
    try {
      state.value.loading = true;
      state.value.error = null;

      const response = await aiService.getPredictions(modelId, data);
      return response;
    } catch (err) {
      state.value.error = err instanceof Error ? err.message : 'Failed to get predictions';
      throw err;
    } finally {
      state.value.loading = false;
    }
  }

  return {
    insights,
    loading,
    error,
    generateInsights,
    getPredictions
  };
});
