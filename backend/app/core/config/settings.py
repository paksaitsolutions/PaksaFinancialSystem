"""
Core application settings and configuration.
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""
    
    # App Info
    APP_NAME: str = "Paksa Financial System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./paksa_financial.db"
    )
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./paksa_financial.db"
    )
    SQLALCHEMY_POOL_SIZE: int = 5
    SQLALCHEMY_MAX_OVERFLOW: int = 10
    SQLALCHEMY_POOL_TIMEOUT: int = 30
    SQLALCHEMY_POOL_RECYCLE: int = 3600
    SQLALCHEMY_ECHO: bool = False
    
    # Read Replica Configuration
    USE_READ_REPLICA: bool = os.getenv("USE_READ_REPLICA", "false").lower() == "true"
    DATABASE_READ_REPLICA_URL: Optional[str] = os.getenv("DATABASE_READ_REPLICA_URL")
    DATABASE_REPLICA_URLS: List[str] = []
    
    # Redis (disabled for now)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL") if os.getenv("REDIS_URL") and not os.getenv("REDIS_URL").startswith("#") else None
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    USE_REDIS: bool = False
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3003", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3003"
    ]
    
    # First superuser
    FIRST_SUPERUSER_EMAIL: str = os.getenv("FIRST_SUPERUSER_EMAIL", "admin@paksa.com")
    FIRST_SUPERUSER_PASSWORD: str = os.getenv("FIRST_SUPERUSER_PASSWORD", "admin123")
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_SERVER: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Banking Integrations
    PLAID_CLIENT_ID: str = os.getenv("PLAID_CLIENT_ID", "")
    PLAID_SECRET: str = os.getenv("PLAID_SECRET", "")
    PLAID_ENVIRONMENT: str = os.getenv("PLAID_ENVIRONMENT", "sandbox")
    
    # Tax Integrations
    AVALARA_ACCOUNT_ID: str = os.getenv("AVALARA_ACCOUNT_ID", "")
    AVALARA_LICENSE_KEY: str = os.getenv("AVALARA_LICENSE_KEY", "")
    AVALARA_ENVIRONMENT: str = os.getenv("AVALARA_ENVIRONMENT", "sandbox")
    TAXJAR_API_TOKEN: str = os.getenv("TAXJAR_API_TOKEN", "")
    
    # Payment Integrations
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    PAYPAL_CLIENT_ID: str = os.getenv("PAYPAL_CLIENT_ID", "")
    PAYPAL_CLIENT_SECRET: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    
    # Notifications
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()