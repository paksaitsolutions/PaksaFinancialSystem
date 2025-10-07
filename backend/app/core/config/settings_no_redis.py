import os
from typing import List, Optional

class Settings:
    # Database
    DATABASE_URL: str = "sqlite:///./paksa_financial.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3003",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3003"
    ]
    
    # Redis disabled
    REDIS_URL: Optional[str] = None
    USE_REDIS: bool = False

settings = Settings()