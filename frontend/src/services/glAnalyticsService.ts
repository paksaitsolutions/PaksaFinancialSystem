import axios from 'axios';
export async function getMultiCurrencyBalances() {
  const res = await axios.get('/api/v1/general_ledger/multi-currency-balances');
  return res.data.balances;
}
export async function getBudgetReport() {
  const res = await axios.get('/api/v1/general_ledger/budgeting');
  return res.data;
}
export async function getConsolidationReport() {
  const res = await axios.get('/api/v1/general_ledger/consolidation');
  return res.data;
}
