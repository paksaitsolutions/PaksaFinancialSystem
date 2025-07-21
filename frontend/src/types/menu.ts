export interface MenuItem {
  id: string;
  title: string;
  icon?: string;
  to?: string;
  children?: MenuItem[];
  permission?: string;
  isHeader?: boolean;
  badge?: {
    text: string | number;
    variant?: string;
  };
  isActive?: boolean;
  disabled?: boolean;
  divider?: boolean;
  class?: string;
  target?: '_blank' | '_self' | '_parent' | '_top';
  rel?: string;
  roles?: string[];
}
