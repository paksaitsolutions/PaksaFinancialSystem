/**
 * User interface representing an authenticated user
 */
export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  permissions: string[];
}

/**
 * Login credentials interface
 */
export interface LoginCredentials {
  email: string;
  password: string;
}

/**
 * Registration data interface
 */
export interface RegistrationData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
}

/**
 * Auth response interface
 */
export interface AuthResponse {
  user: User;
  token: string;
}

/**
 * Password reset request interface
 */
export interface PasswordResetRequest {
  email: string;
}

/**
 * Password reset confirmation interface
 */
export interface PasswordResetConfirmation {
  token: string;
  password: string;
}