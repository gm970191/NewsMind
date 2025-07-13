"""
News service - 简化版
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.news import NewsArticle, NewsSource

logger = logging.getLogger(__name__)


class NewsRepository:
    """新闻数据仓库 - 简化版"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_active_sources(self) -> List[NewsSource]:
        """获取活跃的新闻源"""
        return self.db.query(NewsSource).filter(NewsSource.is_active == True).all()
    
    def get_articles(self, limit: int = 20, skip: int = 0) -> List[NewsArticle]:
        """获取新闻文章列表"""
        return self.db.query(NewsArticle).order_by(desc(NewsArticle.created_at)).offset(skip).limit(limit).all()
    
    def get_article_by_id(self, article_id: int) -> Optional[NewsArticle]:
        """根据ID获取文章"""
        return self.db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
    
    def get_untranslated_articles(self, limit: int = 10) -> List[NewsArticle]:
        """获取未翻译的文章"""
        return self.db.query(NewsArticle).filter(NewsArticle.is_translated == False).order_by(desc(NewsArticle.created_at)).limit(limit).all()
    
    def get_untranslated_count(self) -> int:
        """获取未翻译文章数量"""
        return self.db.query(func.count(NewsArticle.id)).filter(NewsArticle.is_translated == False).scalar()
    
    def save_article(self, article_data: Dict[str, Any]) -> Optional[NewsArticle]:
        """保存文章"""
        try:
            # 检查是否已存在
            existing = self.db.query(NewsArticle).filter(NewsArticle.source_url == article_data['source_url']).first()
            if existing:
                return existing
            
            article = NewsArticle(**article_data)
            self.db.add(article)
            self.db.commit()
            self.db.refresh(article)
            return article
        except Exception as e:
            logger.error(f"保存文章失败: {e}")
            self.db.rollback()
            return None
    
    def update_article_translation(self, article_id: int, translated_title: str, translated_summary: str) -> bool:
        """更新文章翻译"""
        try:
            article = self.db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
            if article:
                article.translated_title = translated_title
                article.translated_summary = translated_summary
                article.is_translated = True
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"更新翻译失败: {e}")
            self.db.rollback()
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            total_articles = self.db.query(func.count(NewsArticle.id)).scalar()
            translated_articles = self.db.query(func.count(NewsArticle.id)).filter(NewsArticle.is_translated == True).scalar()
            untranslated_articles = total_articles - translated_articles
            total_sources = self.db.query(func.count(NewsSource.id)).filter(NewsSource.is_active == True).scalar()
            
            return {
                "total_articles": total_articles,
                "translated_articles": translated_articles,
                "untranslated_articles": untranslated_articles,
                "total_sources": total_sources
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {} 