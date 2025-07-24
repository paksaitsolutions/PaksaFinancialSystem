"""
Application configuration settings with secure defaults.

This module handles all application configuration with a focus on security best practices.
It loads settings from environment variables with appropriate validation and type conversion.
"""
import os
import secrets
import string
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
    validator
)
from pydantic_settings import BaseSettings, SettingsConfigDict

# Type variable for generic model validation
ModelT = TypeVar('ModelT', bound=BaseModel)
# Type variable for generic type hints
T = TypeVar('T')

def generate_random_key(length: int = 64) -> str:
    """Generate a secure random key of specified length.
    
    Args:
        length: Length of the key to generate (default: 64)
        
    Returns:
        str: A cryptographically secure random string
    """
    alphabet = string.ascii_letters + string.digits + "-._~"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def validate_database_url(url: str) -> str:
    """
    Validate and sanitize database URL format.
    
    Args:
        url: The database URL to validate
        
    Returns:
        str: The validated and sanitized database URL
        
    Raises:
        ValueError: If the URL is invalid or uses an unsupported database engine
    """
    if not url:
        raise ValueError("Database URL cannot be empty")
    
    # Basic URL parsing
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid database URL: {str(e)}")
    
    # Check for SQLite URL format
    if parsed.scheme.startswith('sqlite'):
        if not re.match(r'^sqlite(\+\w+)?:///.*\.db$', url):
            raise ValueError(
                "Invalid SQLite database URL format. "
                "Expected format: 'sqlite+aiosqlite:///path/to/database.db'"
            )
        # Ensure the directory exists and has proper permissions
        db_path = Path(parsed.path.lstrip('/'))
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_path.parent.chmod(0o700)  # Restrict directory permissions
        return url
    
    # Check for PostgreSQL URL format
    if parsed.scheme.startswith('postgresql'):
        if not re.match(r'^postgresql(\+\w+)?://[^:]+:[^@]+@[^:/]+(?:\d+)?/\w+$', url):
            raise ValueError(
                "Invalid PostgreSQL database URL format. "
                "Expected format: 'postgresql+asyncpg://user:password@host:port/dbname'"
            )
        # Mask password in logs
        masked_url = url.replace(parsed.password, '***' if parsed.password else '')
        if parsed.password:
            warnings.warn(
                f"Using password in database URL is not recommended. Use environment variables instead. "
                f"URL: {masked_url}",
                UserWarning
            )
        return url
    
    raise ValueError(
        "Unsupported database URL format. "
        "Supported formats: SQLite, PostgreSQL"
    )


