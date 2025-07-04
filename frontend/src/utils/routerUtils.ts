import type { RouteRecordRaw } from 'vue-router';

/**
 * Filters out development routes in production builds
 */
export function filterDevRoutes(routes: RouteRecordRaw[]): RouteRecordRaw[] {
  if (import.meta.env.PROD) {
    return routes.filter(route => {
      // Remove route if it's marked as devOnly
      if (route.meta?.devOnly) {
        return false;
      }
      
      // Process nested routes
      if (route.children) {
        route.children = filterDevRoutes(route.children);
      }
      
      return true;
    });
  }
  
  return routes;
}

/**
 * Type guard to check if a route has children
 */
export function hasChildren(route: RouteRecordRaw): route is RouteRecordRaw & { children: RouteRecordRaw[] } {
  return Array.isArray((route as any).children);
}
