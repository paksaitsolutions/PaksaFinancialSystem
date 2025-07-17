import api from '@/services/api';
import type { User, AuthResponse, RegistrationData } from '@/types/auth';

/**
 * Authentication service for handling user authentication
 */
class AuthService {
  /**
   * Login with email and password
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<AuthResponse>} - User data and token
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    try {
      // In a real app, this would be an actual API call
      // const response = await api.post('/auth/login', { email, password });
      // return response.data;
      
      // Mock response for development
      await new Promise(resolve => setTimeout(resolve, 800));
      
      if (email === 'admin@example.com' && password === 'password') {
        return {
          user: {
            id: '1',
            email: email,
            name: 'Admin User',
            role: 'admin',
            permissions: ['*']
          },
          token: 'mock-jwt-token'
        };
      } else {
        throw new Error('Invalid email or password');
      }
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Register a new user
   * @param {RegistrationData} userData - User registration data
   * @returns {Promise<{ success: boolean, message: string }>} - Registration result
   */
  async register(userData: RegistrationData): Promise<{ success: boolean, message: string }> {
    try {
      // In a real app, this would be an actual API call
      // const response = await api.post('/auth/register', userData);
      // return response.data;
      
      // Mock response for development
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return {
        success: true,
        message: 'User registered successfully'
      };
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  /**
   * Request password reset
   * @param {string} email - User email
   * @returns {Promise<{ success: boolean, message: string }>} - Response data
   */
  async forgotPassword(email: string): Promise<{ success: boolean, message: string }> {
    try {
      // In a real app, this would be an actual API call
      // const response = await api.post('/auth/forgot-password', { email });
      // return response.data;
      
      // Mock response for development
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return {
        success: true,
        message: 'Password reset instructions sent to your email'
      };
    } catch (error) {
      console.error('Forgot password error:', error);
      throw error;
    }
  }

  /**
   * Reset password with token
   * @param {string} token - Reset token
   * @param {string} password - New password
   * @returns {Promise<{ success: boolean, message: string }>} - Response data
   */
  async resetPassword(token: string, password: string): Promise<{ success: boolean, message: string }> {
    try {
      // In a real app, this would be an actual API call
      // const response = await api.post('/auth/reset-password', { token, password });
      // return response.data;
      
      // Mock response for development
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      return {
        success: true,
        message: 'Password reset successful'
      };
    } catch (error) {
      console.error('Reset password error:', error);
      throw error;
    }
  }

  /**
   * Logout the current user
   * @returns {Promise<{ success: boolean }>} - Response data
   */
  async logout(): Promise<{ success: boolean }> {
    try {
      // In a real app, this would be an actual API call
      // const response = await api.post('/auth/logout');
      // return response.data;
      
      // Mock response for development
      await new Promise(resolve => setTimeout(resolve, 500));
      
      return {
        success: true
      };
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  }

  /**
   * Get current user profile
   * @returns {Promise<User>} - User profile data
   */
  async getProfile(): Promise<User> {
    try {
      // In a real app, this would be an actual API call
      // const response = await api.get('/auth/me');
      // return response.data;
      
      // Mock response for development
      await new Promise(resolve => setTimeout(resolve, 500));
      
      return {
        id: '1',
        email: 'admin@example.com',
        name: 'Admin User',
        role: 'admin',
        permissions: ['*']
      };
    } catch (error) {
      console.error('Get profile error:', error);
      throw error;
    }
  }
}

export default new AuthService();