class Settings(BaseSettings):
    """
    Application settings with secure defaults.
    
    This class handles all application configuration with a focus on security.
    It loads settings from environment variables with appropriate validation.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra='ignore',
        env_nested_delimiter='__',
        case_sensitive=True,
        validate_default=True
    )
    
    # Application settings
    PROJECT_NAME: str = Field(
        default="Paksa Financial System",
        description="Name of the application",
        min_length=1,
        max_length=100
    )
    
    PROJECT_DESCRIPTION: str = Field(
        default="Comprehensive financial management platform",
        description="Description of the application"
    )
    
    VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )
    
    API_V1_STR: str = Field(
        default="/api/v1",
        description="API version 1 base path"
    )
    
    API_VERSION: str = Field(
        default="1.0.0",
        description="API version string"
    )
    
    # Security settings
    SECRET_KEY: SecretStr = Field(
        default_factory=lambda: SecretStr(generate_random_key(64)),
        description="Secret key for cryptographic operations. "
                    "Should be at least 64 characters long in production.",
        min_length=64,
        max_length=1024
    )
    
    # JWT Configuration
    JWT_SECRET_KEY: SecretStr = Field(
        default_factory=lambda: SecretStr(generate_random_key(64)),
        description="JWT signing key. Must be at least 64 characters long in production.",
        min_length=64,
        max_length=1024
    )
    JWT_REFRESH_SECRET_KEY: SecretStr = Field(
        default_factory=lambda: SecretStr(generate_random_key(64)),
        description="JWT refresh token signing key. Must be different from JWT_SECRET_KEY.",
        min_length=64,
        max_length=1024
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm. Options: HS256, HS384, HS512"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,  # 1 hour for access tokens
        description="Access token expiration time in minutes",
        gt=0,
        le=1440  # Max 24 hours
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token expiration time in days",
        gt=0,
        le=30  # Max 30 days
    )
    
    # Password policies
    PASSWORD_HASH_ALGORITHM: str = Field(
        default="bcrypt",
        description="Password hashing algorithm. Options: bcrypt, argon2"
    )
    PASSWORD_MIN_LENGTH: int = Field(
        default=12,
        description="Minimum password length",
        ge=12,  # Enforce minimum 12 characters
        le=128
    )
    PASSWORD_COMPLEXITY: Dict[str, Any] = Field(
        default={
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digits": True,
            "require_special_chars": True,
            "max_repeated_chars": 2,
            "max_sequential_chars": 3,
            "min_unique_chars": 8,
            "disallow_common_passwords": True,
            "disallow_user_attributes": ["email", "username", "first_name", "last_name"]
        },
        description="Password complexity requirements"
    )
    PASSWORD_HISTORY_SIZE: int = Field(
        default=5,
        description="Number of previous passwords to store for history check",
        ge=3,  # Enforce minimum history of 3 passwords
        le=24   # Reasonable upper limit
    )
    PASSWORD_RESET_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Password reset token expiration time in minutes",
        gt=0,
        le=1440  # Max 24 hours
    )
    
    # Account security
    MAX_LOGIN_ATTEMPTS: int = Field(
        default=5,
        description="Maximum number of failed login attempts before account lockout",
        gt=0
    )
    ACCOUNT_LOCKOUT_MINUTES: int = Field(
        default=15,
        description="Number of minutes to lock an account after too many failed attempts",
        gt=0
    )
    SESSION_TIMEOUT_MINUTES: int = Field(
        default=30,
        description="User session timeout in minutes",
        gt=0
    )
    
    # Security headers - Enabled by default for maximum security
    SECURE_HEADERS: Dict[str, Union[bool, str]] = Field(
        default={
            # HTTP Strict Transport Security
            "hsts": True,
            "hsts_max_age": 31536000,  # 1 year
            "hsts_include_subdomains": True,
            "hsts_preload": True,
            
            # XSS Protection
            "xss_filter": True,
            "xss_filter_mode": "block",
            
            # MIME type sniffing protection
            "content_type_nosniff": True,
            
            # Clickjacking protection
            "x_frame_options": "DENY",
            
            # Content Security Policy
            "content_security_policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                                      "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                                      "font-src 'self' data:; connect-src 'self'; "
                                      "frame-ancestors 'none'; form-action 'self'; "
                                      "base-uri 'self'; object-src 'none';",
            
            # Referrer Policy
            "referrer_policy": "strict-origin-when-cross-origin",
            
            # Permissions Policy
            "permissions_policy": "camera=(), microphone=(), geolocation=(), payment=()",
            
            # Other security headers
            "x_content_type_options": "nosniff",
            "x_download_options": "noopen",
            "x_permitted_cross_domain_policies": "none",
            "cross_origin_opener_policy": "same-origin",
            "cross_origin_embedder_policy": "require-corp",
            "cross_origin_resource_policy": "same-site",
            "strict_transport_security": "max-age=31536000; includeSubDomains; preload"
        },
        description="Security headers configuration. Boolean values enable/disable headers, "
                   "strings set header values directly."
    )
    
    # Rate limiting and brute force protection
    RATE_LIMIT_REQUESTS: int = Field(
        default=100,
        description="Number of requests allowed per RATE_LIMIT_MINUTES",
        gt=0
    )
    RATE_LIMIT_MINUTES: int = Field(
        default=15,
        description="Time window for rate limiting in minutes",
        gt=0
    )
    
    # API Security
    API_KEY_HEADER: str = Field(
        default="X-API-Key",
        description="Header name for API key authentication"
    )
    
    ENABLE_API_KEY_AUTH: bool = Field(
        default=False,
        description="Enable API key authentication"
    )
    
    # CORS settings are defined in the CORS section below
    
    @field_validator('ALGORITHM')
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """Validate the JWT algorithm is secure."""
        valid_algorithms = {"HS256", "HS384", "HS512", "RS256", "RS384", "RS512"}
        if v.upper() not in valid_algorithms:
            raise ValueError(f"Invalid JWT algorithm. Must be one of {valid_algorithms}")
        return v.upper()
    
    @field_validator('ACCESS_TOKEN_EXPIRE_MINUTES', mode='before')
    @classmethod
    def parse_access_token_expire_minutes(cls, v: Any) -> int:
        if isinstance(v, str):
            # Remove any comments and strip whitespace
            v = v.split('#')[0].strip()
            return int(v)
        return v
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = Field(
        default=[
            "http://localhost:3000",  # Default React dev server
            "http://localhost:8000",  # Default FastAPI dev server
        ],
        description="List of origins that are allowed to make cross-origin requests"
    )
    
    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str], List[AnyHttpUrl]]) -> List[AnyHttpUrl]:
        """Parse and validate CORS origins."""
        if isinstance(v, str) and not v.startswith("["):
            # Handle space or comma separated list of origins
            origins = [i.strip() for i in v.split(",") if i.strip()]
            return [cls._validate_origin(origin) for origin in origins]
        elif isinstance(v, (list, str)):
            return [cls._validate_origin(origin) for origin in v]
        raise ValueError("Invalid CORS origins format")
    
    @classmethod
    def _validate_origin(cls, origin: Union[str, AnyHttpUrl]) -> AnyHttpUrl:
        """
        Validate a single CORS origin URL.
        
        Args:
            origin: The origin URL to validate
            
        Returns:
            Validated AnyHttpUrl object
            
        Raises:
            ValueError: If the origin is invalid
        """
        if not origin:
            raise ValueError("Empty origin not allowed")
            
        if isinstance(origin, AnyHttpUrl):
            return origin
            
        if isinstance(origin, str):
            origin = origin.strip()
            if not origin:
                raise ValueError("Empty origin string")
                
            # Allow localhost in development
            if origin == "*" and cls.model_config.get("ENVIRONMENT") != "production":
                return origin
                
            try:
                parsed = AnyHttpUrl(origin)
                # Additional validation
                if parsed.scheme not in ("http", "https"):
                    raise ValueError(f"Invalid scheme: {parsed.scheme}")
                return parsed
            except ValueError as e:
                raise ValueError(f"Invalid CORS origin: {origin}") from e
                
        raise ValueError(f"Invalid origin type: {type(origin)}")
    
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=False,  # More secure default
        description="Whether to allow credentials in CORS requests"
    )
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        description="List of allowed HTTP methods for CORS"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization"
        ],
        description="List of allowed HTTP headers for CORS"
    )
    CORS_EXPOSE_HEADERS: List[str] = Field(
        default=[],
        description="List of headers exposed to the browser"
    )
    CORS_MAX_AGE: int = Field(
        default=600,  # 10 minutes
        description="Maximum time (in seconds) to cache CORS preflight responses"
    )
    
    # Database configuration
    DB_ENGINE: str = Field(
        default="sqlite",
        description="Database engine (sqlite or postgresql)",
        pattern=r"^(sqlite|postgresql)$"
    )
    SQLITE_DB_PATH: str = Field(
        default="./instance/paksa_finance.db",
        description="Path to SQLite database file"
    )
    POSTGRES_DB: Optional[str] = Field(
        default=None,
        description="PostgreSQL database name"
    )
    POSTGRES_USER: Optional[str] = Field(
        default=None,
        description="PostgreSQL username"
    )
    POSTGRES_PASSWORD: Optional[SecretStr] = Field(
        default=None,
        description="PostgreSQL password"
    )
    POSTGRES_HOST: Optional[str] = Field(
        default="localhost",
        description="PostgreSQL host"
    )
    POSTGRES_PORT: str = Field(
        default="5432",
        description="PostgreSQL port",
        pattern=r"^\d+$"
    )
    DATABASE_URL: Optional[SecretStr] = Field(
        default=None,
        description="Full database URL (overrides individual DB settings)"
    )
    
    # Database connection pool settings
    DB_POOL_SIZE: int = Field(
        default=5,
        description="Database connection pool size",
        gt=0,
        le=20
    )
    
    DB_MAX_OVERFLOW: int = Field(
        default=10,
        description="Maximum overflow for database connections",
        ge=0
    )
    
    DB_POOL_RECYCLE: int = Field(
        default=1800,  # 30 minutes
        description="Database connection recycle time in seconds",
        gt=0
    )
    
    DB_ECHO: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )
    
    # Database URL - will be set by the model validator
    DATABASE_URI: Optional[SecretStr] = None
    
    @model_validator(mode='after')
    def set_database_uri(self) -> 'Settings':
        """Set the database URI based on configuration."""
        # 1. First, try to get from DATABASE_URI environment variable
        if os.getenv('DATABASE_URI'):
            self.DATABASE_URI = os.getenv('DATABASE_URI')
            return self
            
        # 2. Then try DATABASE_URL (common in some platforms)
        if os.getenv('DATABASE_URL'):
            self.DATABASE_URI = os.getenv('DATABASE_URL')
            return self
            
        # 3. Fall back to constructing from individual settings
        if self.DB_ENGINE == "sqlite":
            # Convert to absolute path and ensure directory exists
            db_path = Path(self.SQLITE_DB_PATH).absolute()
            db_path.parent.mkdir(parents=True, exist_ok=True)
            # Format for SQLAlchemy with forward slashes
            db_path_str = str(db_path).replace('\\', '/')
            self.DATABASE_URI = f"sqlite+aiosqlite:///{db_path_str}"
            # Set environment variable for other parts of the app
            os.environ['DATABASE_URI'] = self.DATABASE_URI
        elif self.DB_ENGINE == "postgresql":
            if not all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_DB]):
                raise ValueError("PostgreSQL configuration is incomplete")
            self.DATABASE_URI = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD.get_secret_value()}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        else:
            raise ValueError(f"Unsupported database engine: {self.DB_ENGINE}")
            
        return self
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_DB,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT
        ]):
            db_uri = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:"
                f"{self.POSTGRES_PASSWORD.get_secret_value()}@"
                f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
                f"{self.POSTGRES_DB}"
            )
            self.DATABASE_URI = SecretStr(db_uri)
            # Also set SQLALCHEMY_DATABASE_URI for compatibility
            self.SQLALCHEMY_DATABASE_URI = db_uri
        else:
            raise ValueError(
                "Database configuration is incomplete. "
                "For SQLite, set SQLITE_DB_PATH. "
                "For PostgreSQL, set all POSTGRES_* variables."
            )
            # Set restrictive permissions on the directory
            db_path.parent.chmod(0o700)
            
            # Ensure the database file exists and has proper permissions
            db_path.touch(exist_ok=True)
            db_path.chmod(0o600)  # Read/write for owner only
            
            self.DATABASE_URI = SecretStr(f"sqlite+aiosqlite:///{db_path}")
        
        # Validate the database URL
        if self.DATABASE_URI:
            validate_database_url(self.DATABASE_URI.get_secret_value())
        
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
    @field_serializer('DATABASE_URI')
    def serialize_database_uri(self, v: Optional[SecretStr], _info: ValidationInfo) -> Optional[str]:
        return v.get_secret_value() if v else None

    # Email settings
    SMTP_TLS: bool = Field(
        default=True,
        description="Enable TLS for SMTP connections"
    )

    SMTP_PORT: Optional[int] = Field(
        default=None,
        description="SMTP server port",
        gt=0,
        lt=65536
    )

    SMTP_HOST: Optional[str] = Field(
        default=None,
        description="SMTP server hostname"
    )

    SMTP_USER: Optional[str] = Field(
        default=None,
        description="SMTP authentication username"
    )

    SMTP_PASSWORD: Optional[SecretStr] = Field(
        default=None,
        description="SMTP authentication password"
    )

    EMAILS_FROM_EMAIL: Optional[EmailStr] = Field(
        default=None,
        description="Default 'from' email address for outgoing emails"
    )

    EMAILS_FROM_NAME: Optional[str] = Field(
        default=None,
        description="Default 'from' name for outgoing emails"
    )

    @field_validator("EMAILS_FROM_NAME")
    @classmethod
    def get_project_name(cls, v: Optional[str], values: ValidationInfo) -> str:
        if not v:
            return values.data.get("PROJECT_NAME", "Paksa Financial System")
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = Field(
        default=24,
        description="Expiration time for password reset tokens in hours",
        gt=0
    )

    EMAIL_TEMPLATES_DIR: str = Field(
        default="/app/app/email-templates/build",
        description="Directory containing email templates"
    )

    EMAILS_ENABLED: bool = Field(
        default=False,
        description="Enable email sending functionality"
    )

    @field_validator("EMAILS_ENABLED", mode='before')
    @classmethod
    def get_emails_enabled(cls, v: Optional[bool], values: ValidationInfo) -> bool:
        if v is not None:
            return v

        return bool(
            values.data.get("SMTP_HOST")
            and values.data.get("SMTP_PORT")
            and values.data.get("EMAILS_FROM_EMAIL")
        )

    # Test and development settings
    EMAIL_TEST_USER: EmailStr = Field(
        default="test@example.com",
        description="Test email address for development"
    )

    # First superuser (required for initial setup)
    FIRST_SUPERUSER: EmailStr = Field(
        ...,
        description="Email address of the first superuser (required)"
    )

    FIRST_SUPERUSER_PASSWORD: str = Field(
        ...,
        description="Password for the first superuser (required)",
        min_length=8
    )

    USERS_OPEN_REGISTRATION: bool = Field(
        default=False,
        description="Allow open user registration"
    )

    # Security headers configuration
    SECURITY_HEADERS: Dict[str, str] = Field(
        default_factory=lambda: {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "same-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin"
        },
        description="Security headers configuration for HTTP responses"
    )

    def set_database_uri(self) -> None:
        """Set the database URI based on configuration."""
        if self.DATABASE_URI:
            validate_database_url(self.DATABASE_URI.get_secret_value())

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
@field_serializer('DATABASE_URI')
def serialize_database_uri(self, v: Optional[SecretStr], _info: ValidationInfo) -> Optional[str]:
    return v.get_secret_value() if v else None

# Email settings
SMTP_TLS: bool = Field(
    default=True,
    description="Enable TLS for SMTP connections"
)

SMTP_PORT: Optional[int] = Field(
    default=None,
    description="SMTP server port",
    gt=0,
    lt=65536
)

SMTP_HOST: Optional[str] = Field(
    default=None,
    description="SMTP server hostname"
)

SMTP_USER: Optional[str] = Field(
    default=None,
    description="SMTP authentication username"
)

SMTP_PASSWORD: Optional[SecretStr] = Field(
    default=None,
    description="SMTP authentication password"
)

EMAILS_FROM_EMAIL: Optional[EmailStr] = Field(
    default=None,
    description="Default 'from' email address for outgoing emails"
)

EMAILS_FROM_NAME: Optional[str] = Field(
    default=None,
    description="Default 'from' name for outgoing emails"
)

@field_validator("EMAILS_FROM_NAME")
@classmethod
def get_project_name(cls, v: Optional[str], values: ValidationInfo) -> str:
    if not v:
        return values.data.get("PROJECT_NAME", "Paksa Financial System")
    return v

EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = Field(
    default=24,
    description="Expiration time for password reset tokens in hours",
    gt=0
)

EMAIL_TEMPLATES_DIR: str = Field(
    default="/app/app/email-templates/build",
    description="Directory containing email templates"
)

EMAILS_ENABLED: bool = Field(
    default=False,
    description="Enable email sending functionality"
)

@field_validator("EMAILS_ENABLED", mode='before')
@classmethod
def get_emails_enabled(cls, v: Optional[bool], values: ValidationInfo) -> bool:
    if v is not None:
        return v

    return bool(
        values.data.get("SMTP_HOST")
        and values.data.get("SMTP_PORT")
        and values.data.get("EMAILS_FROM_EMAIL")
    )

# Test and development settings
EMAIL_TEST_USER: EmailStr = Field(
    default="test@example.com",
    description="Test email address for development"
)

# First superuser (required for initial setup)
FIRST_SUPERUSER: EmailStr = Field(
    ...,
    description="Email address of the first superuser (required)"
)

FIRST_SUPERUSER_PASSWORD: str = Field(
    ...,
    description="Password for the first superuser (required)",
    min_length=8
)

USERS_OPEN_REGISTRATION: bool = Field(
    default=False,
    description="Allow open user registration"
)

# Security headers configuration
SECURITY_HEADERS: Dict[str, str] = Field(
    default_factory=lambda: {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "SAMEORIGIN",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "same-origin",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Cross-Origin-Embedder-Policy": "require-corp",
        "Cross-Origin-Opener-Policy": "same-origin",
        "Cross-Origin-Resource-Policy": "same-site"
    },
    description="Security headers to be added to all responses"
)

SESSION_COOKIE_SECURE: bool = Field(
    default=not bool(os.getenv("DEV_MODE")),
    description="Secure flag for session cookies (HTTPS only)"
)

SESSION_COOKIE_SAMESITE: str = Field(
    default="lax",
    description="SameSite attribute for session cookies",
    pattern=r"^(lax|strict|none)$"
)

SESSION_COOKIE_HTTPONLY: bool = Field(
    default=True,
    description="HttpOnly flag for session cookies"
)

# Security middleware settings
SECURE_HSTS_SECONDS: int = Field(
    default=31536000,  # 1 year
    description="HTTP Strict Transport Security max-age in seconds",
    ge=0
)

SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = Field(
    default=True,
    description="Include all subdomains in HSTS policy"
)

SECURE_HSTS_PRELOAD: bool = Field(
    default=True,
    description="Enable HSTS preload inclusion"
)

# File upload settings
UPLOAD_DIR: str = Field(
    default="uploads",
    description="Directory for file uploads"
)

MAX_UPLOAD_SIZE: int = Field(
    default=10 * 1024 * 1024,  # 10MB
    description="Maximum file upload size in bytes",
    gt=0
)

ALLOWED_FILE_TYPES: List[str] = Field(
    default=["image/jpeg", "image/png", "application/pdf", "text/csv"],
    description="List of allowed MIME types for file uploads"
)

# Cache settings
CACHE_TYPE: str = Field(
    default="simple",
    description="Cache backend type (simple, redis, memcached, etc.)"
)

CACHE_DEFAULT_TIMEOUT: int = Field(
    default=300,  # 5 minutes
    description="Default cache timeout in seconds",
    ge=0
)

CACHE_REDIS_URL: Optional[SecretStr] = Field(
    default=None,
    description="Redis URL for cache backend (if using Redis)"
)

# Background tasks
TASK_BROKER_URL: SecretStr = Field(
    default="redis://localhost:6379/0",
    description="Message broker URL for background tasks"
)

TASK_RESULT_BACKEND: SecretStr = Field(
    default="redis://localhost:6379/0",
    description="Result backend URL for background tasks"
)

# Feature flags
FEATURE_MAINTENANCE_MODE: bool = Field(
    default=False,
    description="Enable maintenance mode"
)

FEATURE_API_V2: bool = Field(
    default=False,
    description="Enable experimental API v2 endpoints"
)

# Monitoring and metrics
METRICS_ENABLED: bool = Field(
    default=False,
    description="Enable Prometheus metrics endpoint"
)

METRICS_PORT: int = Field(
    default=9100,
    description="Port for metrics server",
    gt=1024,
    lt=65536
)

# External services
EXTERNAL_SERVICE_TIMEOUT: int = Field(
    default=10,
    description="Default timeout in seconds for external service calls",
    gt=0
)

# Sentry configuration
SENTRY_DSN: Optional[SecretStr] = Field(
    default=None,
    description="Sentry DSN for error tracking"
)

SENTRY_ENVIRONMENT: str = Field(
    default="development",
    description="Environment name for Sentry"
)

# Test settings
TESTING: bool = Field(
    default=False,
    description="Enable test mode"
)

TEST_DATABASE_URL: Optional[SecretStr] = Field(
    default=None,
    description="Database URL for tests (overrides DATABASE_URI in test mode)"
)

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
    env_file = ".env"
    env_file_encoding = 'utf-8'
    extra = 'ignore'  # Ignore extra fields in .env file
    
    # Add example values for documentation
    json_schema_extra = {
        "example": {
            "PROJECT_NAME": "Paksa Financial System",
            "ENVIRONMENT": "development",
            "SECRET_KEY": "change-this-in-production",
            "DATABASE_URL": "postgresql+asyncpg://user:password@localhost:5432/dbname",
            "FIRST_SUPERUSER": "admin@example.com",
            "FIRST_SUPERUSER_PASSWORD": "changeme",
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": 587,
            "SMTP_USER": "user@example.com",
            "SMTP_PASSWORD": "smtp-password",
            "EMAILS_FROM_EMAIL": "noreply@example.com",
            "SENTRY_DSN": "https://public@sentry.example.com/1"
        }
    }

@field_validator("UPLOAD_DIR", mode='after')
@classmethod
def create_upload_dir(cls, v: str) -> str:
    """Ensure upload directory exists and has correct permissions."""
    if v:
        upload_dir = Path(v)
        upload_dir.mkdir(parents=True, exist_ok=True)
        # Set restrictive permissions (rwx------)
        upload_dir.chmod(0o700)
    return v

@field_validator("ALLOWED_FILE_TYPES")
@classmethod
def validate_file_types(cls, v: List[str]) -> List[str]:
    """Validate allowed file types."""
    if not v:
        raise ValueError("At least one file type must be allowed")
    return [t.lower() for t in v]

@field_validator("CACHE_TYPE")
@classmethod
def validate_cache_type(cls, v: str) -> str:
    """Validate cache type."""
    valid_types = ["simple", "redis", "memcached", "filesystem", "null"]
    if v.lower() not in valid_types:
        raise ValueError(f"Invalid cache type. Must be one of: {', '.join(valid_types)}")
    return v.lower()

@field_validator("SENTRY_ENVIRONMENT")
@classmethod
def validate_environment(cls, v: str) -> str:
    """Validate Sentry environment."""
    valid_envs = ["development", "staging", "production"]
    if v.lower() not in valid_envs:
        logger.warning(f"Unexpected Sentry environment: {v}. Expected one of: {', '.join(valid_envs)}")
    return v.lower()

# Create settings instance
settings = Settings()
