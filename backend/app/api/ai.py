"""
AI processing API endpoints - 简化版
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.core.database import get_db
from app.services.news_service import NewsRepository
from app.services.ai_processor import AIProcessor

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/translate")
async def translate_articles(
    limit: int = Query(10, ge=1, le=50, description="翻译文章数量限制")
):
    """批量翻译未翻译的文章"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        processor = AIProcessor(repo)
        results = await processor.process_articles(limit)
        
        return {
            "message": "AI translation completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
    finally:
        db.close()


@router.post("/translate/{article_id}")
async def translate_single_article(article_id: int):
    """翻译单篇文章"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        processor = AIProcessor(repo)
        success = await processor.process_single_article_by_id(article_id)
        
        if success:
            return {
                "message": f"Article {article_id} translated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Article not found or translation failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
    finally:
        db.close()


@router.get("/statistics")
async def get_ai_statistics():
    """获取AI翻译统计信息"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        stats = repo.get_statistics()
        return {
            "translation_statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
    finally:
        db.close()


@router.get("/untranslated-count")
async def get_untranslated_count():
    """获取未翻译文章数量"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        count = repo.get_untranslated_count()
        
        return {
            "untranslated_count": count
        }
    finally:
        db.close()


@router.post("/trigger-translation")
async def trigger_translation():
    """手动触发AI翻译（用于测试或紧急处理）"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        from app.services.scheduler import news_scheduler
        
        # 直接调用翻译逻辑
        await news_scheduler._trigger_ai_translation(db, repo)
        
        return {
            "message": "AI translation triggered successfully",
            "note": "Check logs for detailed results"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation trigger failed: {str(e)}")
    finally:
        db.close() 