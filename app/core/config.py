from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional, Dict, Any, Union
import secrets
import json


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "Image to Video API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: str) -> str:
        if v.startswith("sqlite"):
            # For SQLite, convert to async URL
            return v.replace("sqlite://", "sqlite+aiosqlite://")
        return v
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_HOURS: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"])
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Try to parse as JSON first
            if v.startswith('['):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Otherwise split by comma
            return [i.strip() for i in v.split(",")]
        return v
    
    # API Keys
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    KLING_ACCESS_KEY: str = Field(..., env="KLING_ACCESS_KEY")
    KLING_SECRET_KEY: str = Field(..., env="KLING_SECRET_KEY")
    
    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_JSON: Optional[str] = Field(None, env="GOOGLE_SHEETS_CREDENTIALS_JSON")
    GOOGLE_SHEETS_SPREADSHEET_ID: Optional[str] = Field(None, env="GOOGLE_SHEETS_SPREADSHEET_ID")
    
    # Storage
    UPLOAD_DIR: str = Field(default="./uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=20 * 1024 * 1024, env="MAX_FILE_SIZE")  # 20MB
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()