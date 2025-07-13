"""
News-related database models - 简化版
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class NewsSource(Base):
    """新闻源表"""
    __tablename__ = "news_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(500), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # 'rss' or 'web'
    category = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    articles = relationship("NewsArticle", back_populates="source")

    def __repr__(self):
        return f"<NewsSource(id={self.id}, name='{self.name}', type='{self.type}')>"


class NewsArticle(Base):
    """新闻文章表 - 简化版"""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    
    # 原始字段
    original_title = Column(String(500), nullable=False, index=True)  # 原始标题
    original_summary = Column(Text, nullable=False)  # 原始概要
    
    # 翻译字段
    translated_title = Column(String(500), nullable=True, index=True)  # 中文翻译标题
    translated_summary = Column(Text, nullable=True)  # 中文翻译概要
    
    # 其他字段
    source_url = Column(String(500), nullable=False, unique=True)
    source_id = Column(Integer, ForeignKey("news_sources.id"), nullable=False)
    source_name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    is_translated = Column(Boolean, default=False)  # 是否已翻译
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    source = relationship("NewsSource", back_populates="articles")

    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.original_title[:50]}...')>" 