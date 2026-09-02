import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "NirikshanX - AI Packaged Commodity Compliance"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-nirikshanx-key-2026-change-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 Days

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./nirikshanx.db")
    UPLOAD_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
    
    DEMO_MODE: bool = True
    DEBUG: bool = True

    class Config:
        case_sensitive = True

settings = Settings()
