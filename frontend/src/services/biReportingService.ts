import axios from 'axios';
export async function getKPIReport() {
  const res = await axios.get('/api/bi-reporting/kpi');
  return res.data;
}
export async function getBIDashboard() {
  const res = await axios.get('/api/bi-reporting/dashboard');
  return res.data;
}
