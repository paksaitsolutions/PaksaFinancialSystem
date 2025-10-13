"""
Unified Role-Based Access Control (RBAC) System
Cross-module role and permission management
"""
from typing import List, Dict, Set, Optional
from sqlalchemy import Column, String, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseModel, AuditMixin
from app.models.role import Role, Permission, RolePermission, UserPermission
from app.models.user import User

class ModulePermission(BaseModel, AuditMixin):
    """Module-specific permissions"""
    __tablename__ = "module_permissions"
    
    module_name = Column(String(50), nullable=False, index=True)
    permission_code = Column(String(100), nullable=False, index=True)
    permission_name = Column(String(200), nullable=False)
    description = Column(Text)
    is_system_permission = Column(Boolean, default=False)
    
    __table_args__ = (
        {"extend_existing": True},
    )

class UnifiedRole(BaseModel, AuditMixin):
    """Unified roles across all modules"""
    __tablename__ = "unified_roles"
    
    role_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    is_system_role = Column(Boolean, default=False)
    modules = Column(String(500))  # JSON array of module names
    
    # Relationships
    permissions = relationship("UnifiedRolePermission", back_populates="role", cascade="all, delete-orphan")
    users = relationship("UnifiedUserRole", back_populates="role", cascade="all, delete-orphan")
    
    __table_args__ = (
        {"extend_existing": True},
    )

class UnifiedRolePermission(BaseModel):
    """Role-permission mapping"""
    __tablename__ = "unified_role_permissions"
    
    role_id = Column(String, ForeignKey("unified_roles.id"), nullable=False)
    permission_id = Column(String, ForeignKey("module_permissions.id"), nullable=False)
    
    # Relationships
    role = relationship("UnifiedRole", back_populates="permissions")
    permission = relationship("ModulePermission", viewonly=True)
    
    __table_args__ = (
        {"extend_existing": True},
    )

class UnifiedUserRole(BaseModel):
    """User-role mapping"""
    __tablename__ = "unified_user_roles"
    
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role_id = Column(String, ForeignKey("unified_roles.id"), nullable=False)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    
    # Relationships
    user = relationship("User", viewonly=True)
    role = relationship("UnifiedRole", back_populates="users")
    company = relationship("Company", viewonly=True)
    
    __table_args__ = (
        {"extend_existing": True},
    )

