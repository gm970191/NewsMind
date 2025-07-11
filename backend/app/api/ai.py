"""
AI processing API endpoints
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.core.database import get_db
from app.services.news_service import NewsRepository
from app.services.ai_processor import AIProcessor

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/process")
async def process_articles(
    limit: int = Query(10, ge=1, le=50, description="处理文章数量限制")
):
    """批量处理未处理的文章"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        processor = AIProcessor(repo)
        results = await processor.process_articles(limit)
        
        return {
            "message": "AI processing completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        db.close()


@router.post("/process/{article_id}")
async def process_single_article(article_id: int):
    """处理单篇文章"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        processor = AIProcessor(repo)
        success = await processor.process_single_article_by_id(article_id)
        
        if success:
            return {
                "message": f"Article {article_id} processed successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Article not found or processing failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        db.close()


@router.get("/statistics")
async def get_ai_statistics():
    """获取AI处理统计信息"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        processor = AIProcessor(repo)
        stats = await processor.get_processing_stats()
        
        return {
            "ai_processing_statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
    finally:
        db.close()


@router.get("/unprocessed-count")
async def get_unprocessed_count():
    """获取未处理文章数量"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        unprocessed_articles = repo.get_unprocessed_articles(limit=1000)  # 获取所有未处理文章
        count = len(unprocessed_articles)
        
        return {
            "unprocessed_count": count
        }
    finally:
        db.close()


@router.get("/article-status/{article_id}")
async def get_article_processing_status(article_id: int):
    """获取文章的处理状态"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        # 获取文章信息
        article = repo.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # 直接从文章对象获取AI处理结果
        has_summary_zh = article.summary_zh and len(article.summary_zh.strip()) > 0
        has_detailed_summary_zh = article.detailed_summary_zh and len(article.detailed_summary_zh.strip()) > 0
        has_translation = article.translated_content and len(article.translated_content.strip()) > 0
        
        needs_summary = not has_summary_zh or not has_detailed_summary_zh
        needs_translation = article.original_language not in ['zh', 'zh-CN'] and not has_translation
        
        return {
            "article_id": article_id,
            "original_title": article.original_title,
            "translated_title": article.translated_title,
            "display_title": article.translated_title if article.translated_title else article.original_title,
            "original_language": article.original_language,
            "is_processed": article.is_processed,
            "has_summary_zh": has_summary_zh,
            "has_detailed_summary_zh": has_detailed_summary_zh,
            "has_translation": has_translation,
            "needs_summary": needs_summary,
            "needs_translation": needs_translation,
            "needs_processing": needs_summary or needs_translation
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")
    finally:
        db.close() 