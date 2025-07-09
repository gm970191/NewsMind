#!/usr/bin/env python3
"""
测试爬虫功能，手动触发新闻采集
"""
import sys
import os
import asyncio
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.services.news_service import NewsRepository
from app.services.crawler import WebCrawler


async def test_crawler():
    """测试爬虫功能"""
    print("=== 开始测试新闻采集 ===")
    
    # 创建数据库会话
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        # 获取所有活跃的新闻源
        sources = repo.get_active_sources()
        print(f"找到 {len(sources)} 个活跃新闻源:")
        for source in sources:
            print(f"  - {source.name} ({source.type}): {source.url}")
        
        # 开始采集
        print("\n开始采集新闻...")
        async with WebCrawler(repo) as crawler:
            results = await crawler.crawl_news_sources()
        
        # 显示结果
        print(f"\n采集结果:")
        print(f"  总新闻源: {results['total_sources']}")
        print(f"  成功采集: {results['success_count']}")
        print(f"  采集失败: {results['error_count']}")
        print(f"  新增文章: {results['new_articles']}")
        
        # 显示最新文章
        if results['new_articles'] > 0:
            print(f"\n最新采集的文章:")
            articles = repo.get_recent_articles(days=1)
            for i, article in enumerate(articles[:5], 1):
                print(f"  {i}. {article.title}")
                print(f"     来源: {article.source_name}")
                print(f"     时间: {article.created_at}")
                print(f"     分类: {article.category}")
                print()
        
        return results
        
    except Exception as e:
        print(f"采集过程中出现错误: {e}")
        return None
    finally:
        db.close()


def main():
    """主函数"""
    print("NewsMind 爬虫测试")
    print("=" * 50)
    
    # 运行异步测试
    results = asyncio.run(test_crawler())
    
    if results:
        print("=" * 50)
        print("测试完成!")
        
        if results['new_articles'] > 0:
            print(f"✅ 成功采集到 {results['new_articles']} 篇新文章")
        else:
            print("⚠️  未采集到新文章，可能原因:")
            print("   - 文章已存在（去重机制）")
            print("   - RSS源暂时无更新")
            print("   - 网络连接问题")
    else:
        print("❌ 测试失败")


if __name__ == "__main__":
    main() 