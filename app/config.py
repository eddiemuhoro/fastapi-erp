"""
Configuration management for different environments
"""
import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Database settings
    mysql_host: str = "localhost"
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_database: str = "wholesale"
    mysql_port: int = 3306
    mysql_pool_size: int = 10
    mysql_max_overflow: int = 20
    
    # API settings
    api_title: str = "Wholesale API"
    api_description: str = "API for wholesale business data"
    api_version: str = "1.0.0"
    
    # Security settings
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # CORS settings
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
