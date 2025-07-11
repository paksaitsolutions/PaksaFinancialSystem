import axios from 'axios';
export async function detectAnomalies(data: any) {
  const res = await axios.post('/api/ai-ml/anomaly-detection', data);
  return res.data;
}
export async function runForecasting(data: any) {
  const res = await axios.post('/api/ai-ml/forecasting', data);
  return res.data;
}
export async function getRecommendations(data: any) {
  const res = await axios.post('/api/ai-ml/recommendations', data);
  return res.data;
}
