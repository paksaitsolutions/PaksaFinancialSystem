"""
Paksa Financial System - Compliance & Security Module
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

This module handles compliance and security features including:
- Audit logging
- Data protection (GDPR/CCPA)
- Encryption services
- Security policies
- Access controls
"""

from . import models, schemas, services, exceptions, api
from .models import *
from .schemas import *
from .services import *

__all__ = [
    # Models
    'models',
    
    # Schemas
    'schemas',
    
    # Services
    'services',
    
    # Exceptions
    'exceptions',
    
    # API
    'api',
]

# Initialize the module
def init_module():
    """Initialize the compliance module"""
    # Any module initialization code can go here
    pass
