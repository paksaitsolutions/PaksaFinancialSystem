# -*- coding: utf-8 -*-
"""
Paksa Financial System
----------------------
Version: 1.0
Author: Paksa IT Solutions
Copyright © 2023 Paksa IT Solutions

This file is part of the Paksa Financial System.
It is subject to the terms and conditions defined in
file 'LICENSE', which is part of this source code package.
"""

class BudgetException(Exception):
    """Base exception for budget module."""
    pass

class BudgetNotFound(BudgetException):
    """Raised when a budget is not found."""
    pass

class BudgetItemNotFound(BudgetException):
    """Raised when a budget item is not found."""
    pass

class InvalidBudgetDateRange(BudgetException):
    """Raised when the budget date range is invalid."""
    pass

class BudgetValidationError(BudgetException):
    """Raised for budget validation errors."""
    pass
