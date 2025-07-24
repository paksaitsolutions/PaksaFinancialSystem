import { ref, computed, onMounted, onUnmounted } from 'vue';
import sessionService from '@/services/sessionService';
import { useRouter } from 'vue-router';

export function useSession() {
  const router = useRouter();
  
  const sessionToken = ref<string | null>(null);
  const sessionValid = ref<boolean>(false);
  const sessionExpiry = ref<Date | null>(null);
  const timeUntilExpiry = ref<number>(0);
  const sessionConfig = ref<any>(null);
  
  let sessionCheckInterval: NodeJS.Timeout | null = null;
  let expiryCountdown: NodeJS.Timeout | null = null;
  
  // Computed properties
  const isSessionActive = computed(() => sessionValid.value && sessionToken.value);
  const sessionExpiresIn = computed(() => {
    if (!sessionExpiry.value) return 0;
    return Math.max(0, sessionExpiry.value.getTime() - Date.now());
  });
  
  const sessionExpiresInMinutes = computed(() => {
    return Math.floor(sessionExpiresIn.value / (1000 * 60));
  });
  
  // Initialize session
  const initializeSession = async () => {
    const token = sessionService.utils.getSessionToken();
    if (token) {
      sessionToken.value = token;
      await validateCurrentSession();
    }
    
    await loadSessionConfig();
    startSessionMonitoring();
  };
  
  // Validate current session
  const validateCurrentSession = async () => {
    if (!sessionToken.value) {
      sessionValid.value = false;
      return false;
    }
    
    try {
      const response = await sessionService.validateSession(sessionToken.value);
      const validation = response.data;
      
      sessionValid.value = validation.valid;
      
      if (validation.valid && validation.expires_at) {
        sessionExpiry.value = new Date(validation.expires_at);
      } else {
        sessionExpiry.value = null;
        if (!validation.valid) {
          await logout();
        }
      }
      
      return validation.valid;
    } catch (error) {
      console.error('Session validation failed:', error);
      sessionValid.value = false;
      await logout();
      return false;
    }
  };
  
  // Extend session
  const extendSession = async (durationMinutes?: number) => {
    if (!sessionToken.value) return false;
    
    try {
      const response = await sessionService.extendSession(sessionToken.value, durationMinutes);
      const session = response.data;
      
      sessionExpiry.value = new Date(session.expires_at);
      return true;
    } catch (error) {
      console.error('Failed to extend session:', error);
      return false;
    }
  };
  
  // Logout
  const logout = async (reason: string = 'User logout') => {
    if (sessionToken.value) {
      try {
        await sessionService.terminateSession(sessionToken.value, reason);
      } catch (error) {
        console.error('Failed to terminate session:', error);
      }
    }
    
    sessionService.utils.removeSessionToken();
    sessionToken.value = null;
    sessionValid.value = false;
    sessionExpiry.value = null;
    
    stopSessionMonitoring();
    
    // Redirect to login
    router.push('/login');
  };
  
  // Load session configuration
  const loadSessionConfig = async () => {
    try {
      const response = await sessionService.getSessionConfig();
      sessionConfig.value = response.data;
    } catch (error) {
      console.error('Failed to load session config:', error);
    }
  };
  
  // Start session monitoring
  const startSessionMonitoring = () => {
    // Check session validity every 5 minutes
    sessionCheckInterval = setInterval(async () => {
      await validateCurrentSession();
    }, 5 * 60 * 1000);
    
    // Update expiry countdown every second
    expiryCountdown = setInterval(() => {
      timeUntilExpiry.value = sessionExpiresIn.value;
      
      // Auto-extend session when 5 minutes remaining
      if (sessionConfig.value?.auto_logout_on_idle && sessionExpiresInMinutes.value === 5) {
        extendSession();
      }
      
      // Auto-logout when session expires
      if (sessionExpiresIn.value <= 0 && sessionValid.value) {
        logout('Session expired');
      }
    }, 1000);
  };
  
  // Stop session monitoring
  const stopSessionMonitoring = () => {
    if (sessionCheckInterval) {
      clearInterval(sessionCheckInterval);
      sessionCheckInterval = null;
    }
    
    if (expiryCountdown) {
      clearInterval(expiryCountdown);
      expiryCountdown = null;
    }
  };
  
  // Check if fresh login is required
  const checkFreshLoginRequired = async (): Promise<boolean> => {
    if (!sessionToken.value) return true;
    
    try {
      const response = await sessionService.checkFreshLoginRequired(sessionToken.value);
      return response.data.fresh_login_required;
    } catch (error) {
      console.error('Failed to check fresh login requirement:', error);
      return true;
    }
  };
  
  // Activity tracking
  const trackActivity = () => {
    // Extend session on user activity if auto-extend is enabled
    if (sessionConfig.value?.auto_logout_on_idle && sessionValid.value) {
      extendSession();
    }
  };
  
  // Setup activity listeners
  const setupActivityListeners = () => {
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    events.forEach(event => {
      document.addEventListener(event, trackActivity, { passive: true });
    });
  };
  
  // Cleanup activity listeners
  const cleanupActivityListeners = () => {
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    events.forEach(event => {
      document.removeEventListener(event, trackActivity);
    });
  };
  
  // Lifecycle hooks
  onMounted(() => {
    initializeSession();
    setupActivityListeners();
  });
  
  onUnmounted(() => {
    stopSessionMonitoring();
    cleanupActivityListeners();
  });
  
  return {
    // State
    sessionToken: computed(() => sessionToken.value),
    sessionValid: computed(() => sessionValid.value),
    sessionExpiry: computed(() => sessionExpiry.value),
    sessionConfig: computed(() => sessionConfig.value),
    isSessionActive,
    sessionExpiresIn,
    sessionExpiresInMinutes,
    timeUntilExpiry: computed(() => timeUntilExpiry.value),
    
    // Methods
    initializeSession,
    validateCurrentSession,
    extendSession,
    logout,
    checkFreshLoginRequired,
    trackActivity
  };
}