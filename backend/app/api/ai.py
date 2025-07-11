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
                    "original_title": item['article'].original_title,
                    "translated_title": item['article'].translated_title,
                    "display_title": item['article'].translated_title if item['article'].translated_title else item['article'].original_title,
                    "original_content": item['article'].original_content[:200] + "..." if len(item['article'].original_content) > 200 else item['article'].original_content,
                    "translated_content": item['article'].translated_content[:200] + "..." if item['article'].translated_content and len(item['article'].translated_content) > 200 else item['article'].translated_content,
                    "source_url": item['article'].source_url,
                    "source_name": item['article'].source_name,
                    "category": item['article'].category,
                    "original_language": item['article'].original_language,
                    "is_title_translated": item['article'].is_title_translated,
                    "is_content_translated": item['article'].is_content_translated,
                    "publish_time": item['article'].publish_time,
                    "created_at": item['article'].created_at,
                    "processed_content": {
                        "summary_zh": item['processed_content'].summary_zh,
                        "summary_en": item['processed_content'].summary_en,
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
        
        # 获取AI处理结果
        processed_content = repo.get_processed_content_by_article_id(article_id)
        
        # 分析状态
        has_summary_zh = processed_content and processed_content.summary_zh and len(processed_content.summary_zh.strip()) > 0
        has_summary_en = processed_content and processed_content.summary_en and len(processed_content.summary_en.strip()) > 0
        has_translation = processed_content and processed_content.translation_zh and len(processed_content.translation_zh.strip()) > 0
        
        needs_summary = not has_summary_zh or not has_summary_en
        needs_translation = article.original_language not in ['zh', 'zh-CN'] and not has_translation
        
        return {
            "article_id": article_id,
            "original_title": article.original_title,
            "translated_title": article.translated_title,
            "display_title": article.translated_title if article.translated_title else article.original_title,
            "original_language": article.original_language,
            "is_processed": article.is_processed,
            "has_summary_zh": has_summary_zh,
            "has_summary_en": has_summary_en,
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


@router.post("/process-button/{article_id}")
async def process_article_button(article_id: int):
    """AI处理按钮 - 处理指定文章"""
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        processor = AIProcessor(repo)
        
        # 检查文章是否存在
        article = repo.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # 检查当前处理状态
        processed_content = repo.get_processed_content_by_article_id(article_id)
        
        has_summary_zh = processed_content and processed_content.summary_zh and len(processed_content.summary_zh.strip()) > 0
        has_summary_en = processed_content and processed_content.summary_en and len(processed_content.summary_en.strip()) > 0
        has_translation = processed_content and processed_content.translation_zh and len(processed_content.translation_zh.strip()) > 0
        
        needs_summary = not has_summary_zh or not has_summary_en
        needs_translation = article.original_language not in ['zh', 'zh-CN'] and not has_translation
        
        if needs_summary or needs_translation:
            # 执行AI处理
            success = await processor.process_single_article(article)
            
            if success:
                # 重新获取处理结果
                new_processed_content = repo.get_processed_content_by_article_id(article_id)
                
                return {
                    "success": True,
                    "message": "AI处理完成",
                    "article_id": article_id,
                    "processing_result": {
                        "summary_zh": new_processed_content.summary_zh if new_processed_content else None,
                        "summary_en": new_processed_content.summary_en if new_processed_content else None,
                        "translation_zh": new_processed_content.translation_zh if new_processed_content else None,
                        "quality_score": new_processed_content.quality_score if new_processed_content else None
                    }
                }
            else:
                raise HTTPException(status_code=500, detail="AI processing failed")
        else:
            return {
                "success": True,
                "message": "文章已完全处理",
                "article_id": article_id
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        db.close() 