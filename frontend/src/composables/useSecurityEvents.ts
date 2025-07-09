import { reactive, toRefs } from 'vue';
import { useToast } from 'primevue/usetoast';
import type { SecurityEvent, SecurityEventFilter } from '@/types/security';

// Mock data for demonstration purposes
const severities: SecurityEvent['severity'][] = ['low', 'medium', 'high', 'critical'];
const eventTypes = ['login_attempt', 'permission_change', 'data_access', 'config_change'];
const sources = ['web', 'api', 'system', 'user'];

const mockEvents: SecurityEvent[] = Array.from({ length: 50 }, (_, i) => ({
  id: `evt-${i + 1}`,
  eventType: eventTypes[i % eventTypes.length] as string,
  severity: severities[i % severities.length]!,
  source: sources[i % sources.length] as string,
  description: `This is a mock description for event ${i + 1}.`,
  timestamp: new Date(Date.now() - i * 3600000).toISOString(),
  ipAddress: `192.168.1.${i + 1}`,
  resolved: i % 3 === 0,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
}));

export function useSecurityEvents() {
  const toast = useToast();

  const state = reactive({
    events: [] as SecurityEvent[],
    loading: false,
    error: null as string | null,
    totalRecords: 0,
  });

  const filters = reactive<SecurityEventFilter>({
    skip: 0,
    limit: 10,
    orderBy: 'timestamp',
    orderDesc: true,
  });

  const fetchEvents = async () => {
    state.loading = true;
    state.error = null;
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));

      // Mock filtering and pagination
      let filtered = [...mockEvents];

      if (filters.searchQuery) {
        const query = filters.searchQuery.toLowerCase();
        filtered = filtered.filter(e => 
          e.description.toLowerCase().includes(query) ||
          e.eventType.toLowerCase().includes(query) ||
          e.ipAddress?.toLowerCase().includes(query)
        );
      }
      if(filters.severity) filtered = filtered.filter(e => e.severity === filters.severity);
      if(filters.eventType) filtered = filtered.filter(e => e.eventType === filters.eventType);
      if(filters.resolved !== undefined) filtered = filtered.filter(e => e.resolved === filters.resolved);

      // Mock sorting
      if (filters.orderBy) {
        filtered.sort((a, b) => {
          const fieldA = a[filters.orderBy as keyof SecurityEvent];
          const fieldB = b[filters.orderBy as keyof SecurityEvent];

          if (fieldA == null || fieldB == null) return 0;

          let comparison = 0;
          if (fieldA > fieldB) comparison = 1;
          if (fieldA < fieldB) comparison = -1;
          return filters.orderDesc ? -comparison : comparison;
        });
      }

      state.totalRecords = filtered.length;
      const start = filters.skip || 0;
      const end = start + (filters.limit || 10);
      state.events = filtered.slice(start, end);

    } catch (err) {
      const message = err instanceof Error ? err.message : 'An unknown error occurred';
      state.error = message;
      toast.add({ severity: 'error', summary: 'Error Fetching Events', detail: message, life: 3000 });
    } finally {
      state.loading = false;
    }
  };

  const resolveSecurityEvent = async (eventId: string) => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 300));
      const eventToResolve = mockEvents.find(e => e.id === eventId);
      if (eventToResolve) {
        eventToResolve.resolved = true;
        eventToResolve.resolvedAt = new Date().toISOString();
        eventToResolve.resolvedBy = 'current_admin'; // Mock user
      }
      toast.add({ severity: 'success', summary: 'Event Resolved', life: 2000 });
      await fetchEvents(); // Refresh data
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An unknown error occurred';
      toast.add({ severity: 'error', summary: 'Error Resolving Event', detail: message, life: 3000 });
    }
  };

  return {
    ...toRefs(state),
    filters,
    fetchEvents,
    resolveSecurityEvent,
  };
}
