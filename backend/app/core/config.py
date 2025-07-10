"""
Application configuration settings.
"""
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    BaseModel,
    BaseSettings,
    Field,
    HttpUrl,
    PostgresDsn,
    ValidationError,
    field_validator,
    model_validator,
    validator,
    GetCoreSchemaHandler,
)
from pydantic_core import core_schema
from urllib.parse import urlparse, quote_plus
from typing import Any, Dict, List, Optional, TypeVar, Union, Annotated

T = TypeVar('T')


class AnyDatabaseUrl(str):
    """Custom field type that bypasses Pydantic's URL validation."""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x) if x is not None else None
            ),
        )
    
    @classmethod
    def validate(cls, v: Any, _info: core_schema.ValidationInfo) -> str:
        if not isinstance(v, str):
            raise ValueError("Database URL must be a string")
        
        # Basic validation for SQLite URLs
        if v.startswith(('sqlite://', 'sqlite+aiosqlite://')):
            return v
            
        # For PostgreSQL, do basic validation
        if v.startswith(('postgresql://', 'postgres://', 'postgresql+asyncpg://')):
            parsed = urlparse(v)
            if not all([parsed.scheme, parsed.path or parsed.netloc]):
                raise ValueError("Invalid database URL format")
            return v
        
        raise ValueError(
            "Invalid database URL scheme. Must be one of: "
            "sqlite, sqlite+aiosqlite, postgresql, postgres, postgresql+asyncpg"
        )


class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "Paksa Financial System"
    PROJECT_DESCRIPTION: str = "Comprehensive financial management platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
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
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "paksa_finance")
    
    # Database URL with custom validation
    DATABASE_URI: AnyDatabaseUrl = AnyDatabaseUrl("sqlite+aiosqlite:///./paksa_financial.db")
    
    @model_validator(mode='before')
    @classmethod
    def set_default_database_uri(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if 'DATABASE_URI' not in data or not data['DATABASE_URI']:
                data['DATABASE_URI'] = "sqlite+aiosqlite:///./paksa_financial.db"
        return data
    
    @model_validator(mode='after')
    def assemble_db_connection(self) -> 'Settings':
        # If DATABASE_URI is explicitly set, use it
        if hasattr(self, 'DATABASE_URI') and self.DATABASE_URI:
            return self
            
        # If we're using SQLite, set the default SQLite URL
        if os.getenv("USE_SQLITE", "true").lower() in ("true", "1", "t"):
            self.DATABASE_URI = "sqlite+aiosqlite:///./paksa_financial.db"
            return self
            
        # Otherwise, build a PostgreSQL URL from environment variables
        postgres_host = getattr(self, 'POSTGRES_SERVER', None)
        postgres_db = getattr(self, 'POSTGRES_DB', None)
        username = getattr(self, 'POSTGRES_USER', None)
        password = getattr(self, 'POSTGRES_PASSWORD', None)
        
        if not all([postgres_host, postgres_db, username, password]):
            # If not all PostgreSQL params are provided, fall back to SQLite
            self.DATABASE_URI = "sqlite+aiosqlite:///./paksa_financial.db"
        else:
            # URL-encode the password to handle special characters
            encoded_password = quote_plus(password)
            # Build the PostgreSQL URL
            self.DATABASE_URI = f"postgresql+asyncpg://{username}:{encoded_password}@{postgres_host}/{postgres_db}"
            
        return self
    
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
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()
