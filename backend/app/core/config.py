"""Application configuration with environment variable management."""
from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./squeeze.db"

    # Data provider: mock | ortex | fintel
    data_provider: str = "mock"

    # Auth
    jwt_secret: str = "changeme"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Redis
    redis_url: Optional[str] = None

    # FINRA
    finra_data_dir: str = "./data/finra"

    # Scheduler
    scheduler_interval_hours: int = 6

    # Notifications
    alert_email_smtp: Optional[str] = None
    alert_email_port: int = 587
    alert_email_user: Optional[str] = None
    alert_email_password: Optional[str] = None
    alert_email_from: Optional[str] = None

    # App
    environment: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Vendor API keys
    ortex_api_key: Optional[str] = None
    ortex_base_url: str = "https://api.ortex.com/v1"
    fintel_api_key: Optional[str] = None
    fintel_base_url: str = "https://api.fintel.io/v1"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
