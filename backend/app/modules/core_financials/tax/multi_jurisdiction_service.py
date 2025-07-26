from typing import Dict, List, Optional
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from .models import TaxCode, TaxReturn, TaxJurisdiction, TaxRate
from .schemas import MultiJurisdictionTaxRequest, JurisdictionTaxResult

class MultiJurisdictionService:
    """Service for multi-jurisdiction tax calculations and compliance"""
    
    # Jurisdiction hierarchy levels
    JURISDICTION_LEVELS = {
        'federal': 1,
        'state': 2,
        'county': 3,
        'city': 4,
        'district': 5
    }
    
    async def calculate_multi_jurisdiction_tax(
        self,
        db: AsyncSession,
        request: MultiJurisdictionTaxRequest
    ) -> List[JurisdictionTaxResult]:
        """Calculate taxes across multiple jurisdictions"""
        
        results = []
        
        # Get all applicable jurisdictions for the location
        jurisdictions = await self._get_applicable_jurisdictions(
            db, request.state, request.county, request.city
        )
        
        for jurisdiction in jurisdictions:
            # Get tax rates for this jurisdiction
            tax_rates = await self._get_jurisdiction_tax_rates(
                db, jurisdiction.id, request.tax_period
            )
            
            jurisdiction_result = JurisdictionTaxResult(
                jurisdiction_id=jurisdiction.id,
                jurisdiction_name=jurisdiction.name,
                jurisdiction_type=jurisdiction.jurisdiction_type,
                tax_calculations=[]
            )
            
            total_tax = Decimal('0')
            
            for rate in tax_rates:
                # Calculate tax based on rate type
                tax_amount = self._calculate_tax_by_rate(
                    request.taxable_amount, rate, request.transaction_type
                )
                
                if tax_amount > 0:
                    jurisdiction_result.tax_calculations.append({
                        'tax_type': rate.tax_type,
                        'tax_rate': float(rate.rate),
                        'taxable_amount': float(request.taxable_amount),
                        'tax_amount': float(tax_amount),
                        'description': rate.description
                    })
                    total_tax += tax_amount
            
            jurisdiction_result.total_tax = total_tax
            results.append(jurisdiction_result)
        
        return results
    
    async def _get_applicable_jurisdictions(
        self,
        db: AsyncSession,
        state: str,
        county: Optional[str] = None,
        city: Optional[str] = None
    ) -> List['TaxJurisdiction']:
        """Get all applicable tax jurisdictions for a location"""
        
        jurisdictions = []
        
        # Federal jurisdiction (always applies)
        federal_result = await db.execute(
            select(TaxJurisdiction).where(
                TaxJurisdiction.jurisdiction_type == 'federal'
            )
        )
        federal_jurisdiction = federal_result.scalar_one_or_none()
        if federal_jurisdiction:
            jurisdictions.append(federal_jurisdiction)
        
        # State jurisdiction
        state_result = await db.execute(
            select(TaxJurisdiction).where(
                and_(
                    TaxJurisdiction.jurisdiction_type == 'state',
                    TaxJurisdiction.state_code == state
                )
            )
        )
        state_jurisdiction = state_result.scalar_one_or_none()
        if state_jurisdiction:
            jurisdictions.append(state_jurisdiction)
        
        # County jurisdiction
        if county:
            county_result = await db.execute(
                select(TaxJurisdiction).where(
                    and_(
                        TaxJurisdiction.jurisdiction_type == 'county',
                        TaxJurisdiction.state_code == state,
                        TaxJurisdiction.county_name == county
                    )
                )
            )
            county_jurisdiction = county_result.scalar_one_or_none()
            if county_jurisdiction:
                jurisdictions.append(county_jurisdiction)
        
        # City jurisdiction
        if city:
            city_result = await db.execute(
                select(TaxJurisdiction).where(
                    and_(
                        TaxJurisdiction.jurisdiction_type == 'city',
                        TaxJurisdiction.state_code == state,
                        TaxJurisdiction.city_name == city
                    )
                )
            )
            city_jurisdiction = city_result.scalar_one_or_none()
            if city_jurisdiction:
                jurisdictions.append(city_jurisdiction)
        
        # Special districts (if any)
        district_result = await db.execute(
            select(TaxJurisdiction).where(
                and_(
                    TaxJurisdiction.jurisdiction_type == 'district',
                    TaxJurisdiction.state_code == state,
                    TaxJurisdiction.is_active == True
                )
            )
        )
        district_jurisdictions = district_result.scalars().all()
        jurisdictions.extend(district_jurisdictions)
        
        return jurisdictions
    
    async def _get_jurisdiction_tax_rates(
        self,
        db: AsyncSession,
        jurisdiction_id: int,
        tax_period: date
    ) -> List['TaxRate']:
        """Get active tax rates for a jurisdiction"""
        
        result = await db.execute(
            select(TaxRate).where(
                and_(
                    TaxRate.jurisdiction_id == jurisdiction_id,
                    TaxRate.effective_date <= tax_period,
                    TaxRate.is_active == True
                )
            ).order_by(TaxRate.effective_date.desc())
        )
        
        return result.scalars().all()
    
    def _calculate_tax_by_rate(
        self,
        taxable_amount: Decimal,
        rate: 'TaxRate',
        transaction_type: str
    ) -> Decimal:
        """Calculate tax amount based on rate configuration"""
        
        # Check if rate applies to this transaction type
        if rate.applicable_transaction_types:
            applicable_types = rate.applicable_transaction_types.split(',')
            if transaction_type not in applicable_types:
                return Decimal('0')
        
        # Apply minimum threshold
        if rate.minimum_threshold and taxable_amount < rate.minimum_threshold:
            return Decimal('0')
        
        # Apply maximum threshold
        if rate.maximum_threshold and taxable_amount > rate.maximum_threshold:
            taxable_amount = rate.maximum_threshold
        
        # Calculate tax based on rate type
        if rate.rate_type == 'percentage':
            tax_amount = taxable_amount * (rate.rate / 100)
        elif rate.rate_type == 'flat':
            tax_amount = rate.rate
        elif rate.rate_type == 'tiered':
            tax_amount = self._calculate_tiered_tax(taxable_amount, rate)
        else:
            tax_amount = Decimal('0')
        
        # Apply minimum and maximum tax amounts
        if rate.minimum_tax and tax_amount < rate.minimum_tax:
            tax_amount = rate.minimum_tax
        
        if rate.maximum_tax and tax_amount > rate.maximum_tax:
            tax_amount = rate.maximum_tax
        
        return tax_amount
    
    def _calculate_tiered_tax(self, taxable_amount: Decimal, rate: 'TaxRate') -> Decimal:
        """Calculate tiered tax (progressive rates)"""
        # Simplified tiered calculation
        # In production, would parse tier configuration from rate.tier_configuration
        
        # Example tiers for demonstration
        tiers = [
            {'min': 0, 'max': 10000, 'rate': 0.01},
            {'min': 10000, 'max': 50000, 'rate': 0.02},
            {'min': 50000, 'max': None, 'rate': 0.03}
        ]
        
        total_tax = Decimal('0')
        remaining_amount = taxable_amount
        
        for tier in tiers:
            tier_min = Decimal(str(tier['min']))
            tier_max = Decimal(str(tier['max'])) if tier['max'] else None
            tier_rate = Decimal(str(tier['rate']))
            
            if remaining_amount <= 0:
                break
            
            if taxable_amount <= tier_min:
                continue
            
            # Calculate taxable amount for this tier
            tier_taxable = remaining_amount
            if tier_max and (tier_min + remaining_amount) > tier_max:
                tier_taxable = tier_max - tier_min
            
            # Calculate tax for this tier
            tier_tax = tier_taxable * tier_rate
            total_tax += tier_tax
            remaining_amount -= tier_taxable
        
        return total_tax
    
    async def get_jurisdiction_compliance_summary(
        self,
        db: AsyncSession,
        company_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, any]:
        """Get compliance summary across all jurisdictions"""
        
        # Get all tax returns filed in the period
        returns_result = await db.execute(
            select(TaxReturn).where(
                and_(
                    TaxReturn.company_id == company_id,
                    TaxReturn.filing_date >= start_date,
                    TaxReturn.filing_date <= end_date
                )
            )
        )
        tax_returns = returns_result.scalars().all()
        
        # Group by jurisdiction
        jurisdiction_summary = {}
        
        for tax_return in tax_returns:
            jurisdiction = tax_return.jurisdiction_name or 'Unknown'
            
            if jurisdiction not in jurisdiction_summary:
                jurisdiction_summary[jurisdiction] = {
                    'returns_filed': 0,
                    'total_tax_due': Decimal('0'),
                    'total_tax_paid': Decimal('0'),
                    'outstanding_balance': Decimal('0'),
                    'compliance_status': 'compliant'
                }
            
            summary = jurisdiction_summary[jurisdiction]
            summary['returns_filed'] += 1
            summary['total_tax_due'] += tax_return.tax_due or Decimal('0')
            summary['total_tax_paid'] += tax_return.tax_paid or Decimal('0')
            
            outstanding = (tax_return.tax_due or Decimal('0')) - (tax_return.tax_paid or Decimal('0'))
            summary['outstanding_balance'] += outstanding
            
            # Check compliance status
            if outstanding > 0 and tax_return.due_date < date.today():
                summary['compliance_status'] = 'overdue'
            elif tax_return.filing_status == 'draft':
                summary['compliance_status'] = 'pending'
        
        return {
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
            'total_jurisdictions': len(jurisdiction_summary),
            'jurisdiction_summary': {
                k: {
                    **v,
                    'total_tax_due': float(v['total_tax_due']),
                    'total_tax_paid': float(v['total_tax_paid']),
                    'outstanding_balance': float(v['outstanding_balance'])
                }
                for k, v in jurisdiction_summary.items()
            }
        }
    
    async def validate_jurisdiction_requirements(
        self,
        db: AsyncSession,
        jurisdiction_id: int,
        transaction_data: Dict
    ) -> Dict[str, any]:
        """Validate transaction against jurisdiction requirements"""
        
        # Get jurisdiction details
        jurisdiction_result = await db.execute(
            select(TaxJurisdiction).where(TaxJurisdiction.id == jurisdiction_id)
        )
        jurisdiction = jurisdiction_result.scalar_one_or_none()
        
        if not jurisdiction:
            return {'valid': False, 'errors': ['Jurisdiction not found']}
        
        validation_errors = []
        warnings = []
        
        # Check registration requirements
        if jurisdiction.requires_registration and not transaction_data.get('registration_number'):
            validation_errors.append(f"Registration required for {jurisdiction.name}")
        
        # Check minimum transaction thresholds
        if jurisdiction.minimum_transaction_amount:
            transaction_amount = Decimal(str(transaction_data.get('amount', 0)))
            if transaction_amount < jurisdiction.minimum_transaction_amount:
                warnings.append(f"Transaction below minimum threshold for {jurisdiction.name}")
        
        # Check filing frequency requirements
        if jurisdiction.required_filing_frequency:
            # This would check against actual filing history
            pass
        
        return {
            'valid': len(validation_errors) == 0,
            'errors': validation_errors,
            'warnings': warnings,
            'jurisdiction_name': jurisdiction.name,
            'jurisdiction_type': jurisdiction.jurisdiction_type
        }