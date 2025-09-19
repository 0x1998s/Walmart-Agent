# 🛒 沃尔玛AI Agent平台 - 配置管理
# Walmart AI Agent Platform - Configuration Management

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # ===== 基础配置 =====
    APP_NAME: str = "沃尔玛AI Agent平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # ===== 服务器配置 =====
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8080, env="PORT")
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"], 
        env="ALLOWED_HOSTS"
    )
    
    # ===== 数据库配置 =====
    DATABASE_URL: str = Field(
        default="postgresql://walmart_admin:walmart_secure_2024@localhost:5432/walmart_ai_agent",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # ===== Redis配置 =====
    REDIS_URL: str = Field(
        default="redis://:walmart_redis_2024@localhost:6379/0",
        env="REDIS_URL"
    )
    REDIS_POOL_SIZE: int = Field(default=10, env="REDIS_POOL_SIZE")
    
    # ===== 向量数据库配置 =====
    CHROMA_HOST: str = Field(default="localhost", env="CHROMA_HOST")
    CHROMA_PORT: int = Field(default=8000, env="CHROMA_PORT")
    CHROMA_AUTH_USER: str = Field(default="admin", env="CHROMA_AUTH_USER")
    CHROMA_AUTH_PASSWORD: str = Field(default="walmart_chroma_2024", env="CHROMA_AUTH_PASSWORD")
    
    # ===== AI模型配置 =====
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    
    # ChatGLM
    CHATGLM_API_KEY: Optional[str] = Field(default=None, env="CHATGLM_API_KEY")
    CHATGLM_BASE_URL: str = Field(default="https://open.bigmodel.cn/api/paas/v4", env="CHATGLM_BASE_URL")
    CHATGLM_MODEL: str = Field(default="glm-4", env="CHATGLM_MODEL")
    
    # DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL: str = Field(default="https://api.deepseek.com", env="DEEPSEEK_BASE_URL")
    DEEPSEEK_MODEL: str = Field(default="deepseek-chat", env="DEEPSEEK_MODEL")
    
    # ===== Dify配置 =====
    DIFY_API_URL: str = Field(default="http://localhost:8001", env="DIFY_API_URL")
    DIFY_API_KEY: Optional[str] = Field(default=None, env="DIFY_API_KEY")
    DIFY_APP_TOKEN: Optional[str] = Field(default=None, env="DIFY_APP_TOKEN")
    
    # ===== 文件存储配置 =====
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_FILE_SIZE: int = Field(default=100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=[".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".csv", ".json"],
        env="ALLOWED_FILE_TYPES"
    )
    
    # ===== 安全配置 =====
    SECRET_KEY: str = Field(
        default="walmart-ai-agent-super-secret-key-2024",
        env="SECRET_KEY"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # ===== Celery配置 =====
    CELERY_BROKER_URL: str = Field(
        default="redis://:walmart_redis_2024@localhost:6379/1",
        env="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://:walmart_redis_2024@localhost:6379/2",
        env="CELERY_RESULT_BACKEND"
    )
    
    # ===== 监控配置 =====
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    # ===== 业务配置 =====
    DEFAULT_EMBEDDING_MODEL: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        env="DEFAULT_EMBEDDING_MODEL"
    )
    MAX_CONTEXT_LENGTH: int = Field(default=4000, env="MAX_CONTEXT_LENGTH")
    SIMILARITY_THRESHOLD: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取应用设置（缓存）"""
    return Settings()
