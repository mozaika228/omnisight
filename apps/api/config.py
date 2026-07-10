"""
OmniSight application configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API
    API_TITLE: str = "OmniSight API"
    API_VERSION: str = "0.1.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://omnisight:omnisight_dev_password@localhost:5432/omnisight"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    
    # Storage
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "omnisight"
    S3_SECRET_KEY: str = "omnisight_dev_password"
    S3_BUCKET: str = "omnisight-videos"
    
    # AI Models
    YOLO_MODEL: str = "yolov11n"
    WHISPER_MODEL: str = "base"
    EMBEDDING_MODEL: str = "openai/clip-vit-base-patch32"
    
    # Hardware
    DEVICE: str = "cpu"  # cuda or cpu
    ENABLE_GPU: bool = False
    
    # Logging
    LOG_LEVEL: str = "info"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
