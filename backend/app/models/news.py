"""
News-related database models
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class NewsSource(Base):
    """新闻源表"""
    __tablename__ = "news_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(500), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # 'web' or 'rss'
    category = Column(String(100), nullable=True)  # 政治、科技、财经、军事等
    weight = Column(Float, default=1.0)  # 权重，用于排序
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    articles = relationship("NewsArticle", back_populates="source")

    def __repr__(self):
        return f"<NewsSource(id={self.id}, name='{self.name}', type='{self.type}')>"


class NewsArticle(Base):
    """新闻文章表 - 重新设计，包含原始字段和翻译字段"""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    
    # 原始字段
    original_title = Column(String(500), nullable=False, index=True)  # 原始标题
    original_content = Column(Text, nullable=False)  # 原始内容
    original_language = Column(String(10), nullable=True)  # 检测到的原始语言
    
    # 翻译字段
    translated_title = Column(String(500), nullable=True, index=True)  # 中文翻译标题
    translated_content = Column(Text, nullable=True)  # 中文翻译内容
    
    # AI处理字段
    summary_zh = Column(Text, nullable=True)  # 中文摘要
    detailed_summary_zh = Column(Text, nullable=True)  # 中文详细摘要
    
    # 翻译状态字段
    is_title_translated = Column(Boolean, default=False)  # 标题是否已翻译
    is_content_translated = Column(Boolean, default=False)  # 内容是否已翻译
    translation_quality_score = Column(Float, default=0.0)  # 翻译质量评分
    
    # 其他字段
    source_url = Column(String(500), nullable=False, unique=True)
    source_id = Column(Integer, ForeignKey("news_sources.id"), nullable=False)
    source_name = Column(String(255), nullable=False)  # 冗余字段，便于查询
    publish_time = Column(DateTime, nullable=True)
    category = Column(String(100), nullable=True)  # 分类标签
    quality_score = Column(Float, default=0.0)  # 整体质量评分
    is_processed = Column(Boolean, default=False)  # 是否已AI处理
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    source = relationship("NewsSource", back_populates="articles")
    # processed_content 字段已移除

    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.original_title[:50]}...')>"


# ProcessedContent 模型已移除 