#!/usr/bin/env python3
"""
比较AI处理速度优化效果
"""
import asyncio
import time
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.ai_processor import AIProcessor
from app.services.fast_ai_processor import FastAIProcessor
from app.models.news import NewsRepository
from app.core.database import get_db

async def compare_ai_speed():
    """比较AI处理速度"""
    print("🚀 开始比较AI处理速度...")
    
    # 获取数据库连接
    db = next(get_db())
    repo = NewsRepository(db)
    
    try:
        # 获取未处理的文章
        unprocessed_articles = repo.get_unprocessed_articles(limit=2)
        
        if len(unprocessed_articles) < 2:
            print("❌ 需要至少2篇未处理文章进行对比测试")
            return
        
        article1, article2 = unprocessed_articles[0], unprocessed_articles[1]
        
        print(f"📰 测试文章1: {article1.title[:30]}...")
        print(f"📰 测试文章2: {article2.title[:30]}...")
        
        # 测试标准AI处理器
        print("\n" + "="*50)
        print("🔧 测试标准AI处理器")
        print("="*50)
        
        processor_standard = AIProcessor(repo)
        
        # 处理第一篇文章
        start_time = time.time()
        success1 = await processor_standard.process_single_article(article1)
        time1 = time.time() - start_time
        
        if success1:
            print(f"✅ 标准处理文章1成功: {time1:.1f}秒")
        else:
            print(f"❌ 标准处理文章1失败: {time1:.1f}秒")
        
        # 测试快速AI处理器
        print("\n" + "="*50)
        print("⚡ 测试快速AI处理器")
        print("="*50)
        
        processor_fast = FastAIProcessor(repo)
        
        # 处理第二篇文章
        start_time = time.time()
        success2 = await processor_fast.process_single_article_fast(article2)
        time2 = time.time() - start_time
        
        if success2:
            print(f"✅ 快速处理文章2成功: {time2:.1f}秒")
        else:
            print(f"❌ 快速处理文章2失败: {time2:.1f}秒")
        
        # 比较结果
        print("\n" + "="*50)
        print("📊 速度对比结果")
        print("="*50)
        
        if success1 and success2:
            speedup = time1 / time2 if time2 > 0 else float('inf')
            print(f"⏱️  标准AI处理器: {time1:.1f}秒")
            print(f"⚡ 快速AI处理器: {time2:.1f}秒")
            print(f"🚀 速度提升: {speedup:.1f}倍")
            
            if speedup > 1.5:
                print("🎉 快速处理器显著提升了处理速度！")
            elif speedup > 1.1:
                print("👍 快速处理器有一定速度提升")
            else:
                print("⚠️  速度提升不明显，可能需要进一步优化")
        else:
            print("❌ 无法进行速度对比，因为处理失败")
        
        # 获取处理结果对比
        if success1:
            processed1 = repo.get_processed_content_by_article_id(article1.id)
            if processed1:
                print(f"\n📝 标准处理结果:")
                print(f"   中文摘要长度: {len(processed1.summary_zh) if processed1.summary_zh else 0}字符")
                print(f"   英文摘要长度: {len(processed1.summary_en) if processed1.summary_en else 0}字符")
        
        if success2:
            processed2 = repo.get_processed_content_by_article_id(article2.id)
            if processed2:
                print(f"\n📝 快速处理结果:")
                print(f"   中文摘要长度: {len(processed2.summary_zh) if processed2.summary_zh else 0}字符")
                print(f"   英文摘要长度: {len(processed2.summary_en) if processed2.summary_en else 0}字符")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(compare_ai_speed()) 