from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "MarketPulse"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Auth / JWT
    SECRET_KEY: str = "insecure-dev-secret-key-change-in-production-marketpulse"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours for seamless development
    
    # Database (PostgreSQL or SQLite async)
    DATABASE_URL: str = "sqlite+aiosqlite:///./marketpulse.db"
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_DEFAULT_TTL: int = 30  # seconds
    
    # Market Data
    DEFAULT_MARKET_PROVIDER: str = "mock"  # "mock" or "yfinance"
    
    # AI / LLM
    LLM_PROVIDER: str = "mock"  # "mock", "gemini", "openai", "groq"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
