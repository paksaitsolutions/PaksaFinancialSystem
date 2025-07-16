import { ref } from 'vue';

// Mock auth header function - replace with actual authentication logic
const token = ref<string | null>(localStorage.getItem('auth_token') || null);

export const authHeader = () => {
  return token.value ? { 'Authorization': `Bearer ${token.value}` } : {};
};

export const setAuthToken = (newToken: string | null) => {
  token.value = newToken;
  if (newToken) {
    localStorage.setItem('auth_token', newToken);
  } else {
    localStorage.removeItem('auth_token');
  }
};

export const isAuthenticated = () => {
  return !!token.value;
};
