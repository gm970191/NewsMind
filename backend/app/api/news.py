"""
News API endpoints - 简化版
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.news_service import NewsRepository
from app.services.crawler import NewsCrawler

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/articles")
async def get_articles(
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """获取新闻文章列表"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        articles = repo.get_articles(limit=limit, skip=skip)
        return {
            "articles": [
                {
                    "id": article.id,
                    "original_title": article.original_title,
                    "original_summary": article.original_summary,
                    "translated_title": article.translated_title,
                    "translated_summary": article.translated_summary,
                    "source_name": article.source_name,
                    "source_url": article.source_url,
                    "category": article.category,
                    "is_translated": article.is_translated,
                    "created_at": article.created_at
                }
                for article in articles
            ]
        }
    finally:
        db.close()


@router.get("/articles/{article_id}")
async def get_article(article_id: int):
    """获取单篇文章详情"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        article = repo.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return {
            "id": article.id,
            "original_title": article.original_title,
            "original_summary": article.original_summary,
            "translated_title": article.translated_title,
            "translated_summary": article.translated_summary,
            "source_name": article.source_name,
            "source_url": article.source_url,
            "category": article.category,
            "is_translated": article.is_translated,
            "created_at": article.created_at
        }
    finally:
        db.close()


@router.post("/crawl")
async def crawl_news():
    """抓取当天新闻"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        crawler = NewsCrawler(repo)
        result = await crawler.crawl_today_news()
        
        return {
            "message": "News crawling completed",
            "new_articles": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawling failed: {str(e)}")
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
    finally:
        db.close() 