"""
Application configuration management.
"""
import os
from typing import Optional
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/paksa_financial"
    DATABASE_URL_SYNC: Optional[str] = None
    DATABASE_READ_REPLICA_URL: Optional[str] = None
    USE_READ_REPLICA: bool = False
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    @validator("DATABASE_URL_SYNC", pre=True)
    def build_sync_db_url(cls, v: Optional[str], values: dict) -> str:
        """Build sync database URL from async URL."""
        if v:
            return v
        async_url = values.get("DATABASE_URL", "")
        return async_url.replace("postgresql+asyncpg://", "postgresql://")
    
    @validator("DEBUG", pre=True)
    def parse_debug(cls, v):
        """Parse debug from environment."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()