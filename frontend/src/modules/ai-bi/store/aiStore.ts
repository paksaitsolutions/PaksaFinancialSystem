import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { aiService, type AIInsight, type AIMetrics } from '../services/aiService'

export const useAIStore = defineStore('ai', () => {
  // State
  const metrics = ref<AIMetrics>({
    cashFlowAccuracy: 0,
    anomaliesDetected: 0,
    costSavings: 0,
    processingSpeed: 0,
    trends: {
      cashFlow: 0,
      anomalies: 0,
      savings: 0,
      speed: 0
    }
  })
  
  const recommendations = ref<AIInsight[]>([])
  const anomalies = ref<any[]>([])
  const activityFeed = ref<any[]>([])
  const connectionStatus = ref('Disconnected')
  const loading = ref(false)
  const realTimeEnabled = ref(true)

  // Computed
  const isConnected = computed(() => connectionStatus.value === 'Connected')
  const hasAnomalies = computed(() => anomalies.value.length > 0)
  const highPriorityRecommendations = computed(() => 
    recommendations.value.filter(r => r.priority === 'high')
  )

  // Actions
  const connectRealTime = () => {
    if (!realTimeEnabled.value) return
    
    aiService.connectWebSocket(
      (data) => handleRealTimeUpdate(data),
      (status) => connectionStatus.value = status
    )
  }

  const disconnectRealTime = () => {
    aiService.disconnectWebSocket()
    connectionStatus.value = 'Disconnected'
  }

  const handleRealTimeUpdate = (data: any) => {
    switch (data.type) {
      case 'metrics':
        updateMetrics(data.payload)
        break
      case 'anomaly':
        addAnomaly(data.payload)
        break
      case 'recommendation':
        addRecommendation(data.payload)
        break
      case 'activity':
        addActivity(data.payload)
        break
    }
  }

  const updateMetrics = (newMetrics: Partial<AIMetrics>) => {
    Object.assign(metrics.value, newMetrics)
  }

  const addAnomaly = (anomaly: any) => {
    anomalies.value.unshift(anomaly)
    if (anomalies.value.length > 50) {
      anomalies.value = anomalies.value.slice(0, 50)
    }
  }

  const addRecommendation = (recommendation: AIInsight) => {
    recommendations.value.unshift(recommendation)
    if (recommendations.value.length > 10) {
      recommendations.value = recommendations.value.slice(0, 10)
    }
  }

  const addActivity = (activity: any) => {
    activityFeed.value.unshift({
      ...activity,
      timestamp: new Date()
    })
    if (activityFeed.value.length > 100) {
      activityFeed.value = activityFeed.value.slice(0, 100)
    }
  }

  const fetchMetrics = async () => {
    try {
      loading.value = true
      const data = await aiService.getAIMetrics()
      metrics.value = data
    } catch (error) {
      console.error('Failed to fetch AI metrics:', error)
    } finally {
      loading.value = false
    }
  }

  const fetchRecommendations = async () => {
    try {
      const data = await aiService.getRecommendations()
      recommendations.value = data
    } catch (error) {
      console.error('Failed to fetch recommendations:', error)
    }
  }

  const applyRecommendation = async (recommendationId: string) => {
    try {
      const success = await aiService.applyRecommendation(recommendationId)
      if (success) {
        const index = recommendations.value.findIndex(r => r.id === recommendationId)
        if (index > -1) {
          recommendations.value.splice(index, 1)
        }
      }
      return success
    } catch (error) {
      console.error('Failed to apply recommendation:', error)
      return false
    }
  }

  const dismissRecommendation = async (recommendationId: string) => {
    try {
      const success = await aiService.dismissRecommendation(recommendationId)
      if (success) {
        const index = recommendations.value.findIndex(r => r.id === recommendationId)
        if (index > -1) {
          recommendations.value.splice(index, 1)
        }
      }
      return success
    } catch (error) {
      console.error('Failed to dismiss recommendation:', error)
      return false
    }
  }

  const refreshAll = async () => {
    await Promise.all([
      fetchMetrics(),
      fetchRecommendations()
    ])
  }

  return {
    // State
    metrics,
    recommendations,
    anomalies,
    activityFeed,
    connectionStatus,
    loading,
    realTimeEnabled,
    
    // Computed
    isConnected,
    hasAnomalies,
    highPriorityRecommendations,
    
    // Actions
    connectRealTime,
    disconnectRealTime,
    fetchMetrics,
    fetchRecommendations,
    applyRecommendation,
    dismissRecommendation,
    refreshAll,
    updateMetrics,
    addAnomaly,
    addRecommendation,
    addActivity
  }
})