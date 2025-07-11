"""
News service layer - Repository pattern implementation
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_, or_, func

from app.models.news import NewsArticle, NewsSource, ProcessedContent
from app.core.config import settings


class NewsRepository:
    """新闻数据访问层"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # NewsSource operations
    def create_source(self, source_data: Dict[str, Any]) -> NewsSource:
        """创建新闻源"""
        source = NewsSource(**source_data)
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source
    
    def get_source_by_id(self, source_id: int) -> Optional[NewsSource]:
        """根据ID获取新闻源"""
        return self.db.query(NewsSource).filter(NewsSource.id == source_id).first()
    
    def get_source_by_url(self, url: str) -> Optional[NewsSource]:
        """根据URL获取新闻源"""
        return self.db.query(NewsSource).filter(NewsSource.url == url).first()
    
    def get_active_sources(self) -> List[NewsSource]:
        """获取所有活跃的新闻源"""
        return self.db.query(NewsSource).filter(NewsSource.is_active == True).all()
    
    def get_sources_by_category(self, category: str) -> List[NewsSource]:
        """根据分类获取新闻源"""
        return self.db.query(NewsSource).filter(
            and_(NewsSource.category == category, NewsSource.is_active == True)
        ).all()
    
    def update_source(self, source_id: int, update_data: Dict[str, Any]) -> Optional[NewsSource]:
        """更新新闻源"""
        source = self.get_source_by_id(source_id)
        if source:
            for key, value in update_data.items():
                setattr(source, key, value)
            source.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(source)
        return source
    
    def delete_source(self, source_id: int) -> bool:
        """删除新闻源"""
        source = self.get_source_by_id(source_id)
        if source:
            self.db.delete(source)
            self.db.commit()
            return True
        return False
    
    # NewsArticle operations
    def create_article(self, article_data: Dict[str, Any]) -> NewsArticle:
        """创建新闻文章"""
        article = NewsArticle(**article_data)
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article
    
    def get_article_by_id(self, article_id: int) -> Optional[NewsArticle]:
        """根据ID获取新闻文章"""
        return self.db.query(NewsArticle).filter(NewsArticle.id == article_id).first()
    
    def get_article_by_url(self, source_url: str) -> Optional[NewsArticle]:
        """根据URL获取新闻文章"""
        return self.db.query(NewsArticle).filter(NewsArticle.source_url == source_url).first()
    
    def get_articles(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        source_id: Optional[int] = None,
        language: Optional[str] = None,
        is_processed: Optional[bool] = None,
        date: Optional[str] = None,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> List[NewsArticle]:
        """获取新闻文章列表"""
        query = self.db.query(NewsArticle)
        
        # 添加过滤条件
        if category:
            query = query.filter(NewsArticle.category == category)
        if source_id:
            query = query.filter(NewsArticle.source_id == source_id)
        if language:
            query = query.filter(NewsArticle.original_language == language)
        if is_processed is not None:
            query = query.filter(NewsArticle.is_processed == is_processed)
        if date:
            # 处理日期过滤
            from datetime import datetime, timedelta
            from sqlalchemy import func
            today = datetime.utcnow().date()
            if date == "today":
                query = query.filter(func.date(NewsArticle.created_at) == today)
            elif date == "yesterday":
                yesterday = today - timedelta(days=1)
                query = query.filter(func.date(NewsArticle.created_at) == yesterday)
            elif date == "week":
                week_ago = today - timedelta(days=7)
                query = query.filter(NewsArticle.created_at >= week_ago)
            elif date == "month":
                month_ago = today - timedelta(days=30)
                query = query.filter(NewsArticle.created_at >= month_ago)
        
        # 排序
        if order_desc:
            query = query.order_by(desc(getattr(NewsArticle, order_by)))
        else:
            query = query.order_by(asc(getattr(NewsArticle, order_by)))
        
        return query.offset(skip).limit(limit).all()
    
    def get_recent_articles(self, days: int = 7) -> List[NewsArticle]:
        """获取最近几天的文章"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(NewsArticle).filter(
            NewsArticle.created_at >= cutoff_date
        ).order_by(desc(NewsArticle.created_at)).all()
    
    def update_article(self, article_id: int, update_data: Dict[str, Any]) -> Optional[NewsArticle]:
        """更新新闻文章"""
        article = self.get_article_by_id(article_id)
        if article:
            for key, value in update_data.items():
                setattr(article, key, value)
            article.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(article)
        return article
    
    def update_article_processed_status(self, article_id: int, is_processed: bool) -> bool:
        """更新文章处理状态"""
        article = self.get_article_by_id(article_id)
        if article:
            article.is_processed = is_processed
            article.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def delete_old_articles(self, days: int = None) -> int:
        """删除旧文章"""
        if days is None:
            days = settings.content_retention_days
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = self.db.query(NewsArticle).filter(
            NewsArticle.created_at < cutoff_date
        ).delete()
        self.db.commit()
        return deleted_count
    
    def search_articles(self, keyword: str, limit: int = 50) -> List[NewsArticle]:
        """搜索文章"""
        return self.db.query(NewsArticle).filter(
            or_(
                NewsArticle.original_title.contains(keyword),
                NewsArticle.translated_title.contains(keyword),
                NewsArticle.original_content.contains(keyword),
                NewsArticle.translated_content.contains(keyword)
            )
        ).order_by(desc(NewsArticle.created_at)).limit(limit).all()
    
    # ProcessedContent operations
    def create_processed_content(self, content_data: Dict[str, Any]) -> ProcessedContent:
        """创建处理结果"""
        content = ProcessedContent(**content_data)
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content
    
    def get_processed_content(self, article_id: int) -> Optional[ProcessedContent]:
        """获取文章的处理结果"""
        return self.db.query(ProcessedContent).filter(
            ProcessedContent.article_id == article_id
        ).first()
    
    def get_processed_content_by_article_id(self, article_id: int) -> Optional[ProcessedContent]:
        """根据文章ID获取处理结果（别名方法）"""
        return self.get_processed_content(article_id)
    
    def update_processed_content(
        self, article_id: int, update_data: Dict[str, Any]
    ) -> Optional[ProcessedContent]:
        """更新处理结果"""
        content = self.get_processed_content(article_id)
        if content:
            for key, value in update_data.items():
                setattr(content, key, value)
            content.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(content)
        return content
    
    def delete_processed_content(self, article_id: int) -> bool:
        """删除处理结果"""
        content = self.get_processed_content(article_id)
        if content:
            self.db.delete(content)
            self.db.commit()
            return True
        return False
    
    def get_unprocessed_articles(self, limit: int = 50) -> List[NewsArticle]:
        """获取未处理的文章"""
        return self.db.query(NewsArticle).filter(
            NewsArticle.is_processed == False
        ).order_by(asc(NewsArticle.created_at)).limit(limit).all()
    
    def get_processed_articles_with_content(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        min_quality: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """获取已处理且包含处理结果的文章"""
        query = self.db.query(NewsArticle, ProcessedContent).join(
            ProcessedContent, NewsArticle.id == ProcessedContent.article_id
        )
        
        if category:
            query = query.filter(NewsArticle.category == category)
        if min_quality:
            query = query.filter(ProcessedContent.quality_score >= min_quality)
        
        # 明确指定排序字段，避免ambiguous column错误
        results = query.order_by(desc(NewsArticle.created_at)).offset(skip).limit(limit).all()
        
        return [
            {
                'article': article,
                'processed_content': content
            }
            for article, content in results
        ]
    
    # Statistics
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_articles = self.db.query(NewsArticle).count()
        processed_articles = self.db.query(NewsArticle).filter(
            NewsArticle.is_processed == True
        ).count()
        total_sources = self.db.query(NewsSource).filter(
            NewsSource.is_active == True
        ).count()
        
        return {
            "total_articles": total_articles,
            "processed_articles": processed_articles,
            "unprocessed_articles": total_articles - processed_articles,
            "total_sources": total_sources,
            "processing_rate": (processed_articles / total_articles * 100) if total_articles > 0 else 0
        }
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """获取AI处理统计信息"""
        # 基础统计
        total_processed = self.db.query(ProcessedContent).count()
        
        # 平均质量分数
        avg_quality = self.db.query(func.avg(ProcessedContent.quality_score)).scalar()
        avg_quality = round(float(avg_quality), 2) if avg_quality else 0.0
        
        # 平均处理时间
        avg_processing_time = self.db.query(func.avg(ProcessedContent.processing_time)).scalar()
        avg_processing_time = round(float(avg_processing_time), 2) if avg_processing_time else 0.0
        
        # 质量分布
        quality_distribution = self.db.query(
            func.count(ProcessedContent.id).label('count'),
            func.floor(ProcessedContent.quality_score).label('score_range')
        ).group_by(func.floor(ProcessedContent.quality_score)).all()
        
        # 按分类统计 - 明确指定字段避免ambiguous column错误
        category_stats = self.db.query(
            NewsArticle.category,
            func.count(ProcessedContent.id).label('processed_count')
        ).join(ProcessedContent, NewsArticle.id == ProcessedContent.article_id).group_by(
            NewsArticle.category
        ).all()
        
        return {
            "total_processed": total_processed,
            "average_quality_score": avg_quality,
            "average_processing_time": avg_processing_time,
            "quality_distribution": [
                {"score_range": int(item.score_range), "count": item.count}
                for item in quality_distribution
            ],
            "category_statistics": [
                {"category": item.category, "processed_count": item.processed_count}
                for item in category_stats
            ]
        } 