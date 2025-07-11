import axios from 'axios';
export async function getAPReport() {
  const res = await axios.get('/api/v1/accounts_payable/reporting');
  return res.data;
}
export async function getThreeWayMatchStatus() {
  // Stub: Replace with actual API call for three-way match status
  return [];
}
