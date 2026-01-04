"""
Configuration settings for the Land Detection System
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Cloud-Native Land Detection System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # S3 Buckets
    S3_SATELLITE_DATA_BUCKET: str = os.getenv("S3_SATELLITE_DATA_BUCKET", "land-detection-satellite-data")
    S3_ML_MODELS_BUCKET: str = os.getenv("S3_ML_MODELS_BUCKET", "land-detection-ml-models")
    S3_RESULTS_BUCKET: str = os.getenv("S3_RESULTS_BUCKET", "land-detection-results")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/land_detection"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Model Configuration
    MODEL_CONFIDENCE_THRESHOLD: float = 0.75
    BATCH_SIZE: int = 32
    
    # SageMaker
    SAGEMAKER_ENDPOINT_NAME: str = os.getenv("SAGEMAKER_ENDPOINT_NAME", "land-detection-endpoint")
    
    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
