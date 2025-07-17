"""Real-time tax compliance monitoring service."""
from datetime import datetime, timedelta
import json
import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Set

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import pytz

from app.core.config import settings
from app.models.tax_models import (
    ComplianceCheck, ComplianceRule, ComplianceAlert, TaxTransaction, TaxRate
)
from app.core.integrations.regulatory_api import RegulatoryAPIClient
from app.core.notifications import NotificationService

logger = logging.getLogger(__name__)


class ComplianceCheckType(str, Enum):
    """Types of compliance checks."""
    TRANSACTION = "transaction"
    CUSTOMER = "customer"
    VENDOR = "vendor"
    REPORT = "report"
    DOCUMENT = "document"


class ComplianceStatus(str, Enum):
    """Compliance check statuses."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"


class ComplianceCheckRequest(BaseModel):
    """Request model for compliance check."""
    check_type: ComplianceCheckType
    entity_id: str
    entity_type: str
    jurisdiction: str
    check_data: Dict[str, Any]
    rules: Optional[List[str]] = None
    priority: str = "medium"


class ComplianceCheckResult(BaseModel):
    """Result of a compliance check."""
    check_id: str
    status: ComplianceStatus
    timestamp: datetime
    entity_id: str
    entity_type: str
    check_type: ComplianceCheckType
    passed_rules: List[Dict] = Field(default_factory=list)
    failed_rules: List[Dict] = Field(default_factory=list)
    warnings: List[Dict] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    next_check: Optional[datetime] = None


class ComplianceService:
    """Service for real-time compliance monitoring."""
    
    def __init__(self, db: Session):
        self.db = db
        self.regulatory_client = RegulatoryAPIClient(
            api_key=settings.REGULATORY_API_KEY,
            environment=settings.ENV
        )
        self.notification_service = NotificationService()
        
        # Cache for rules to avoid repeated DB queries
        self._rules_cache = {}
        self._rules_cache_updated = None
        self._rules_cache_ttl = timedelta(minutes=5)
    
    async def check_compliance(
        self,
        request: ComplianceCheckRequest,
        user_id: Optional[str] = None
    ) -> ComplianceCheckResult:
        """Perform a compliance check."""
        try:
            # Get applicable rules
            rules = await self._get_applicable_rules(
                check_type=request.check_type,
                jurisdiction=request.jurisdiction,
                entity_type=request.entity_type,
                rule_ids=request.rules
            )
            
            # Initialize result
            result = ComplianceCheckResult(
                check_id=f"chk_{datetime.utcnow().timestamp()}",
                status=ComplianceStatus.PENDING,
                timestamp=datetime.utcnow(),
                entity_id=request.entity_id,
                entity_type=request.entity_type,
                check_type=request.check_type
            )
            
            # Execute rules
            for rule in rules:
                rule_result = await self._execute_rule(rule, request.check_data)
                
                if rule_result["status"] == ComplianceStatus.FAILED:
                    result.failed_rules.append(rule_result)
                elif rule_result["status"] == ComplianceStatus.WARNING:
                    result.warnings.append(rule_result)
                else:
                    result.passed_rules.append(rule_result)
            
            # Determine overall status
            if result.failed_rules:
                result.status = ComplianceStatus.FAILED
            elif result.warnings:
                result.status = ComplianceStatus.WARNING
            else:
                result.status = ComplianceStatus.PASSED
            
            # Save check result
            await self._save_check_result(result, user_id)
            
            # Generate alerts if needed
            if result.status in [ComplianceStatus.FAILED, ComplianceStatus.WARNING]:
                await self._generate_alerts(result, user_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error performing compliance check: {str(e)}")
            raise
    
    async def monitor_transaction_compliance(
        self,
        transaction: TaxTransaction,
        user_id: Optional[str] = None
    ) -> ComplianceCheckResult:
        """Monitor a transaction for compliance."""
        try:
            # Prepare check data
            check_data = {
                "transaction_id": str(transaction.id),
                "amount": float(transaction.amount),
                "currency": transaction.currency,
                "transaction_date": transaction.transaction_date.isoformat(),
                "parties": {
                    "from": transaction.from_party,
                    "to": transaction.to_party
                },
                "tax_components": [
                    {
                        "type": c.tax_type,
                        "rate": float(c.rate),
                        "amount": float(c.amount)
                    }
                    for c in transaction.components
                ]
            }
            
            # Create check request
            request = ComplianceCheckRequest(
                check_type=ComplianceCheckType.TRANSACTION,
                entity_id=str(transaction.id),
                entity_type="transaction",
                jurisdiction=transaction.jurisdiction,
                check_data=check_data,
                priority="high"
            )
            
            # Perform compliance check
            return await self.check_compliance(request, user_id)
            
        except Exception as e:
            logger.error(f"Error monitoring transaction compliance: {str(e)}")
            raise
    
    async def check_regulatory_updates(self) -> Dict:
        """Check for regulatory updates and apply compliance rules."""
        try:
            # Get latest updates from regulatory API
            updates = await self.regulatory_client.get_updates(
                since=datetime.utcnow() - timedelta(days=7)
            )
            
            results = {
                "updates_processed": 0,
                "rules_updated": 0,
                "alerts_generated": 0
            }
            
            # Process each update
            for update in updates:
                # Apply update to rules
                updated = await self._apply_regulatory_update(update)
                if updated:
                    results["rules_updated"] += 1
                
                # Generate alerts for significant changes
                if update.get("severity") in ["high", "critical"]:
                    await self._generate_regulatory_alert(update)
                    results["alerts_generated"] += 1
                
                results["updates_processed"] += 1
            
            # Clear rules cache after updates
            self._rules_cache = {}
            self._rules_cache_updated = None
            
            return results
            
        except Exception as e:
            logger.error(f"Error checking regulatory updates: {str(e)}")
            raise
    
    async def _get_applicable_rules(
        self,
        check_type: ComplianceCheckType,
        jurisdiction: str,
        entity_type: str,
        rule_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """Get applicable compliance rules."""
        try:
            cache_key = f"{check_type}:{jurisdiction}:{entity_type}"
            
            # Check cache first
            if cache_key in self._rules_cache and self._rules_cache_updated and \
               (datetime.utcnow() - self._rules_cache_updated) < self._rules_cache_ttl:
                return self._rules_cache[cache_key]
            
            # Query database for rules
            query = self.db.query(ComplianceRule).filter(
                ComplianceRule.is_active == True,
                ComplianceRule.check_type == check_type,
                ComplianceRule.jurisdiction == jurisdiction,
                ComplianceRule.entity_types.contains([entity_type])
            )
            
            if rule_ids:
                query = query.filter(ComplianceRule.id.in_(rule_ids))
            
            rules = query.all()
            
            # Cache the results
            self._rules_cache[cache_key] = rules
            self._rules_cache_updated = datetime.utcnow()
            
            return rules
            
        except Exception as e:
            logger.error(f"Error getting applicable rules: {str(e)}")
            return []
    
    async def _execute_rule(self, rule: Dict, check_data: Dict) -> Dict:
        """Execute a single compliance rule."""
        # Add rule execution logic here
        pass
    
    async def _save_check_result(
        self,
        result: ComplianceCheckResult,
        user_id: Optional[str] = None
    ) -> None:
        """Save compliance check result to database."""
        try:
            check = ComplianceCheck(
                check_id=result.check_id,
                status=result.status,
                entity_id=result.entity_id,
                entity_type=result.entity_type,
                check_type=result.check_type,
                passed_rules=result.passed_rules,
                failed_rules=result.failed_rules,
                warnings=result.warnings,
                metadata=result.metadata,
                created_by=user_id
            )
            
            self.db.add(check)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving compliance check result: {str(e)}")
            raise
    
    async def _generate_alerts(
        self,
        result: ComplianceCheckResult,
        user_id: Optional[str] = None
    ) -> None:
        """Generate compliance alerts."""
        try:
            # Create alert record
            alert = ComplianceAlert(
                title=f"Compliance {result.status} for {result.entity_type} {result.entity_id}",
                description=f"Compliance check resulted in {result.status}",
                severity="high" if result.status == ComplianceStatus.FAILED else "medium",
                status="open",
                check_id=result.check_id,
                entity_id=result.entity_id,
                entity_type=result.entity_type,
                details={
                    "passed_rules": result.passed_rules,
                    "failed_rules": result.failed_rules,
                    "warnings": result.warnings
                },
                created_by=user_id
            )
            
            self.db.add(alert)
            self.db.commit()
            
            # Send notification
            await self.notification_service.send_compliance_alert(
                alert_id=str(alert.id),
                title=alert.title,
                description=alert.description,
                severity=alert.severity,
                recipients=[user_id] if user_id else []
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating compliance alert: {str(e)}")
    
    async def _apply_regulatory_update(self, update: Dict) -> bool:
        """Apply a regulatory update to compliance rules."""
        # Add logic to update rules based on regulatory changes
        return False
    
    async def _generate_regulatory_alert(self, update: Dict) -> None:
        """Generate an alert for a regulatory update."""
        # Add logic to generate alerts for regulatory updates
        pass
