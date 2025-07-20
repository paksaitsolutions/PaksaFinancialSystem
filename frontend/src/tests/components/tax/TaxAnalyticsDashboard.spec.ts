import { describe, it, expect, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import TaxAnalyticsDashboard from '@/modules/tax/views/TaxAnalyticsDashboard.vue';
import { useTaxAnalyticsStore } from '@/modules/tax/store/analytics';
import { createTestingPinia } from '@pinia/testing';
import { createVuetify } from 'vuetify';
import { nextTick } from 'vue';

// Mock API responses
type MockResponse = {
  metrics: {
    totalTax: number;
    avgTaxPerEmployee: number;
    complianceRate: number;
    exemptionUsage: Record<string, number>;
    jurisdictionalBreakdown: Record<string, number>;
  };
  insights: {
    compliance: string;
    optimization: string;
    risk: string;
  };
  period: {
    start: string;
    end: string;
  };
};

const mockAnalyticsResponse: MockResponse = {
  metrics: {
    totalTax: 100000,
    avgTaxPerEmployee: 5000,
    complianceRate: 95,
    exemptionUsage: { 'healthcare': 10000, 'education': 5000 },
    jurisdictionalBreakdown: { 'federal': 70000, 'state': 30000 }
  },
  insights: {
    compliance: 'High compliance rate observed',
    optimization: 'Potential savings identified',
    risk: 'Low risk exposure detected'
  },
  period: {
    start: '2025-01-01',
    end: '2025-01-31'
  }
};

describe('TaxAnalyticsDashboard', () => {
  let wrapper: any;
  let vuetify: any;

  beforeEach(() => {
    vuetify = createVuetify();
    wrapper = mount(TaxAnalyticsDashboard, {
      global: {
        plugins: [vuetify, createTestingPinia()],
        stubs: {
          'apexchart': true
        }
      }
    });
  });

  it('renders component correctly', () => {
    expect(wrapper.exists()).toBe(true);
  });

  it('displays correct page title', () => {
    const title = wrapper.find('h1');
    expect(title.text()).toBe('Tax Analytics Dashboard');
  });

  it('fetches analytics data on mount', async () => {
    const store = useTaxAnalyticsStore();
    await nextTick();
    expect(store.fetchAnalytics).toHaveBeenCalled();
  });

  it('updates analytics data when period changes', async () => {
    const store = useTaxAnalyticsStore();
    const periodSelect = wrapper.find('v-select');
    
    await periodSelect.setValue('current_month');
    await nextTick();
    
    expect(store.fetchAnalytics).toHaveBeenCalled();
  });

  it('displays tax metrics correctly', async () => {
    const store = useTaxAnalyticsStore();
    store.analyticsData = mockAnalyticsResponse.metrics;
    await nextTick();

    const cards = wrapper.findAll('.v-card');
    expect(cards.length).toBe(4);

    const totalTaxCard = cards[0];
    expect(totalTaxCard.text()).toContain('$100,000');

    const avgTaxCard = cards[1];
    expect(avgTaxCard.text()).toContain('$5,000');

    const complianceCard = cards[2];
    expect(complianceCard.text()).toContain('95%');
  });

  it('displays AI insights correctly', async () => {
    const store = useTaxAnalyticsStore();
    store.insights = mockAnalyticsResponse.insights;
    await nextTick();

    const insightsTabs = wrapper.find('.v-tabs');
    expect(insightsTabs.exists()).toBe(true);

    const complianceTab = wrapper.find('[value="compliance"]');
    await complianceTab.trigger('click');
    await nextTick();

    const complianceContent = wrapper.find('.v-card-text');
    expect(complianceContent.text()).toContain('High compliance rate observed');
  });

  it('handles export functionality', async () => {
    const store = useTaxAnalyticsStore();
    const exportBtn = wrapper.find('[aria-label="Export Insights"]');
    
    await exportBtn.trigger('click');
    await nextTick();

    expect(store.exportAnalytics).toHaveBeenCalled();
  });

  it('refreshes data when refresh button clicked', async () => {
    const store = useTaxAnalyticsStore();
    const refreshBtn = wrapper.find('[aria-label="Refresh Data"]');
    
    await refreshBtn.trigger('click');
    await nextTick();

    expect(store.refreshData).toHaveBeenCalled();
  });
});
