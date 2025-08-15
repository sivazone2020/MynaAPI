from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str
    
    # Pinecone Configuration
    pinecone_api_key: str
    pinecone_host: str
    pinecone_index: str
    
    # JWT Configuration
    jwt_secret_key: str = "myna-api-secret-key-2024"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Application Configuration
    log_level: str = "INFO"
    environment: str = "development"
    
    # API Configuration
    api_version: str = "v1"
    api_title: str = "MynaAPI"
    api_description: str = "Backend service for college recommendation system"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create a global settings instance
settings = Settings()