class UnifiedRBACService:
    """Service for unified RBAC management"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def check_permission(self, user_id: str, company_id: str, module: str, permission: str) -> bool:
        """Check if user has permission for a specific module action"""
        user_roles = await self.db.query(UnifiedUserRole).filter(
            UnifiedUserRole.user_id == user_id,
            UnifiedUserRole.company_id == company_id
        ).all()
        
        for user_role in user_roles:
            role_permissions = await self.db.query(UnifiedRolePermission).join(
                ModulePermission
            ).filter(
                UnifiedRolePermission.role_id == user_role.role_id,
                ModulePermission.module_name == module,
                ModulePermission.permission_code == permission
            ).first()
            
            if role_permissions:
                return True
        
        return False
    
    async def get_user_permissions(self, user_id: str, company_id: str, module: str = None) -> Set[str]:
        """Get all permissions for a user"""
        query = self.db.query(ModulePermission).join(
            UnifiedRolePermission
        ).join(
            UnifiedUserRole
        ).filter(
            UnifiedUserRole.user_id == user_id,
            UnifiedUserRole.company_id == company_id
        )
        
        if module:
            query = query.filter(ModulePermission.module_name == module)
        
        permissions = await query.all()
        return {p.permission_code for p in permissions}
    
    async def assign_role(self, user_id: str, role_id: str, company_id: str) -> UnifiedUserRole:
        """Assign role to user"""
        existing = await self.db.query(UnifiedUserRole).filter(
            UnifiedUserRole.user_id == user_id,
            UnifiedUserRole.role_id == role_id,
            UnifiedUserRole.company_id == company_id
        ).first()
        
        if existing:
            return existing
        
        user_role = UnifiedUserRole(
            user_id=user_id,
            role_id=role_id,
            company_id=company_id
        )
        self.db.add(user_role)
        await self.db.commit()
        return user_role
    
    async def create_role(self, role_name: str, description: str, modules: List[str], 
                         permissions: List[str]) -> UnifiedRole:
        """Create a new role with permissions"""
        role = UnifiedRole(
            role_name=role_name,
            description=description,
            modules=",".join(modules)
        )
        self.db.add(role)
        await self.db.flush()
        
        # Add permissions
        for perm_id in permissions:
            role_perm = UnifiedRolePermission(
                role_id=role.id,
                permission_id=perm_id
            )
            self.db.add(role_perm)
        
        await self.db.commit()
        return role

# Default module permissions
DEFAULT_PERMISSIONS = {
    "gl": [
        ("gl.accounts.view", "View Chart of Accounts"),
        ("gl.accounts.create", "Create Accounts"),
        ("gl.accounts.edit", "Edit Accounts"),
        ("gl.journals.view", "View Journal Entries"),
        ("gl.journals.create", "Create Journal Entries"),
        ("gl.journals.post", "Post Journal Entries"),
        ("gl.reports.view", "View GL Reports"),
        ("gl.close_period", "Close Accounting Periods")
    ],
    "ap": [
        ("ap.vendors.view", "View Vendors"),
        ("ap.vendors.create", "Create Vendors"),
        ("ap.invoices.view", "View AP Invoices"),
        ("ap.invoices.create", "Create AP Invoices"),
        ("ap.invoices.approve", "Approve AP Invoices"),
        ("ap.payments.view", "View AP Payments"),
        ("ap.payments.create", "Create AP Payments"),
        ("ap.reports.view", "View AP Reports")
    ],
    "ar": [
        ("ar.customers.view", "View Customers"),
        ("ar.customers.create", "Create Customers"),
        ("ar.invoices.view", "View AR Invoices"),
        ("ar.invoices.create", "Create AR Invoices"),
        ("ar.payments.view", "View AR Payments"),
        ("ar.payments.create", "Create AR Payments"),
        ("ar.collections.manage", "Manage Collections"),
        ("ar.reports.view", "View AR Reports")
    ],
    "tax": [
        ("tax.rates.view", "View Tax Rates"),
        ("tax.rates.manage", "Manage Tax Rates"),
        ("tax.returns.view", "View Tax Returns"),
        ("tax.returns.file", "File Tax Returns"),
        ("tax.exemptions.manage", "Manage Tax Exemptions"),
        ("tax.reports.view", "View Tax Reports")
    ],
    "payroll": [
        ("payroll.employees.view", "View Employees"),
        ("payroll.employees.manage", "Manage Employees"),
        ("payroll.runs.view", "View Payroll Runs"),
        ("payroll.runs.process", "Process Payroll"),
        ("payroll.timesheets.approve", "Approve Timesheets"),
        ("payroll.reports.view", "View Payroll Reports")
    ],
    "inventory": [
        ("inventory.items.view", "View Inventory Items"),
        ("inventory.items.manage", "Manage Inventory Items"),
        ("inventory.transactions.view", "View Inventory Transactions"),
        ("inventory.adjustments.create", "Create Inventory Adjustments"),
        ("inventory.reports.view", "View Inventory Reports")
    ],
    "hrm": [
        ("hrm.employees.view", "View Employee Records"),
        ("hrm.employees.manage", "Manage Employee Records"),
        ("hrm.leave.approve", "Approve Leave Requests"),
        ("hrm.performance.manage", "Manage Performance Reviews"),
        ("hrm.reports.view", "View HRM Reports")
    ],
    "admin": [
        ("admin.users.manage", "Manage Users"),
        ("admin.roles.manage", "Manage Roles"),
        ("admin.settings.manage", "Manage System Settings"),
        ("admin.audit.view", "View Audit Logs"),
        ("admin.backup.manage", "Manage Backups")
    ]
}

# Default roles
DEFAULT_ROLES = {
    "Super Admin": {
        "description": "Full system access",
        "modules": ["gl", "ap", "ar", "tax", "payroll", "inventory", "hrm", "admin"],
        "permissions": "all"
    },
    "Accounting Manager": {
        "description": "Full accounting access",
        "modules": ["gl", "ap", "ar", "tax"],
        "permissions": "all_module"
    },
    "AP Clerk": {
        "description": "Accounts Payable clerk",
        "modules": ["ap"],
        "permissions": ["ap.vendors.view", "ap.invoices.view", "ap.invoices.create", "ap.payments.view"]
    },
    "AR Clerk": {
        "description": "Accounts Receivable clerk", 
        "modules": ["ar"],
        "permissions": ["ar.customers.view", "ar.invoices.view", "ar.invoices.create", "ar.payments.view"]
    },
    "Payroll Manager": {
        "description": "Payroll management",
        "modules": ["payroll", "hrm"],
        "permissions": "all_module"
    },
    "Inventory Manager": {
        "description": "Inventory management",
        "modules": ["inventory"],
        "permissions": "all_module"
    },
    "Read Only": {
        "description": "View-only access",
        "modules": ["gl", "ap", "ar", "tax", "payroll", "inventory", "hrm"],
        "permissions": "view_only"
    }
}