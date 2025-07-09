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


@router.post("/reprocess/{article_id}")
async def reprocess_article(article_id: int):
    """重新处理指定文章"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        processor = AIProcessor(repo)
        success = await processor.reprocess_article(article_id)
        
        if success:
            return {
                "message": f"Article {article_id} reprocessed successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Article not found or reprocessing failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reprocessing failed: {str(e)}")
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


@router.get("/processed-articles")
async def get_processed_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    min_quality: Optional[float] = Query(None, ge=0.0, le=10.0)
):
    """获取已处理且包含AI处理结果的文章"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        articles_with_content = repo.get_processed_articles_with_content(
            skip=skip,
            limit=limit,
            category=category,
            min_quality=min_quality
        )
        
        return {
            "articles": [
                {
                    "id": item['article'].id,
                    "title": item['article'].title,
                    "content": item['article'].content[:200] + "..." if len(item['article'].content) > 200 else item['article'].content,
                    "source_url": item['article'].source_url,
                    "source_name": item['article'].source_name,
                    "category": item['article'].category,
                    "language": item['article'].language,
                    "publish_time": item['article'].publish_time,
                    "created_at": item['article'].created_at,
                    "ai_processing": {
                        "summary_zh": item['processed_content'].summary_zh,
                        "summary_en": item['processed_content'].summary_en,
                        "translation_zh": item['processed_content'].translation_zh,
                        "quality_score": item['processed_content'].quality_score,
                        "processing_time": item['processed_content'].processing_time
                    }
                }
                for item in articles_with_content
            ],
            "total": len(articles_with_content),
            "skip": skip,
            "limit": limit
        }
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