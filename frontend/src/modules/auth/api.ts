import axios from 'axios';

interface LoginResponse {
  user: {
    id: number;
    name: string;
    email: string;
    permissions?: string[];
  };
  token: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';

/**
 * Login with username and password
 * @param username - User's email or username
 * @param password - User's password
 * @returns Promise with user data and token
 */
export const login = async (username: string, password: string): Promise<LoginResponse> => {
  try {
    const response = await axios.post<LoginResponse>(
      `${API_BASE_URL}/auth/login`,
      { username, password },
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      // Handle specific error status codes
      if (error.response) {
        switch (error.response.status) {
          case 401:
            throw new Error('Invalid username or password');
          case 403:
            throw new Error('Account not activated');
          case 500:
            throw new Error('Server error. Please try again later.');
          default:
            throw new Error(error.response.data?.message || 'Login failed');
        }
      } else if (error.request) {
        // The request was made but no response was received
        throw new Error('No response from server. Please check your connection.');
      }
    }
    // Handle any other errors
    throw new Error('An unexpected error occurred. Please try again.');
  }
};

/**
 * Logout the current user
 * @param token - JWT token for authentication
 */
export const logout = async (token: string): Promise<void> => {
  try {
    await axios.post(
      `${API_BASE_URL}/auth/logout`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
  } catch (error) {
    // Log the error but don't fail the logout process
    console.error('Logout error:', error);
  }
};

/**
 * Get the current authenticated user's profile
 * @param token - JWT token for authentication
 * @returns Promise with user data
 */
export const getCurrentUser = async (token: string): Promise<LoginResponse['user']> => {
  try {
    const response = await axios.get<LoginResponse['user']>(
      `${API_BASE_URL}/auth/me`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Failed to fetch user profile:', error);
    throw error;
  }
};
