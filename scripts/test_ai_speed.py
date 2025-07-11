#!/usr/bin/env python3
"""
测试AI处理速度优化效果
"""
import asyncio
import time
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.ai_processor import AIProcessor
from app.models.news import NewsRepository
from app.core.database import get_db

async def test_ai_speed():
    """测试AI处理速度"""
    print("🚀 开始测试AI处理速度...")
    
    # 获取数据库连接
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        # 创建AI处理器
        processor = AIProcessor(repo)
        
        # 获取一篇未处理的文章
        unprocessed_articles = repo.get_unprocessed_articles(limit=1)
        
        if not unprocessed_articles:
            print("❌ 没有找到未处理的文章")
            return
        
        article = unprocessed_articles[0]
        print(f"📰 测试文章: {article.title[:50]}...")
        print(f"📏 内容长度: {len(article.content)} 字符")
        print(f"🌐 语言: {article.language}")
        
        # 记录开始时间
        start_time = time.time()
        
        # 处理文章
        success = await processor.process_single_article(article)
        
        # 计算耗时
        processing_time = time.time() - start_time
        
        if success:
            print(f"✅ AI处理成功!")
            print(f"⏱️  总耗时: {processing_time:.1f} 秒")
            
            # 获取处理结果
            processed_content = repo.get_processed_content_by_article_id(article.id)
            if processed_content:
                print(f"📝 中文摘要长度: {len(processed_content.summary_zh) if processed_content.summary_zh else 0} 字符")
                print(f"📝 英文摘要长度: {len(processed_content.summary_en) if processed_content.summary_en else 0} 字符")
                if processed_content.translation_zh:
                    print(f"🌐 翻译长度: {len(processed_content.translation_zh)} 字符")
                print(f"⭐ 质量评分: {processed_content.quality_score}")
        else:
            print(f"❌ AI处理失败，耗时: {processing_time:.1f} 秒")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_ai_speed()) 