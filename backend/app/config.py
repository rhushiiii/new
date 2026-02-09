"""
Configuration settings for PowerGuard backend.
Uses environment variables for deployment flexibility.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # Application
    APP_NAME: str = "PowerGuard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/powerguard"
    
    # For SQLite fallback (development)
    USE_SQLITE: bool = True
    SQLITE_URL: str = "sqlite+aiosqlite:///./powerguard.db"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # ML Settings
    ANOMALY_THRESHOLD: float = 0.5
    ISOLATION_FOREST_CONTAMINATION: float = 0.1
    USE_AUTOENCODER: bool = False
    
    # API Settings
    API_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
