import { api } from '@/utils/api';

export interface Permission {
  id: string;
  name: string;
  code: string;
  description?: string;
  resource: string;
  action: string;
  created_at: string;
  updated_at: string;
}

export interface Role {
  id: string;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  permissions: Permission[];
  created_at: string;
  updated_at: string;
}

export interface PermissionCreate {
  name: string;
  code: string;
  description?: string;
  resource: string;
  action: string;
}

export interface RoleCreate {
  name: string;
  code: string;
  description?: string;
  is_active?: boolean;
  permission_ids: string[];
}

export interface UserRoleAssignment {
  user_id: string;
  role_ids: string[];
}

export interface PermissionCheck {
  resource: string;
  action: string;
}

/**
 * RBAC Service
 * Provides methods to interact with the RBAC API endpoints
 */
export default {
  /**
   * Create a new permission
   * @param permission - Permission data
   * @returns Promise with the created permission
   */
  async createPermission(permission: PermissionCreate) {
    return api.post('/rbac/permissions', permission);
  },

  /**
   * List all permissions
   * @param options - Filter options
   * @returns Promise with the list of permissions
   */
  async listPermissions(options = {
    skip: 0,
    limit: 100
  }) {
    const params = new URLSearchParams({
      skip: options.skip.toString(),
      limit: options.limit.toString()
    });

    return api.get(`/rbac/permissions?${params.toString()}`);
  },

  /**
   * Create a new role
   * @param role - Role data
   * @returns Promise with the created role
   */
  async createRole(role: RoleCreate) {
    return api.post('/rbac/roles', role);
  },

  /**
   * List all roles
   * @param options - Filter options
   * @returns Promise with the list of roles
   */
  async listRoles(options = {
    skip: 0,
    limit: 100
  }) {
    const params = new URLSearchParams({
      skip: options.skip.toString(),
      limit: options.limit.toString()
    });

    return api.get(`/rbac/roles?${params.toString()}`);
  },

  /**
   * Assign roles to a user
   * @param assignment - User role assignment data
   * @returns Promise with the result
   */
  async assignRolesToUser(assignment: UserRoleAssignment) {
    return api.post('/rbac/users/assign-roles', assignment);
  },

  /**
   * Check if current user has a specific permission
   * @param permissionCheck - Permission check data
   * @returns Promise with the permission check result
   */
  async checkPermission(permissionCheck: PermissionCheck) {
    return api.post('/rbac/check-permission', permissionCheck);
  },

  /**
   * Initialize default permissions and roles
   * @returns Promise with the result
   */
  async initializeRBAC() {
    return api.post('/rbac/initialize');
  }
};