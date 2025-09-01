import api from './api'

const BankAccountService = {
  async getBankAccounts() {
    const res = await api.get('/api/v1/cash/accounts')
    // Normalize to expected shape: id, name
    return { data: Array.isArray(res.data) ? res.data.map((a: any) => ({
      id: a.id || a.id,
      name: a.name || a.account_name || a.accountNumber || 'Account'
    })) : [] }
  }
}

export default BankAccountService

