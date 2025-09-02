import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface AIInsight {
  id: string
  type: 'prediction' | 'anomaly' | 'recommendation' | 'optimization'
  title: string
  description: string
  confidence: number
  priority: 'low' | 'medium' | 'high'
  timestamp: Date
  data?: any
}

export interface AIMetrics {
  cashFlowAccuracy: number
  anomaliesDetected: number
  costSavings: number
  processingSpeed: number
  trends: {
    cashFlow: number
    anomalies: number
    savings: number
    speed: number
  }
}

class AIService {
  private ws: WebSocket | null = null

  connectWebSocket(onMessage: (data: any) => void, onStatusChange: (status: string) => void) {
    try {
      this.ws = new WebSocket(`ws://localhost:8000/ws/ai-insights`)
      
      this.ws.onopen = () => {
        onStatusChange('Connected')
        console.log('AI WebSocket connected')
      }
      
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        onMessage(data)
      }
      
      this.ws.onclose = () => {
        onStatusChange('Disconnected')
        setTimeout(() => this.connectWebSocket(onMessage, onStatusChange), 5000)
      }
      
      this.ws.onerror = () => {
        onStatusChange('Error')
      }
    } catch (error) {
      onStatusChange('Failed')
    }
  }

  disconnectWebSocket() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  async getAIMetrics(): Promise<AIMetrics> {
    return {
      cashFlowAccuracy: 92 + Math.random() * 8,
      anomaliesDetected: Math.floor(Math.random() * 5),
      costSavings: 12450 + Math.random() * 5000,
      processingSpeed: 1.2 + Math.random() * 0.5,
      trends: {
        cashFlow: (Math.random() - 0.5) * 10,
        anomalies: (Math.random() - 0.5) * 20,
        savings: (Math.random() - 0.5) * 15,
        speed: (Math.random() - 0.5) * 8
      }
    }
  }

  async getRecommendations(): Promise<AIInsight[]> {
    return [
      {
        id: '1',
        type: 'optimization',
        title: 'Optimize Payment Terms',
        description: 'Extend payment terms with 3 vendors to improve cash flow by 15%',
        confidence: 94,
        priority: 'high',
        timestamp: new Date()
      },
      {
        id: '2',
        type: 'anomaly',
        title: 'Review Expense Patterns',
        description: 'Unusual spending detected in office supplies category',
        confidence: 87,
        priority: 'medium',
        timestamp: new Date()
      }
    ]
  }
}

export const aiService = new AIService()
export default aiService