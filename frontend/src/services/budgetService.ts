import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export interface BudgetLineItem {
  id?: number;
  account_code: string;
  account_name: string;
  category?: string;
  budgeted_amount: number;
  actual_amount?: number;
  variance?: number;
}

export interface Budget {
  id?: number;
  name: string;
  description?: string;
  fiscal_year: number;
  start_date: string;
  end_date: string;
  total_amount?: number;
  status?: string;
  line_items: BudgetLineItem[];
}

export interface BudgetApproval {
  budget_id: number;
  approver_id: number;
  status: string;
  comments?: string;
}

class BudgetService {
  private api = axios.create({
    baseURL: `${API_BASE_URL}/budget`,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  async getBudgets(): Promise<Budget[]> {
    const response = await this.api.get('/');
    return response.data;
  }

  async getBudget(id: number): Promise<Budget> {
    const response = await this.api.get(`/${id}`);
    return response.data;
  }

  async createBudget(budget: Budget): Promise<Budget> {
    const response = await this.api.post('/', budget);
    return response.data;
  }

  async updateBudget(id: number, budget: Partial<Budget>): Promise<Budget> {
    const response = await this.api.put(`/${id}`, budget);
    return response.data;
  }

  async deleteBudget(id: number): Promise<void> {
    await this.api.delete(`/${id}`);
  }

  async getBudgetsByFiscalYear(fiscalYear: number): Promise<Budget[]> {
    const response = await this.api.get(`/fiscal-year/${fiscalYear}`);
    return response.data;
  }

  async approveBudget(budgetId: number, approval: BudgetApproval): Promise<any> {
    const response = await this.api.post(`/${budgetId}/approve`, approval);
    return response.data;
  }
}

export default new BudgetService();