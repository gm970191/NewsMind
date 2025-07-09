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
    """新闻文章表"""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=False, unique=True)
    source_id = Column(Integer, ForeignKey("news_sources.id"), nullable=False)
    source_name = Column(String(255), nullable=False)  # 冗余字段，便于查询
    publish_time = Column(DateTime, nullable=True)
    language = Column(String(10), nullable=True)  # 检测到的语言
    category = Column(String(100), nullable=True)  # 分类标签
    quality_score = Column(Float, default=0.0)  # 质量评分
    is_processed = Column(Boolean, default=False)  # 是否已AI处理
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    source = relationship("NewsSource", back_populates="articles")
    processed_content = relationship("ProcessedContent", back_populates="article", uselist=False)

    def __repr__(self):
        return f"<NewsArticle(id={self.id}, title='{self.title[:50]}...')>"


class ProcessedContent(Base):
    """AI处理结果表"""
    __tablename__ = "processed_content"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=False, unique=True)
    summary_zh = Column(Text, nullable=True)  # 中文摘要
    summary_en = Column(Text, nullable=True)  # 英文摘要
    translation_zh = Column(Text, nullable=True)  # 中文翻译
    quality_score = Column(Float, default=0.0)  # AI评估的质量分数
    processing_time = Column(Float, nullable=True)  # 处理耗时（秒）
    api_calls_used = Column(Integer, default=0)  # 使用的API调用次数
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    article = relationship("NewsArticle", back_populates="processed_content")

    def __repr__(self):
        return f"<ProcessedContent(id={self.id}, article_id={self.article_id})>" 