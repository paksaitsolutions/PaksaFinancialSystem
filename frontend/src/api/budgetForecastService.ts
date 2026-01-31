
export interface BudgetForecastDetail {
  id?: number
  period: string
  category: string
  historical: number
  forecast: number
  variance: number
  confidence: number
}

export interface BudgetForecast {
  id?: number
  name: string
  period: string
  method: string
  growth_rate: number
  total_forecast: number
  confidence_level: number
  risk_level: string
  status: string
  created_at?: string
  updated_at?: string
  forecast_details: BudgetForecastDetail[]
}

export interface ForecastSummary {
  total: number
  growth_rate: number
  confidence: number
  risk_level: string
}

export interface ChartData {
  labels: string[]
  datasets: any[]
}

export interface BudgetScenario {
  id?: number
  forecast_id: number
  scenario_type: string
  growth_rate: number
  q1_amount: number
  q2_amount: number
  q3_amount: number
  q4_amount: number
}

export const budgetForecastService = {
  async getForecasts() {
    const response = await apiClient.get('/budget-forecasts/')
    return response.data
  },

  async createForecast(forecast: Partial<BudgetForecast>) {
    const response = await apiClient.post('/budget-forecasts/', forecast)
    return response.data
  },

  async getForecast(id: number) {
    const response = await apiClient.get(`/budget-forecasts/${id}`)
    return response.data
  },

  async updateForecast(id: number, forecast: Partial<BudgetForecast>) {
    const response = await apiClient.put(`/budget-forecasts/${id}`, forecast)
    return response.data
  },

  async deleteForecast(id: number) {
    const response = await apiClient.delete(`/budget-forecasts/${id}`)
    return response.data
  },

  async generateForecast(period: string, method: string, growthRate: number) {
    const response = await apiClient.post('/budget-forecasts/generate', null, {
      params: { period, method, growth_rate: growthRate }
    })
    return response.data
  },

  async getForecastSummary(id: number): Promise<ForecastSummary> {
    const response = await apiClient.get(`/budget-forecasts/summary/${id}`)
    return response.data
  },

  async getChartData(id: number): Promise<ChartData> {
    const response = await apiClient.get(`/budget-forecasts/chart-data/${id}`)
    return response.data
  },

  async getScenarios(id: number): Promise<BudgetScenario[]> {
    const response = await apiClient.get(`/budget-forecasts/scenarios/${id}`)
    return response.data
  }
}