"""
Data validation service for import/export operations.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
import re



class ValidationRule:
    """Base validation rule."""
    
    def __init__(self, field: str, rule_type: str, params: Dict[str, Any] = None):
        """  Init  ."""
        self.field = field
        self.rule_type = rule_type
        self.params = params or {}
    
    def validate(self, data: Dict[str, Any]) -> Optional[str]:
        """Validate."""
        """Validate data against rule."""
        value = data.get(self.field)
        
        if self.rule_type == "required":
            if not value:
                return f"{self.field} is required"
        
        elif self.rule_type == "email":
            if value and not re.match(r'^[^@]+@[^@]+\.[^@]+$', str(value)):
                return f"{self.field} must be a valid email"
        
        elif self.rule_type == "numeric":
            if value and not str(value).replace('.', '').replace('-', '').isdigit():
                return f"{self.field} must be numeric"
        
        elif self.rule_type == "max_length":
            max_len = self.params.get("length", 255)
            if value and len(str(value)) > max_len:
                return f"{self.field} must be less than {max_len} characters"
        
        return None


class DataValidationService:
    """Service for validating data during import/export."""
    
    def __init__(self):
        """  Init  ."""
        self.validation_rules = {
            "vendors": [
                ValidationRule("name", "required"),
                ValidationRule("email", "email"),
                ValidationRule("name", "max_length", {"length": 200})
            ],
            "customers": [
                ValidationRule("name", "required"),
                ValidationRule("email", "email"),
                ValidationRule("name", "max_length", {"length": 200})
            ],
            "items": [
                ValidationRule("name", "required"),
                ValidationRule("price", "numeric"),
                ValidationRule("name", "max_length", {"length": 200})
            ]
        }
    
    def validate_record(self, data_type: str, data: Dict[str, Any]) -> List[str]:
        """Validate Record."""
        """Validate a single record."""
        errors = []
        
        if data_type not in self.validation_rules:
            return errors
        
        for rule in self.validation_rules[data_type]:
            error = rule.validate(data)
            if error:
                errors.append(error)
        
        return errors
    
    def validate_batch(self, data_type: str, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate Batch."""
        """Validate a batch of records."""
        results = {
            "total_records": len(records),
            "valid_records": 0,
            "invalid_records": 0,
            "errors": []
        }
        
        for index, record in enumerate(records):
            errors = self.validate_record(data_type, record)
            
            if errors:
                results["invalid_records"] += 1
                results["errors"].append({
                    "row": index,
                    "errors": errors
                })
            else:
                results["valid_records"] += 1
        
        return results
    
    def get_validation_schema(self, data_type: str) -> Dict[str, Any]:
        """Get Validation Schema."""
        """Get validation schema for a data type."""
        if data_type not in self.validation_rules:
            return {}
        
        schema = {}
        for rule in self.validation_rules[data_type]:
            if rule.field not in schema:
                schema[rule.field] = []
            
            schema[rule.field].append({
                "type": rule.rule_type,
                "params": rule.params
            })
        
        return schema