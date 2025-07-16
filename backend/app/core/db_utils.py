"""
Database URL utilities for handling SQLite and PostgreSQL URLs.
"""
from typing import Optional
from urllib.parse import urlparse, urlunparse, ParseResult

def validate_database_url(url: str) -> str:
    """
    Validate and normalize a database URL.
    
    Args:
        url: The database URL to validate
        
    Returns:
        The normalized URL
        
    Raises:
        ValueError: If the URL is invalid
    """
    if not url:
        raise ValueError("Database URL cannot be empty")
        
    # Check for SQLite URLs
    if url.startswith(('sqlite://', 'sqlite+aiosqlite://')):
        # For SQLite, just ensure it starts with sqlite:// or sqlite+aiosqlite://
        # and has a valid path
        if not any(url.startswith(prefix) for prefix in [
            'sqlite:///',  # Absolute path
            'sqlite://',   # Relative path (will be normalized)
            'sqlite+aiosqlite:///',
            'sqlite+aiosqlite://',
        ]):
            raise ValueError(
                "SQLite URL must start with 'sqlite:///' or 'sqlite+aiosqlite:///' "
                "for absolute paths, or 'sqlite://'/'sqlite+aiosqlite://' for relative paths"
            )
        return url
        
    # For PostgreSQL, do proper URL parsing
    try:
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError("Invalid database URL format")
            
        # Reconstruct the URL to normalize it
        return urlunparse(parsed)
    except Exception as e:
        raise ValueError(f"Invalid database URL: {str(e)}")


def get_database_url() -> str:
    """
    Get the database URL from environment variables or use SQLite as default.
    """
    import os
    
    # Check for explicit database URL
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return validate_database_url(db_url)
        
    # Check for PostgreSQL environment variables
    postgres_vars = [
        os.getenv("POSTGRES_SERVER"),
        os.getenv("POSTGRES_USER"),
        os.getenv("POSTGRES_PASSWORD"),
        os.getenv("POSTGRES_DB")
    ]
    
    if all(postgres_vars):
        # Build PostgreSQL URL from environment variables
        from urllib.parse import quote_plus
        
        user = os.getenv("POSTGRES_USER")
        password = quote_plus(os.getenv("POSTGRES_PASSWORD", ""))
        host = os.getenv("POSTGRES_SERVER")
        db = os.getenv("POSTGRES_DB")
        port = os.getenv("POSTGRES_PORT", "5432")
        
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
    
    # Default to SQLite
    return "sqlite+aiosqlite:///./paksa_financial.db"
