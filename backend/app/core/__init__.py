"""
Paksa Financial System - Core Package
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This is the core package for the Paksa Financial System.
"""

# Import database components from their respective modules
from sqlalchemy import Column, DateTime, Text, func, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, AsyncConnection
from sqlalchemy.orm import sessionmaker, declarative_base, declared_attr

# Define naming convention for database constraints
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=NAMING_CONVENTION)

# Import all database components from the db package
from app.core.db import (
    # Base models
    Base,
    BaseModel,
    
    # Session management
    SessionLocal,
    async_session_factory,
    get_db,
    get_db_session,
    get_db_context,
    SessionType,
    
    # Initialization
    init_db,
    seed_database,
    seed_users,
    
    # Database URL utilities
    get_database_url,
    validate_database_url
)

# For backward compatibility
get_db_sync = get_db_session  # Alias for backward compatibility
