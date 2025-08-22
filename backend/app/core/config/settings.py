"""
Application configuration settings.
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TypeVar
from urllib.parse import urlparse, quote_plus
import re

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
    field_serializer,
    HttpUrl
)
from pydantic_settings import BaseSettings

def validate_database_url(url: str) -> str:
    """Validate database URL format."""
    if not url:
        raise ValueError("Database URL cannot be empty")
    
    # Check if it's a SQLite URL
    if url.startswith("sqlite"):
        if not url.startswith("sqlite:///"):
            raise ValueError("SQLite URL must start with 'sqlite:///'")
        return url
    
    # For other databases, validate the URL format
    try:
        result = urlparse(url)
        if not all([result.scheme, result.path]):
            raise ValueError("Invalid database URL format")
        return url
    except Exception as e:
        raise ValueError(f"Invalid database URL: {e}")

class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    PROJECT_NAME: str = "Paksa Financial System"
    PROJECT_DESCRIPTION: str = "Comprehensive financial management platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    API_VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Default React dev server
        "http://localhost:8000",  # Default FastAPI dev server
    ]
    
    # Database
    DB_ENGINE: str = "sqlite"
    POSTGRES_DB: str = "paksa_finance"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    SQLITE_DB_PATH: str = "./instance/paksa_finance.db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 300
    DB_ECHO: bool = False
    DATABASE_URI: str = ""
    USE_READ_REPLICA: bool = False
    DATABASE_READ_REPLICA_URL: Optional[str] = None
    
    # SQLAlchemy
    SQLALCHEMY_POOL_SIZE: int = 5
    SQLALCHEMY_MAX_OVERFLOW: int = 10
    SQLALCHEMY_POOL_TIMEOUT: int = 30
    SQLALCHEMY_POOL_RECYCLE: int = 3600
    SQLALCHEMY_ECHO: bool = False
    
    # First Superuser
    FIRST_SUPERUSER_EMAIL: EmailStr = "admin@paksa.finance"
    FIRST_SUPERUSER_PASSWORD: str = "changeme"
    FIRST_SUPERUSER_FULL_NAME: str = "Admin"
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # File Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "application/pdf", "text/csv"]
    
    # Security Headers
    SECURE_CONTENT_TYPE_NOSNIFF: bool = True
    SECURE_BROWSER_XSS_FILTER: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SECURE: bool = not bool(os.getenv("DEV_MODE"))
    SESSION_COOKIE_SAMESITE: str = "lax"
    
    # Rate Limiting
    RATE_LIMIT: str = "100/minute"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    TESTING: bool = os.getenv("TESTING", "False").lower() in ("true", "1", "t")
    
    # API Documentation
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"
    OPENAPI_URL: Optional[str] = "/openapi.json"
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = 3600
    
    # Reporting
    REPORT_CACHE_TTL: int = 86400
    REPORT_QUEUE_NAME: str = "tax_report_queue"
    REPORT_CHUNK_SIZE: int = 1000
    BACKGROUND_TASK_TIMEOUT: int = 300
    MAX_CONCURRENT_REPORTS: int = 5
    
    # Validators
    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES")
    def parse_access_token_expire_minutes(cls, v: Any) -> int:
        if isinstance(v, str):
            return int(v)
        return v
    
    @field_validator('BACKEND_CORS_ORIGINS')
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    def set_database_uri(self) -> None:
        """Set the database URI based on the database engine."""
        if self.DB_ENGINE == "postgresql":
            self.DATABASE_URI = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{quote_plus(self.POSTGRES_PASSWORD)}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
                f"{self.POSTGRES_DB}"
            )
        else:  # SQLite
            self.DATABASE_URI = f"sqlite+aiosqlite:///{Path(self.SQLITE_DB_PATH).absolute()}"
    
    @property
    def IS_SQLITE(self) -> bool:
        """Check if using SQLite database."""
        return self.DB_ENGINE == "sqlite"
    
    @property
    def IS_POSTGRESQL(self) -> bool:
        """Check if using PostgreSQL database."""
        return self.DB_ENGINE == "postgresql"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Get the database URI in a format compatible with SQLAlchemy and Alembic."""
        if not self.DATABASE_URI:
            self.set_database_uri()
        return self.DATABASE_URI
    
    @field_serializer('DATABASE_URI')
    def serialize_database_uri(self, uri: str, _info: Any) -> str:
        """Ensure the database URI is properly serialized."""
        if not uri:
            self.set_database_uri()
            return self.DATABASE_URI
        return uri
    
    @model_validator(mode='before')
    def get_project_name(cls, v: Optional[Dict], info: Any) -> Any:
        if not v:
            return v
        if 'PROJECT_NAME' not in v:
            v['PROJECT_NAME'] = "Paksa Financial System"
        return v
    
    @field_validator('PROJECT_NAME')
    def project_name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Project name cannot be empty")
        return v.strip()

# Create settings instance
settings = Settings()
