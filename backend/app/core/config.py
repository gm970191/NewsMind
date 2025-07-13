"""
Configuration settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基本信息
    app_name: str = "NewsMind"
    app_version: str = "0.5.0"
    debug: bool = True
    
    # API配置
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # 数据库配置
    database_url: str = "sqlite:///./newsmind.db"
    
    # AI配置 - 已移除DeepSeek，仅使用本地LM Studio
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # 字段名映射
        fields = {
            # 已移除DeepSeek配置
            'database_url': {'env': 'DATABASE_URL'},
        }
    
    # 新闻采集配置
    max_articles_per_source: int = 20
    content_retention_days: int = 30
    
    # AI处理配置
    max_processing_batch_size: int = 10
    processing_delay_seconds: int = 1
    
    # 日志配置
    log_file: str = "newsmind.log"
    log_level: str = "INFO"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 验证必需的配置 - 允许在开发环境中跳过API密钥验证
        # AI功能使用本地LM Studio，无需API密钥


# 全局配置实例
settings = Settings() 