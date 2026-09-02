from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    PROJECT_NAME: str = "NirikshanX"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./nirikshanx.db"
    JWT_SECRET_KEY: str = "nirikshanx-secret-key-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    PRODUCT_DETECTION_THRESHOLD: float = 0.60
    DEMO_MODE: bool = True
    AI_MODE: str = "demo"
    UPLOAD_DIR: str = "uploads"

settings = Settings()