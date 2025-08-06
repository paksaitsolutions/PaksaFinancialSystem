/**
 * User interface representing an authenticated user
 */

export interface User {
  id: string;
  email: string;
  name: string;
  permissions?: string[];
  roles?: string[];
  isActive?: boolean;
  lastLogin?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface AuthResponse {
  user: User;
  token: string;
  refreshToken?: string | null;
}