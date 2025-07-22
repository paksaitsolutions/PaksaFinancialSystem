import axios from 'axios';

interface User {
  id: number;
  email: string;
  // Add other user fields as needed
  name?: string;
  permissions?: string[];
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

interface LoginResponse {
  user: User;
  token: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Login with username and password
 * @param username - User's email or username
 * @param password - User's password
 * @returns Promise with user data and token
 */
export const login = async (username: string, password: string): Promise<{ user: User; token: string }> => {
  try {
    // Convert to URL-encoded form data as required by FastAPI OAuth2
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('grant_type', 'password');
    formData.append('scope', '');

    // Make the login request
    const response = await axios.post<TokenResponse>(
      `${API_BASE_URL}/api/v1/auth/token`,
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json',
        },
      }
    );

    // Extract token from response
    const { access_token: token, token_type } = response.data;
    
    // Decode the token to get user info (no need for additional API call)
    const tokenParts = token.split('.');
    if (tokenParts.length !== 3) {
      throw new Error('Invalid token format');
    }
    
    const payload = JSON.parse(atob(tokenParts[1]));
    const user: User = {
      id: payload.sub, // Using email as ID for now
      email: payload.sub,
      name: payload.sub.split('@')[0], // Default name from email
    };
    
    return { user, token };
  } catch (error) {
    console.error('Login error:', error);
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        const message = error.response.data?.detail || 'Login failed. Please check your credentials.';
        throw new Error(message);
        
        // Handle OAuth2 error responses
        if (error.response.data?.detail) {
          if (error.response.status === 401) {
            throw new Error('Invalid username or password');
          }
          throw new Error(error.response.data.detail);
        }

        switch (error.response.status) {
          case 401:
            throw new Error('Invalid username or password');
          case 403:
            throw new Error('Account not activated');
          case 422:
            throw new Error('Invalid input data');
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
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
    } catch (error) {
      console.error('Logout error:', error);
      // Continue with local logout even if the API call fails
    } finally {
      // Clear local storage
      localStorage.removeItem('token');
      localStorage.removeItem('token_type');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      sessionStorage.removeItem('user');
      
      // Clear axios default headers
      if (api.defaults.headers.common['Authorization']) {
        delete api.defaults.headers.common['Authorization'];
      }
    }
  },
  
  /**
   * Get the current user's profile
   */
  async getProfile(token: string): Promise<User> {
    const response = await api.get<User>('/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    });
    return response.data;
  }
};
