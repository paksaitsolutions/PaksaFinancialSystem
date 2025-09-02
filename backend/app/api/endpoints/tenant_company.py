from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from app.schemas.tenant_company import (
    TenantCompanyCreate, TenantCompanyUpdate, TenantCompanyInDB, TenantCompanyResponse,
    CompanyStats, CompanyActivationRequest, CompanyActivationResponse,
    CompanyModuleCreate, CompanyModuleUpdate, CompanyModuleInDB
)
from app.models.tenant_company import TenantCompany, CompanyAdmin, CompanyModule, CompanySubscription
from app.models.user import User
from app.models.company_settings import CompanySettings
from app.core.deps import get_db, get_current_user
from app.services.auth_service import create_access_token, get_password_hash
from app.services.tenant_service import TenantService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/companies", response_model=List[TenantCompanyResponse])
def get_companies(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    plan: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all companies with optional filtering"""
    try:
        query = db.query(TenantCompany)
        
        # Apply filters
        if status:
            query = query.filter(TenantCompany.status == status)
        if plan:
            query = query.filter(TenantCompany.plan == plan)
        if search:
            query = query.filter(
                TenantCompany.name.ilike(f"%{search}%") |
                TenantCompany.code.ilike(f"%{search}%") |
                TenantCompany.domain.ilike(f"%{search}%")
            )
        
        companies = query.offset(skip).limit(limit).all()
        
        # Calculate additional fields for response
        response_companies = []
        for company in companies:
            company_dict = company.__dict__.copy()
            company_dict['users_percentage'] = (
                (company.current_users / company.max_users * 100) 
                if company.max_users > 0 else 0
            )
            response_companies.append(TenantCompanyResponse(**company_dict))
        
        return response_companies
    except Exception as e:
        logger.error(f"Error fetching companies: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/companies/{company_id}", response_model=TenantCompanyResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific company by ID"""
    try:
        company = db.query(TenantCompany).filter(TenantCompany.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        company_dict = company.__dict__.copy()
        company_dict['users_percentage'] = (
            (company.current_users / company.max_users * 100) 
            if company.max_users > 0 else 0
        )
        
        return TenantCompanyResponse(**company_dict)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company {company_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/companies", response_model=TenantCompanyResponse)
def register_company(
    company_data: TenantCompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register a new company with admin user"""
    try:
        # Check if company code or subdomain already exists
        existing_company = db.query(TenantCompany).filter(
            (TenantCompany.code == company_data.code) |
            (TenantCompany.subdomain == company_data.subdomain)
        ).first()
        
        if existing_company:
            raise HTTPException(
                status_code=400, 
                detail="Company code or subdomain already exists"
            )
        
        # Check if admin email already exists
        existing_user = db.query(User).filter(User.email == company_data.admin_email).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Admin email already exists"
            )
        
        # Create company
        company = TenantCompany(
            name=company_data.name,
            code=company_data.code,
            industry=company_data.industry,
            size=company_data.size,
            address=company_data.address,
            domain=f"{company_data.subdomain}.paksa.com",
            subdomain=company_data.subdomain,
            logo_url=company_data.logo_url,
            primary_color=company_data.primary_color,
            secondary_color=company_data.secondary_color,
            plan=company_data.plan,
            max_users=company_data.max_users,
            current_users=1,  # Admin user
            storage_limit_gb=company_data.storage_limit_gb,
            api_rate_limit=company_data.api_rate_limit,
            timezone=company_data.timezone,
            language=company_data.language,
            currency=company_data.currency,
            date_format=company_data.date_format,
            enabled_modules=company_data.enabled_modules or ['gl', 'ap', 'ar'],
            feature_flags=company_data.feature_flags or {},
            custom_settings=company_data.custom_settings or {},\n            status='Active',\n            is_active=True,\n            created_by=current_user.id\n        )\n        \n        # Set trial period if specified\n        if company_data.trial_days:\n            company.status = 'Trial'\n            company.trial_ends_at = datetime.utcnow() + timedelta(days=company_data.trial_days)\n        \n        db.add(company)\n        db.flush()  # Get company ID\n        \n        # Create admin user\n        admin_user = User(\n            email=company_data.admin_email,\n            full_name=company_data.admin_name,\n            hashed_password=get_password_hash(company_data.admin_password),\n            phone=company_data.admin_phone,\n            is_active=True,\n            is_superuser=False,\n            company_id=company.id,\n            role='company_admin'\n        )\n        \n        db.add(admin_user)\n        db.flush()  # Get user ID\n        \n        # Create company admin relationship\n        company_admin = CompanyAdmin(\n            company_id=company.id,\n            user_id=admin_user.id,\n            role='owner',\n            is_primary=True\n        )\n        \n        db.add(company_admin)\n        \n        # Create default company settings\n        company_settings = CompanySettings(\n            company_id=company.id,\n            company_name=company.name,\n            company_code=company.code,\n            base_currency=company.currency,\n            timezone=company.timezone,\n            language=company.language,\n            date_format=company.date_format\n        )\n        \n        db.add(company_settings)\n        \n        # Enable default modules\n        default_modules = [\n            {'name': 'gl', 'display_name': 'General Ledger'},\n            {'name': 'ap', 'display_name': 'Accounts Payable'},\n            {'name': 'ar', 'display_name': 'Accounts Receivable'},\n            {'name': 'cash', 'display_name': 'Cash Management'},\n            {'name': 'reports', 'display_name': 'Financial Reports'}\n        ]\n        \n        for module in default_modules:\n            company_module = CompanyModule(\n                company_id=company.id,\n                module_name=module['name'],\n                is_enabled=True,\n                configuration={'display_name': module['display_name']},\n                license_type='included'\n            )\n            db.add(company_module)\n        \n        db.commit()\n        db.refresh(company)\n        \n        logger.info(f"Company {company.name} registered successfully with ID {company.id}")\n        \n        # Prepare response\n        company_dict = company.__dict__.copy()\n        company_dict['users_percentage'] = (\n            (company.current_users / company.max_users * 100) \n            if company.max_users > 0 else 0\n        )\n        \n        return TenantCompanyResponse(**company_dict)\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f"Error registering company: {str(e)}")\n        db.rollback()\n        raise HTTPException(status_code=500, detail="Failed to register company")

@router.put("/companies/{company_id}", response_model=TenantCompanyResponse)
def update_company(\n    company_id: int,\n    company_data: TenantCompanyUpdate,\n    db: Session = Depends(get_db),\n    current_user: User = Depends(get_current_user)\n):\n    """Update company information"""\n    try:\n        company = db.query(TenantCompany).filter(TenantCompany.id == company_id).first()\n        if not company:\n            raise HTTPException(status_code=404, detail="Company not found")\n        \n        # Update only provided fields\n        update_data = company_data.dict(exclude_unset=True)\n        for field, value in update_data.items():\n            if hasattr(company, field):\n                setattr(company, field, value)\n        \n        company.updated_at = datetime.utcnow()\n        \n        db.commit()\n        db.refresh(company)\n        \n        logger.info(f"Company {company.name} updated successfully")\n        \n        company_dict = company.__dict__.copy()\n        company_dict['users_percentage'] = (\n            (company.current_users / company.max_users * 100) \n            if company.max_users > 0 else 0\n        )\n        \n        return TenantCompanyResponse(**company_dict)\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f"Error updating company {company_id}: {str(e)}")\n        db.rollback()\n        raise HTTPException(status_code=500, detail="Failed to update company")

@router.post("/companies/{company_id}/activate", response_model=CompanyActivationResponse)
def activate_company(\n    company_id: int,\n    db: Session = Depends(get_db),\n    current_user: User = Depends(get_current_user)\n):\n    """Activate a company and switch context to it"""\n    try:\n        company = db.query(TenantCompany).filter(TenantCompany.id == company_id).first()\n        if not company:\n            raise HTTPException(status_code=404, detail="Company not found")\n        \n        if not company.is_active:\n            raise HTTPException(status_code=400, detail="Company is not active")\n        \n        # Check if user has access to this company\n        user_access = db.query(CompanyAdmin).filter(\n            CompanyAdmin.company_id == company_id,\n            CompanyAdmin.user_id == current_user.id\n        ).first()\n        \n        if not user_access and not current_user.is_superuser:\n            raise HTTPException(status_code=403, detail="Access denied to this company")\n        \n        # Update user's current company\n        current_user.company_id = company_id\n        db.commit()\n        \n        # Generate new access token with company context\n        access_token = create_access_token(\n            data={\n                "sub": current_user.email,\n                "company_id": company_id,\n                "company_code": company.code\n            }\n        )\n        \n        logger.info(f"User {current_user.email} activated company {company.name}")\n        \n        company_dict = company.__dict__.copy()\n        company_dict['users_percentage'] = (\n            (company.current_users / company.max_users * 100) \n            if company.max_users > 0 else 0\n        )\n        \n        return CompanyActivationResponse(\n            success=True,\n            message=f"Successfully activated {company.name}",\n            company=TenantCompanyResponse(**company_dict),\n            access_token=access_token\n        )\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f"Error activating company {company_id}: {str(e)}")\n        raise HTTPException(status_code=500, detail="Failed to activate company")

@router.delete("/companies/{company_id}")
def delete_company(\n    company_id: int,\n    db: Session = Depends(get_db),\n    current_user: User = Depends(get_current_user)\n):\n    """Delete a company (soft delete)"""\n    try:\n        company = db.query(TenantCompany).filter(TenantCompany.id == company_id).first()\n        if not company:\n            raise HTTPException(status_code=404, detail="Company not found")\n        \n        # Soft delete - mark as inactive\n        company.is_active = False\n        company.status = 'Inactive'\n        company.updated_at = datetime.utcnow()\n        \n        # Deactivate all users in the company\n        db.query(User).filter(User.company_id == company_id).update(\n            {User.is_active: False}\n        )\n        \n        db.commit()\n        \n        logger.info(f"Company {company.name} deleted successfully")\n        \n        return {"message": f"Company {company.name} has been deleted"}\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f"Error deleting company {company_id}: {str(e)}")\n        db.rollback()\n        raise HTTPException(status_code=500, detail="Failed to delete company")

@router.get("/companies/stats", response_model=CompanyStats)
def get_company_stats(\n    db: Session = Depends(get_db),\n    current_user: User = Depends(get_current_user)\n):\n    """Get company statistics"""\n    try:\n        total_companies = db.query(TenantCompany).count()\n        active_companies = db.query(TenantCompany).filter(TenantCompany.status == 'Active').count()\n        trial_companies = db.query(TenantCompany).filter(TenantCompany.status == 'Trial').count()\n        suspended_companies = db.query(TenantCompany).filter(TenantCompany.status == 'Suspended').count()\n        total_users = db.query(User).filter(User.is_active == True).count()\n        \n        # Companies by plan\n        plan_stats = db.query(TenantCompany.plan, db.func.count(TenantCompany.id)).group_by(TenantCompany.plan).all()\n        companies_by_plan = {plan: count for plan, count in plan_stats}\n        \n        # Companies by status\n        status_stats = db.query(TenantCompany.status, db.func.count(TenantCompany.id)).group_by(TenantCompany.status).all()\n        companies_by_status = {status: count for status, count in status_stats}\n        \n        return CompanyStats(\n            total_companies=total_companies,\n            active_companies=active_companies,\n            trial_companies=trial_companies,\n            suspended_companies=suspended_companies,\n            total_users=total_users,\n            companies_by_plan=companies_by_plan,\n            companies_by_status=companies_by_status\n        )\n        \n    except Exception as e:\n        logger.error(f"Error fetching company stats: {str(e)}")\n        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@router.post("/companies/{company_id}/logo")
async def upload_company_logo(\n    company_id: int,\n    file: UploadFile = File(...),\n    db: Session = Depends(get_db),\n    current_user: User = Depends(get_current_user)\n):\n    """Upload company logo"""\n    try:\n        company = db.query(TenantCompany).filter(TenantCompany.id == company_id).first()\n        if not company:\n            raise HTTPException(status_code=404, detail="Company not found")\n        \n        # Validate file type\n        if not file.content_type.startswith('image/'):\n            raise HTTPException(status_code=400, detail="File must be an image")\n        \n        # TODO: Implement file upload to cloud storage (S3, etc.)\n        # For now, we'll just return a placeholder URL\n        logo_url = f"/uploads/logos/{company_id}/{file.filename}"\n        \n        company.logo_url = logo_url\n        company.updated_at = datetime.utcnow()\n        \n        db.commit()\n        \n        return {"message": "Logo uploaded successfully", "logo_url": logo_url}\n        \n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f"Error uploading logo for company {company_id}: {str(e)}")\n        raise HTTPException(status_code=500, detail="Failed to upload logo")

@router.get("/companies/{company_id}/modules", response_model=List[CompanyModuleInDB])
def get_company_modules(\n    company_id: int,\n    db: Session = Depends(get_db),\n    current_user: User = Depends(get_current_user)\n):\n    """Get all modules for a company"""\n    try:\n        modules = db.query(CompanyModule).filter(CompanyModule.company_id == company_id).all()\n        return modules\n    except Exception as e:\n        logger.error(f"Error fetching modules for company {company_id}: {str(e)}")\n        raise HTTPException(status_code=500, detail="Failed to fetch modules")

@router.post("/companies/{company_id}/modules", response_model=CompanyModuleInDB)
def add_company_module(\n    company_id: int,\n    module_data: CompanyModuleCreate,\n    db: Session = Depends(get_db),\n    current_user: User = Depends(get_current_user)\n):\n    """Add a module to a company"""\n    try:\n        # Check if module already exists\n        existing_module = db.query(CompanyModule).filter(\n            CompanyModule.company_id == company_id,\n            CompanyModule.module_name == module_data.module_name\n        ).first()\n        \n        if existing_module:\n            raise HTTPException(status_code=400, detail="Module already exists for this company")\n        \n        module = CompanyModule(**module_data.dict())\n        db.add(module)\n        db.commit()\n        db.refresh(module)\n        \n        return module\n    except HTTPException:\n        raise\n    except Exception as e:\n        logger.error(f"Error adding module to company {company_id}: {str(e)}")\n        db.rollback()\n        raise HTTPException(status_code=500, detail="Failed to add module")