// GL Category Types

export const GL_CATEGORY_TYPES = {
  ASSET: 'ASSET',
  LIABILITY: 'LIABILITY',
  EQUITY: 'EQUITY',
  REVENUE: 'REVENUE',
  EXPENSE: 'EXPENSE',
} as const;

export type GlCategoryType = typeof GL_CATEGORY_TYPES[keyof typeof GL_CATEGORY_TYPES];

export interface GlCategory {
  id: string;
  code: string;
  name: string;
  description?: string;
  type: GlCategoryType;
  isActive: boolean;
  parentId?: string | null;
  sortOrder?: number;
  createdAt?: string | Date;
  updatedAt?: string | Date;
  createdBy?: string;
  updatedBy?: string;
}

export interface GlCategoryTreeNode extends GlCategory {
  children?: GlCategoryTreeNode[];
  level: number;
  isExpanded?: boolean;
}

export interface CreateGlCategoryDto {
  code: string;
  name: string;
  description?: string;
  type: GlCategoryType;
  isActive?: boolean;
  parentId?: string | null;
  sortOrder?: number;
}

export interface UpdateGlCategoryDto extends Partial<CreateGlCategoryDto> {
  id: string;
}

export interface GlCategoryFilters {
  searchTerm?: string;
  type?: GlCategoryType | GlCategoryType[];
  isActive?: boolean;
  parentId?: string | null;
}

export interface GlCategoryState {
  categories: GlCategory[];
  loading: boolean;
  error: string | null;
  selectedCategory: GlCategory | null;
}

export const GL_CATEGORY_TYPE_OPTIONS = [
  { label: 'Asset', value: GL_CATEGORY_TYPES.ASSET },
  { label: 'Liability', value: GL_CATEGORY_TYPES.LIABILITY },
  { label: 'Equity', value: GL_CATEGORY_TYPES.EQUITY },
  { label: 'Revenue', value: GL_CATEGORY_TYPES.REVENUE },
  { label: 'Expense', value: GL_CATEGORY_TYPES.EXPENSE },
];

export const GL_CATEGORY_TYPE_LABELS: Record<GlCategoryType, string> = {
  [GL_CATEGORY_TYPES.ASSET]: 'Asset',
  [GL_CATEGORY_TYPES.LIABILITY]: 'Liability',
  [GL_CATEGORY_TYPES.EQUITY]: 'Equity',
  [GL_CATEGORY_TYPES.REVENUE]: 'Revenue',
  [GL_CATEGORY_TYPES.EXPENSE]: 'Expense',
};

export const GL_CATEGORY_TYPE_ICONS: Record<GlCategoryType, string> = {
  [GL_CATEGORY_TYPES.ASSET]: 'pi pi-wallet',
  [GL_CATEGORY_TYPES.LIABILITY]: 'pi pi-credit-card',
  [GL_CATEGORY_TYPES.EQUITY]: 'pi pi-chart-line',
  [GL_CATEGORY_TYPES.REVENUE]: 'pi pi-money-bill',
  [GL_CATEGORY_TYPES.EXPENSE]: 'pi pi-shopping-cart',
};

export const GL_CATEGORY_TYPE_COLORS: Record<GlCategoryType, string> = {
  [GL_CATEGORY_TYPES.ASSET]: '#4CAF50',
  [GL_CATEGORY_TYPES.LIABILITY]: '#F44336',
  [GL_CATEGORY_TYPES.EQUITY]: '#2196F3',
  [GL_CATEGORY_TYPES.REVENUE]: '#9C27B0',
  [GL_CATEGORY_TYPES.EXPENSE]: '#FF9800',
};
