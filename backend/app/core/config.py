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
    ValidationError,
    field_validator,
    model_validator,
    validator,
    GetCoreSchemaHandler,
    EmailStr,
    field_serializer,
)
from pydantic_core import core_schema
from urllib.parse import urlparse, quote_plus
from typing import Any, Dict, List, Optional, TypeVar, Union, Annotated

# Import our database URL utilities
from .db_utils import get_database_url, validate_database_url

T = TypeVar('T')


class DatabaseUrl(str):
    """Custom field type for database URLs with proper validation."""
    
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
        return validate_database_url(v)


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
    # Database connection settings
    DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite").lower()
    DB_NAME: str = os.getenv("POSTGRES_DB", "paksa_finance")
    DB_USER: str = os.getenv("POSTGRES_USER", "postgres")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    DB_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # SQLite specific settings
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "./instance/paksa_finance.db")
    
    # Connection pool settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "300"))  # 5 minutes
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() in ("true", "1", "t")
    
    # Database URL - will be set by the model validator
    DATABASE_URI: DatabaseUrl = ""
    
    @model_validator(mode='after')
    def set_database_uri(self) -> 'Settings':
        """Set the database URI based on the database engine."""
        if self.DB_ENGINE == "postgresql":
            # PostgreSQL connection string
            self.DATABASE_URI = f"postgresql+asyncpg://{self.DB_USER}:{quote_plus(self.DB_PASSWORD)}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            # SQLite connection string (default)
            # Ensure the directory exists
            db_path = Path(self.SQLITE_DB_PATH)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            self.DATABASE_URI = f"sqlite+aiosqlite:///{db_path.absolute()}"
        
        # Validate the database URL
        self.DATABASE_URI = validate_database_url(self.DATABASE_URI)
        return self
        
    @property
    def IS_SQLITE(self) -> bool:
        """Check if using SQLite database."""
        return self.DATABASE_URI.startswith(('sqlite://', 'sqlite+aiosqlite://'))
    
    @property
    def IS_POSTGRESQL(self) -> bool:
        """Check if using PostgreSQL database."""
        return 'postgresql' in self.DATABASE_URI or 'postgresql+asyncpg' in self.DATABASE_URI
    
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
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()
