# Import unified budget models from core_models to eliminate duplicates
from app.models.core_models import (
    Budget,
    BudgetLineItem
)

# All budget models are now unified in core_models.py
# This file serves as a compatibility layer for existing imports