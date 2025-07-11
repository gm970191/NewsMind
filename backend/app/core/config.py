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
    
    # DeepSeek API配置 - 从环境变量读取
    deepseek_api_key: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        # 字段名映射
        fields = {
            'deepseek_api_key': {'env': 'DEEPSEEK_API_KEY'},
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
        if not self.deepseek_api_key and not self.debug:
            raise ValueError("DEEPSEEK_API_KEY 环境变量未设置。请在 .env 文件中设置您的 API 密钥。")
        elif not self.deepseek_api_key:
            print("⚠️  警告: DEEPSEEK_API_KEY 未设置，AI功能将不可用")


# 全局配置实例
settings = Settings() 