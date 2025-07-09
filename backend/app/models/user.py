"""
User preferences and system configuration models
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text, Integer, Boolean

from app.core.database import Base


class UserPreference(Base):
    """用户偏好表"""
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=True)
    description = Column(String(500), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserPreference(key='{self.key}', value='{self.value}')>"


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=True)
    description = Column(String(500), nullable=True)
    is_public = Column(Boolean, default=False)  # 是否公开配置
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', value='{self.value}')>" 