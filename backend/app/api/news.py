"""
News API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.news_service import NewsRepository
from app.services.crawler import WebCrawler
from app.models.news import NewsArticle, NewsSource

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/articles")
async def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    source_id: Optional[int] = None,
    language: Optional[str] = None,
    is_processed: Optional[bool] = None,
    date: Optional[str] = None,
    order_by: str = Query("created_at", regex="^(created_at|publish_time|original_title|translated_title)$"),
    order_desc: bool = Query(True)
):
    """获取新闻文章列表"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        articles = repo.get_articles(
            skip=skip,
            limit=limit,
            category=category,
            source_id=source_id,
            language=language,
            is_processed=is_processed,
            date=date,
            order_by=order_by,
            order_desc=order_desc
        )
        
        return {
            "articles": [
                {
                    "id": article.id,
                    "original_title": article.original_title,
                    "translated_title": article.translated_title,
                    "display_title": article.translated_title if article.translated_title else article.original_title,
                    "original_content": article.original_content[:200] + "..." if len(article.original_content) > 200 else article.original_content,
                    "translated_content": article.translated_content[:200] + "..." if article.translated_content and len(article.translated_content) > 200 else article.translated_content,
                    "summary_zh": article.summary_zh,
                    "detailed_summary_zh": article.detailed_summary_zh,
                    "source_url": article.source_url,
                    "source_name": article.source_name,
                    "publish_time": article.publish_time,
                    "category": article.category,
                    "original_language": article.original_language,
                    "is_title_translated": article.is_title_translated,
                    "is_content_translated": article.is_content_translated,
                    "translation_quality_score": article.translation_quality_score,
                    "quality_score": article.quality_score,
                    "is_processed": article.is_processed,
                    "created_at": article.created_at
                }
                for article in articles
            ],
            "total": len(articles),
            "skip": skip,
            "limit": limit
        }
    finally:
        db.close()


@router.get("/articles/{article_id}")
async def get_article(article_id: int):
    """获取新闻文章详情"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        article = repo.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return {
            "id": article.id,
            "original_title": article.original_title,
            "translated_title": article.translated_title,
            "display_title": article.translated_title if article.translated_title else article.original_title,
            "original_content": article.original_content,
            "translated_content": article.translated_content,
            "summary_zh": article.summary_zh,
            "detailed_summary_zh": article.detailed_summary_zh,
            "source_url": article.source_url,
            "source_name": article.source_name,
            "publish_time": article.publish_time,
            "category": article.category,
            "original_language": article.original_language,
            "is_title_translated": article.is_title_translated,
            "is_content_translated": article.is_content_translated,
            "translation_quality_score": article.translation_quality_score,
            "quality_score": article.quality_score,
            "is_processed": article.is_processed,
            "created_at": article.created_at
        }
    finally:
        db.close()


@router.get("/search")
async def search_articles(
    keyword: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100)
):
    """搜索新闻文章"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        articles = repo.search_articles(keyword, limit)
        
        return {
            "articles": [
                {
                    "id": article.id,
                    "original_title": article.original_title,
                    "translated_title": article.translated_title,
                    "display_title": article.translated_title if article.translated_title else article.original_title,
                    "original_content": article.original_content[:200] + "..." if len(article.original_content) > 200 else article.original_content,
                    "translated_content": article.translated_content[:200] + "..." if article.translated_content and len(article.translated_content) > 200 else article.translated_content,
                    "source_url": article.source_url,
                    "source_name": article.source_name,
                    "category": article.category,
                    "original_language": article.original_language,
                    "is_title_translated": article.is_title_translated,
                    "created_at": article.created_at
                }
                for article in articles
            ],
            "keyword": keyword,
            "total": len(articles)
        }
    finally:
        db.close()


@router.get("/sources")
async def get_sources():
    """获取新闻源列表"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        sources = repo.get_active_sources()
        
        return {
            "sources": [
                {
                    "id": source.id,
                    "name": source.name,
                    "url": source.url,
                    "type": source.type,
                    "category": source.category,
                    "weight": source.weight,
                    "is_active": source.is_active,
                    "created_at": source.created_at
                }
                for source in sources
            ],
            "total": len(sources)
        }
    finally:
        db.close()


@router.get("/statistics")
async def get_statistics():
    """获取统计信息"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        stats = repo.get_statistics()
        return stats
    finally:
        db.close()


@router.post("/crawl")
async def manual_crawl():
    """手动触发新闻采集"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        async with WebCrawler(repo) as crawler:
            results = await crawler.crawl_news_sources()
            
            return {
                "message": "News crawling completed",
                "results": results
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawling failed: {str(e)}")
    finally:
        db.close()


@router.post("/cleanup")
async def manual_cleanup():
    """手动触发数据清理"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        deleted_count = repo.delete_old_articles()
        
        return {
            "message": "Data cleanup completed",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
    finally:
        db.close() 