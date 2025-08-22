"""Configuration validation and feature flags"""
from pydantic import BaseSettings, validator
from typing import Optional, List
import os
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class DatabaseConfig(BaseSettings):
    """Database configuration with validation"""
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    
    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        if not v or not v.startswith(('postgresql://', 'postgresql+asyncpg://')):
            raise ValueError('DATABASE_URL must be a valid PostgreSQL connection string')
        return v

class SecurityConfig(BaseSettings):
    """Security configuration with validation"""
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    BCRYPT_ROUNDS: int = 12
    
    @validator('SECRET_KEY', 'JWT_SECRET_KEY')
    def validate_secrets(cls, v):
        if not v or len(v) < 32:
            raise ValueError('Secret keys must be at least 32 characters long')
        return v

class FeatureFlags(BaseSettings):
    """Feature flags for enabling/disabling functionality"""
    ENABLE_AI_FEATURES: bool = True
    ENABLE_MULTI_TENANT: bool = True
    ENABLE_AUDIT_LOGGING: bool = True
    ENABLE_RATE_LIMITING: bool = True
    ENABLE_CACHING: bool = True
    ENABLE_BACKGROUND_JOBS: bool = True
    
    class Config:
        env_prefix = "FEATURE_"

class AppConfig(BaseSettings):
    """Main application configuration"""
    APP_NAME: str = "Paksa Financial System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    
    # Database
    database: DatabaseConfig = DatabaseConfig()
    
    # Security
    security: SecurityConfig = SecurityConfig()
    
    # Features
    features: FeatureFlags = FeatureFlags()
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".pdf", ".xlsx", ".csv", ".jpg", ".png"]
    
    @validator('ENVIRONMENT')
    def validate_environment(cls, v):
        if v == Environment.PRODUCTION and cls.DEBUG:
            raise ValueError('DEBUG cannot be True in production')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global configuration instance
config = AppConfig()

def validate_configuration():
    """Validate all configuration settings"""
    try:
        # Test database connection
        if not config.database.DATABASE_URL:
            raise ValueError("DATABASE_URL is required")
        
        # Validate security settings
        if config.ENVIRONMENT == Environment.PRODUCTION:
            if config.DEBUG:
                raise ValueError("DEBUG must be False in production")
            if len(config.security.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
        
        # Validate feature flags
        if config.features.ENABLE_MULTI_TENANT and not config.features.ENABLE_AUDIT_LOGGING:
            raise ValueError("Audit logging is required when multi-tenant is enabled")
        
        return True
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False