"""
API v1 Endpoints Package

This package contains all the API v1 endpoint modules.
"""

# Import endpoint modules here to make them available when importing from this package
# from . import users, items, etc.
from . import payroll

# Export the payroll router
router = payroll.router
