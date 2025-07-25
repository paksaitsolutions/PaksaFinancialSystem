"""
Application configuration management.
"""
import os
from typing import Optional, List
from pydantic import BaseSettings, validator, Field
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with proper environment-based configuration."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    TESTING: bool = Field(default=False, env="TESTING")
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./paksa_finance.db",
        env="DATABASE_URL"
    )
    DATABASE_URL_SYNC: Optional[str] = Field(default=None, env="DATABASE_URL_SYNC")
    DATABASE_READ_REPLICA_URL: Optional[str] = Field(default=None, env="DATABASE_READ_REPLICA_URL")
    USE_READ_REPLICA: bool = Field(default=False, env="USE_READ_REPLICA")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Security - Enhanced
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # Reduced for security
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Enhanced Security Settings
    ENCRYPTION_KEY: str = Field(
        default="dev-encryption-key-change-in-production",
        env="ENCRYPTION_KEY"
    )
    CSRF_SECRET_KEY: str = Field(
        default="dev-csrf-key-change-in-production",
        env="CSRF_SECRET_KEY"
    )
    SECURITY_HEADERS_ENABLED: bool = Field(default=True, env="SECURITY_HEADERS_ENABLED")
    RATE_LIMIT_STRICT_MODE: bool = Field(default=False, env="RATE_LIMIT_STRICT_MODE")
    
    # Redis
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # Email
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    SMTP_FROM_EMAIL: str = Field(default="noreply@paksa.com.pk", env="SMTP_FROM_EMAIL")
    
    # API
    API_V1_STR: str = Field(default="/api/v1", env="API_V1_STR")
    PROJECT_NAME: str = Field(default="Paksa Financial System", env="PROJECT_NAME")
    VERSION: str = Field(default="1.0.0", env="VERSION")
    
    # CORS
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    # File Storage
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    @validator("DATABASE_URL_SYNC", pre=True)
    def build_sync_db_url(cls, v: Optional[str], values: dict) -> str:
        """Build sync database URL from async URL."""
        if v:
            return v
        async_url = values.get("DATABASE_URL", "")
        if "postgresql+asyncpg://" in async_url:
            return async_url.replace("postgresql+asyncpg://", "postgresql://")
        elif "sqlite+aiosqlite://" in async_url:
            return async_url.replace("sqlite+aiosqlite://", "sqlite://")
        return async_url
    
    @validator("REDIS_URL", pre=True)
    def build_redis_url(cls, v: Optional[str], values: dict) -> str:
        """Build Redis URL if not provided."""
        if v:
            return v
        host = values.get("REDIS_HOST", "localhost")
        port = values.get("REDIS_PORT", 6379)
        db = values.get("REDIS_DB", 0)
        password = values.get("REDIS_PASSWORD")
        
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"
    
    @validator("DEBUG", "TESTING", "USE_READ_REPLICA", "SMTP_USE_TLS", "RATE_LIMIT_ENABLED", pre=True)
    def parse_bool(cls, v):
        """Parse boolean values from environment."""
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)
    
    @validator("ALLOWED_HOSTS", "CORS_ORIGINS", pre=True)
    def parse_list(cls, v):
        """Parse comma-separated lists from environment."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v
    
    @validator("UPLOAD_DIR", pre=True)
    def create_upload_dir(cls, v):
        """Create upload directory if it doesn't exist."""
        upload_path = Path(v)
        upload_path.mkdir(parents=True, exist_ok=True)
        return str(upload_path)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.TESTING or self.ENVIRONMENT.lower() == "testing"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()