from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from functools import lru_cache
import logging

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Paksa Financial System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str
    API_PREFIX: str = "/api/v1"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # Database settings
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Security settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # First superuser
    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str
    
    # Email settings (for future use)
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@example.com"
    EMAILS_FROM_NAME: str = "Paksa Finance"
    
    # AI/ML settings (for future use)
    OPENAI_API_KEY: str = ""
    
    # External services (for future use)
    SENTRY_DSN: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Global settings instance
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
