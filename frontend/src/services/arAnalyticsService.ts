import axios from 'axios';
export async function getARReport() {
  const res = await axios.get('/api/v1/accounts_receivable/reporting');
  return res.data;
}
export async function getDunningStatus() {
  // Stub: Replace with actual API call for dunning/dispute status
  return [];
}
