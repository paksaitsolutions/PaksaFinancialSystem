from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from ..schemas.company import Company, CompanyStatus, SubscriptionTier, CompanyUsage

class SuperAdminService:
    def __init__(self):
        self._companies = {}
        self._usage_stats = {}
        self._system_config = {
            "max_users_free": 5,
            "max_users_basic": 25,
            "max_users_premium": 100,
            "max_storage_gb": {"free": 1, "basic": 10, "premium": 100, "enterprise": 1000}
        }
        self._init_mock_data()
    
    def _init_mock_data(self):
        """Initialize with mock company data"""
        companies = [
            {
                "id": uuid4(),
                "name": "ABC Corporation",
                "email": "admin@abc.com",
                "status": CompanyStatus.ACTIVE,
                "subscription_tier": SubscriptionTier.PREMIUM,
                "user_count": 45,
                "storage_used": 25.5,
                "created_at": datetime.now() - timedelta(days=120),
                "last_active": datetime.now() - timedelta(hours=2),
                "monthly_revenue": 299.0
            },
            {
                "id": uuid4(),
                "name": "XYZ Startup",
                "email": "admin@xyz.com",
                "status": CompanyStatus.PENDING,
                "subscription_tier": SubscriptionTier.FREE,
                "user_count": 3,
                "storage_used": 0.8,
                "created_at": datetime.now() - timedelta(days=5),
                "last_active": datetime.now() - timedelta(hours=6),
                "monthly_revenue": 0.0
            }
        ]
        
        for company_data in companies:
            company = Company(**company_data)
            self._companies[company.id] = company
            self._usage_stats[company.id] = CompanyUsage(
                company_id=company.id,
                api_calls=12500,
                storage_gb=company.storage_used,
                active_users=company.user_count,
                transactions_count=8750,
                last_updated=datetime.now()
            )
    
    def get_all_companies(self) -> List[Company]:
        """Get all registered companies"""
        return list(self._companies.values())
    
    def approve_company(self, company_id: UUID) -> Optional[Company]:
        """Approve a pending company"""
        if company_id in self._companies:
            self._companies[company_id].status = CompanyStatus.ACTIVE
            return self._companies[company_id]
        return None
    
    def suspend_company(self, company_id: UUID, reason: str = "") -> Optional[Company]:
        """Suspend a company"""
        if company_id in self._companies:
            self._companies[company_id].status = CompanyStatus.SUSPENDED
            return self._companies[company_id]
        return None
    
    def get_company_usage(self, company_id: UUID) -> Optional[CompanyUsage]:
        """Get usage statistics for a company"""
        return self._usage_stats.get(company_id)
    
    def get_platform_analytics(self) -> Dict[str, Any]:
        """Get platform-wide analytics"""
        companies = list(self._companies.values())
        
        return {
            "total_companies": len(companies),
            "active_companies": len([c for c in companies if c.status == CompanyStatus.ACTIVE]),
            "pending_companies": len([c for c in companies if c.status == CompanyStatus.PENDING]),
            "suspended_companies": len([c for c in companies if c.status == CompanyStatus.SUSPENDED]),
            "total_users": sum(c.user_count for c in companies),
            "total_storage_gb": sum(c.storage_used for c in companies),
            "monthly_revenue": sum(c.monthly_revenue for c in companies),
            "subscription_breakdown": self._get_subscription_breakdown()
        }
    
    def _get_subscription_breakdown(self) -> Dict[str, int]:
        """Get breakdown of companies by subscription tier"""
        breakdown = {tier.value: 0 for tier in SubscriptionTier}
        for company in self._companies.values():
            breakdown[company.subscription_tier.value] += 1
        return breakdown
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        return {
            "status": "healthy",
            "uptime": "99.9%",
            "response_time_ms": 145,
            "error_rate": 0.02,
            "active_connections": 1247,
            "memory_usage": 68.5,
            "cpu_usage": 23.1,
            "disk_usage": 45.2
        }
    
    def update_global_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update global system configuration"""
        self._system_config.update(config)
        return self._system_config
    
    def get_global_config(self) -> Dict[str, Any]:
        """Get current global configuration"""
        return self._system_config.copy()