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

T = TypeVar('T')

def validate_database_url(url: str) -> str:
    """Validate database URL format."""
    if not url:
        raise ValueError("Database URL cannot be empty")
    
    # Check for SQLite URL format
    if url.startswith('sqlite'):
        if not re.match(r'^sqlite(\+\w+)?:///.*\.db$', url):
            raise ValueError("Invalid SQLite database URL format. Expected format: 'sqlite+aiosqlite:///path/to/database.db'")
        return url
    
    # Check for PostgreSQL URL format
    if url.startswith('postgresql'):
        if not re.match(r'^postgresql(\+\w+)?://[^:]+:[^@]+@[^:/]+(?:\d+)?/\w+$', url):
            raise ValueError("Invalid PostgreSQL database URL format. Expected format: 'postgresql+asyncpg://user:password@host:port/dbname'")
        return url
    
    raise ValueError("Unsupported database URL format. Supported formats: SQLite, PostgreSQL")


class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    PROJECT_NAME: str = "Paksa Financial System"
    PROJECT_DESCRIPTION: str = "Comprehensive financial management platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    API_VERSION: str = "1.0.0"  # Add missing API_VERSION
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours by default
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    @field_validator('ACCESS_TOKEN_EXPIRE_MINUTES', mode='before')
    @classmethod
    def parse_access_token_expire_minutes(cls, v: Any) -> int:
        if isinstance(v, str):
            # Remove any comments and strip whitespace
            v = v.split('#')[0].strip()
            return int(v)
        return v
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Default React dev server
        "http://localhost:8000",  # Default FastAPI dev server
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database settings
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'allow'  # Allow extra fields in .env file
    
    # Database connection settings
    DB_ENGINE: str = "sqlite"
    POSTGRES_DB: str = "paksa_finance"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    SQLITE_DB_PATH: str = "./instance/paksa_finance.db"
    
    # Connection pool settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 300  # 5 minutes
    DB_ECHO: bool = False
    
    # Database URL - will be set by the model validator
    DATABASE_URI: str = ""
    
    @model_validator(mode='after')
    def set_database_uri(self) -> 'Settings':
        """Set the database URI based on the database engine."""
        if self.DB_ENGINE == "postgresql":
            # PostgreSQL connection string
            self.DATABASE_URI = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            # SQLite connection string (default)
            # Ensure the directory exists
            db_path = Path(self.SQLITE_DB_PATH)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self.DATABASE_URI = f"sqlite+aiosqlite:///{db_path.absolute()}"
        
        # Validate the database URL
        self.DATABASE_URI = validate_database_url(self.DATABASE_URI)
        return self
    
    @field_serializer('DATABASE_URI')
    def serialize_database_uri(self, uri: str) -> str:
        """Serialize the database URI for JSON output."""
        return uri
        
    @property
    def IS_SQLITE(self) -> bool:
        """Check if using SQLite database."""
        return self.DATABASE_URI.startswith(('sqlite://', 'sqlite+aiosqlite://'))
    
    @property
    def IS_POSTGRESQL(self) -> bool:
        """Check if using PostgreSQL database."""
        return 'postgresql' in self.DATABASE_URI or 'postgresql+asyncpg' in self.DATABASE_URI
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Get the database URI in a format compatible with SQLAlchemy and Alembic."""
        # Convert asyncpg to psycopg2 for synchronous operations
        if 'postgresql+asyncpg' in self.DATABASE_URI:
            return self.DATABASE_URI.replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
        return self.DATABASE_URI
    
    @field_serializer('DATABASE_URI')
    def serialize_database_uri(self, uri: str, _info: Any) -> str:
        """Ensure the database URI is properly serialized."""
        return str(uri)
    
    # SQLAlchemy settings
    SQLALCHEMY_POOL_SIZE: int = 5
    SQLALCHEMY_MAX_OVERFLOW: int = 10
    SQLALCHEMY_POOL_TIMEOUT: int = 30
    SQLALCHEMY_POOL_RECYCLE: int = 3600
    SQLALCHEMY_ECHO: bool = False
    
    # First superuser
    FIRST_SUPERUSER_EMAIL: EmailStr = "admin@paksa.finance"
    FIRST_SUPERUSER_PASSWORD: str = "changeme"
    FIRST_SUPERUSER_FULL_NAME: str = "Admin"
    
    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    @field_validator("EMAILS_FROM_NAME", mode='before')
    @classmethod
    def get_project_name(cls, v: Optional[str], info: Any) -> str:
        if not v and hasattr(info, 'data') and 'PROJECT_NAME' in info.data:
            return info.data["PROJECT_NAME"]
        return v or ""
    
    @field_validator("PROJECT_NAME")
    @classmethod
    def project_name_must_not_be_empty(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("PROJECT_NAME must not be empty")
        return v
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "application/pdf", "text/csv"]
    
    # Security headers
    SECURE_CONTENT_TYPE_NOSNIFF: bool = True
    SECURE_BROWSER_XSS_FILTER: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SECURE: bool = not bool(os.getenv("DEV_MODE"))
    SESSION_COOKIE_SAMESITE: str = "lax"
    
    # Rate limiting
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
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = 3600  # Default cache TTL in seconds (1 hour)
    
    # Report Generation Settings
    REPORT_CACHE_TTL: int = 86400  # 24 hours for report caching
    REPORT_QUEUE_NAME: str = "tax_report_queue"
    REPORT_CHUNK_SIZE: int = 1000  # Number of records to process in each chunk
    
    # Background Task Settings
    BACKGROUND_TASK_TIMEOUT: int = 300  # 5 minutes
    MAX_CONCURRENT_REPORTS: int = 5  # Maximum number of concurrent report generations
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()
