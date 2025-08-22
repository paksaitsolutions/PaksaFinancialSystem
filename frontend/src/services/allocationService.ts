import { api } from '@/utils/api';
import { format } from 'date-fns';

export interface AllocationRule {
  id: string;
  rule_name: string;
  rule_code: string;
  description?: string;
  allocation_method: 'percentage' | 'fixed_amount' | 'equal' | 'weighted' | 'formula';
  status: 'active' | 'inactive' | 'draft';
  source_account_id?: string;
  effective_from: string;
  effective_to?: string;
  priority: number;
  allocation_lines: AllocationRuleLine[];
  created_at: string;
  updated_at: string;
}

export interface AllocationRuleLine {
  id?: string;
  target_account_id: string;
  allocation_percentage?: number;
  fixed_amount?: number;
  weight?: number;
  line_order: number;
}

export interface AllocationRuleCreate {
  rule_name: string;
  rule_code?: string;
  description?: string;
  allocation_method: string;
  status?: string;
  source_account_id?: string;
  effective_from: Date;
  effective_to?: Date;
  priority?: number;
  allocation_lines: AllocationRuleLine[];
}

export interface Allocation {
  id: string;
  allocation_number: string;
  allocation_date: string;
  source_journal_entry_id: string;
  source_amount: string;
  allocation_rule_id: string;
  status: string;
  description?: string;
  allocation_entries: AllocationEntry[];
  created_at: string;
}

export interface AllocationEntry {
  id: string;
  allocation_id: string;
  target_account_id: string;
  allocated_amount: string;
  allocation_percentage?: number;
  journal_entry_id?: string;
  description?: string;
  created_at: string;
}

/**
 * Allocation Service
 * Provides methods to interact with the allocation API endpoints
 */
export default {
  /**
   * Create a new allocation rule
   * @param rule - Allocation rule data
   * @returns Promise with the created rule
   */
  async createAllocationRule(rule: AllocationRuleCreate) {
    const formattedRule = {
      ...rule,
      effective_from: format(rule.effective_from, 'yyyy-MM-dd'),
      effective_to: rule.effective_to ? format(rule.effective_to, 'yyyy-MM-dd') : undefined
    };
    return api.post('/allocation/rules', formattedRule);
  },

  /**
   * Get an allocation rule by ID
   * @param id - Rule ID
   * @returns Promise with the rule details
   */
  async getAllocationRule(id: string) {
    return api.get(`/allocation/rules/${id}`);
  },

  /**
   * List allocation rules
   * @param options - Filter options
   * @returns Promise with the list of rules
   */
  async listAllocationRules(options = {
    skip: 0,
    limit: 100
  }) {
    const params = new URLSearchParams({
      skip: options.skip.toString(),
      limit: options.limit.toString()
    });

    return api.get(`/allocation/rules?${params.toString()}`);
  },

  /**
   * Process allocation for a journal entry
   * @param journalEntryId - Journal entry ID
   * @returns Promise with the allocation result
   */
  async processAllocation(journalEntryId: string) {
    return api.post(`/allocation/process/${journalEntryId}`);
  }
};