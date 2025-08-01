import { RouteRecordRaw } from 'vue-router';

export interface RouteMeta {
  title?: string;
  requiresAuth?: boolean;
  roles?: string[];
  icon?: string;
  breadcrumb?: boolean;
  hidden?: boolean;
  permissions?: string[];
  layout?: string;
}

export interface RouteRecordWithMeta extends Omit<RouteRecordRaw, 'meta' | 'children'> {
  meta?: RouteMeta;
  children?: RouteRecordWithMeta[];
}

export interface ModuleRoute {
  name: string;
  path: string;
  routes: RouteRecordWithMeta[];
  meta?: RouteMeta;
}

export interface ModuleRoutes {
  [key: string]: ModuleRoute;
}
