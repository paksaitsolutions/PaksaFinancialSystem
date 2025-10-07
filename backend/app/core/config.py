import os
from typing import List
from pydantic import BaseModel, ConfigDict

class Settings(BaseModel):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    CORS_ORIGINS: List[str]
    RATE_LIMIT_PER_MINUTE: int
    MAX_LOGIN_ATTEMPTS: int
    LOCKOUT_DURATION_MINUTES: int
    REDIS_URL: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    ENVIRONMENT: str
    DEBUG: bool
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    PLAID_ENVIRONMENT: str

    model_config = ConfigDict(env_file=".env")

settings = Settings(
    DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./paksa_financial.db"),
    SECRET_KEY=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
    ALGORITHM=os.getenv("ALGORITHM", "HS256"),
    ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
    REFRESH_TOKEN_EXPIRE_DAYS=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
    CORS_ORIGINS=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3003").split(","),
    RATE_LIMIT_PER_MINUTE=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
    MAX_LOGIN_ATTEMPTS=int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")),
    LOCKOUT_DURATION_MINUTES=int(os.getenv("LOCKOUT_DURATION_MINUTES", "15")),
    REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379"),
    SMTP_HOST=os.getenv("SMTP_HOST", ""),
    SMTP_PORT=int(os.getenv("SMTP_PORT", "587")),
    SMTP_USER=os.getenv("SMTP_USER", ""),
    SMTP_PASSWORD=os.getenv("SMTP_PASSWORD", ""),
    ENVIRONMENT=os.getenv("ENVIRONMENT", "development"),
    DEBUG=os.getenv("DEBUG", "true").lower() == "true",
    PLAID_CLIENT_ID=os.getenv("PLAID_CLIENT_ID", ""),
    PLAID_SECRET=os.getenv("PLAID_SECRET", ""),
    PLAID_ENVIRONMENT=os.getenv("PLAID_ENVIRONMENT", "sandbox")
)