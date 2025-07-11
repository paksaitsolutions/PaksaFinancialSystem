import axios from 'axios';
export async function getCashForecast() {
  const res = await axios.get('/api/v1/cash_management/forecasting');
  return res.data;
}
export async function getEnhancedReconciliation() {
  const res = await axios.get('/api/v1/cash_management/enhanced-reconciliation');
  return res.data;
}
