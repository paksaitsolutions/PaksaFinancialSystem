from decimal import Decimal
from datetime import date
from typing import Dict, Any
from .models import FixedAsset, DepreciationMethod

class AdvancedDepreciationService:
    """Service for advanced depreciation calculations"""
    
    def calculate_units_of_production_depreciation(
        self,
        asset: FixedAsset,
        units_produced: int,
        total_estimated_units: int
    ) -> Decimal:
        """Calculate depreciation using units of production method"""
        
        if total_estimated_units <= 0:
            return Decimal('0')
        
        depreciable_amount = asset.purchase_cost - asset.salvage_value
        depreciation_per_unit = depreciable_amount / total_estimated_units
        
        return depreciation_per_unit * units_produced
    
    def calculate_sum_of_years_digits_depreciation(
        self,
        asset: FixedAsset,
        current_year: int
    ) -> Decimal:
        """Calculate depreciation using sum of years digits method"""
        
        useful_life = asset.useful_life_years
        sum_of_years = useful_life * (useful_life + 1) / 2
        
        remaining_years = useful_life - current_year + 1
        depreciation_rate = Decimal(remaining_years) / Decimal(sum_of_years)
        
        depreciable_amount = asset.purchase_cost - asset.salvage_value
        return depreciable_amount * depreciation_rate
    
    def calculate_double_declining_balance_depreciation(
        self,
        asset: FixedAsset,
        current_book_value: Decimal
    ) -> Decimal:
        """Calculate depreciation using double declining balance method"""
        
        rate = Decimal('2') / asset.useful_life_years
        annual_depreciation = current_book_value * rate
        
        # Ensure we don't depreciate below salvage value
        remaining_depreciable = current_book_value - asset.salvage_value
        return min(annual_depreciation, remaining_depreciable)
    
    def get_depreciation_schedule(
        self,
        asset: FixedAsset,
        method: DepreciationMethod = None
    ) -> Dict[str, Any]:
        """Generate complete depreciation schedule for an asset"""
        
        method = method or asset.depreciation_method
        schedule = []
        
        current_book_value = asset.purchase_cost
        accumulated_depreciation = Decimal('0')
        
        for year in range(1, asset.useful_life_years + 1):
            if method == DepreciationMethod.STRAIGHT_LINE:
                annual_depreciation = (asset.purchase_cost - asset.salvage_value) / asset.useful_life_years
            
            elif method == DepreciationMethod.DECLINING_BALANCE:
                annual_depreciation = self.calculate_double_declining_balance_depreciation(
                    asset, current_book_value
                )
            
            elif method == DepreciationMethod.UNITS_OF_PRODUCTION:
                # For schedule, assume equal production each year
                estimated_annual_units = 1000  # This would come from asset configuration
                total_estimated_units = estimated_annual_units * asset.useful_life_years
                annual_depreciation = self.calculate_units_of_production_depreciation(
                    asset, estimated_annual_units, total_estimated_units
                )
            
            else:
                annual_depreciation = Decimal('0')
            
            # Ensure we don't go below salvage value
            if accumulated_depreciation + annual_depreciation > (asset.purchase_cost - asset.salvage_value):
                annual_depreciation = (asset.purchase_cost - asset.salvage_value) - accumulated_depreciation
            
            accumulated_depreciation += annual_depreciation
            current_book_value = asset.purchase_cost - accumulated_depreciation
            
            schedule.append({
                "year": year,
                "beginning_book_value": float(current_book_value + annual_depreciation),
                "depreciation_expense": float(annual_depreciation),
                "accumulated_depreciation": float(accumulated_depreciation),
                "ending_book_value": float(current_book_value)
            })
            
            # Stop if we've reached salvage value
            if current_book_value <= asset.salvage_value:
                break
        
        return {
            "asset_id": asset.id,
            "asset_name": asset.name,
            "purchase_cost": float(asset.purchase_cost),
            "salvage_value": float(asset.salvage_value),
            "useful_life_years": asset.useful_life_years,
            "depreciation_method": method.value,
            "schedule": schedule,
            "total_depreciation": float(asset.purchase_cost - asset.salvage_value)
        }