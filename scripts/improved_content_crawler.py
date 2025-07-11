#!/usr/bin/env python3
"""
改进的内容爬虫脚本
专门用于抓取有完整内容的新闻
"""
import sys
import asyncio
import os
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.services.news_service import NewsRepository
from app.services.crawler import WebCrawler
from app.models.news import NewsSource


async def crawl_with_full_content():
    """抓取有完整内容的新闻"""
    print("🔍 开始抓取有完整内容的新闻...")
    
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        # 创建一些高质量新闻源
        quality_sources = [
            {
                'name': 'BBC News',
                'url': 'https://www.bbc.com/news',
                'type': 'web',
                'category': '国际',
                'weight': 1.0,
                'is_active': True
            },
            {
                'name': 'Reuters',
                'url': 'https://www.reuters.com',
                'type': 'web',
                'category': '国际',
                'weight': 1.0,
                'is_active': True
            },
            {
                'name': 'TechCrunch',
                'url': 'https://techcrunch.com',
                'type': 'web',
                'category': '科技',
                'weight': 1.0,
                'is_active': True
            },
            {
                'name': 'CNN',
                'url': 'https://www.cnn.com',
                'type': 'web',
                'category': '国际',
                'weight': 1.0,
                'is_active': True
            }
        ]
        
        # 添加高质量新闻源
        for source_data in quality_sources:
            try:
                # 检查是否已存在
                existing = repo.get_source_by_url(source_data['url'])
                if not existing:
                    repo.create_source(source_data)
                    print(f"✓ 添加新闻源: {source_data['name']}")
                else:
                    print(f"⚠ 新闻源已存在: {source_data['name']}")
            except Exception as e:
                print(f"✗ 添加新闻源失败: {e}")
        
        # 使用改进的爬虫抓取新闻
        print("\n🚀 开始新闻采集...")
        async with WebCrawler(repo) as crawler:
            results = await crawler.crawl_news_sources()
            
            print(f"\n📊 采集结果:")
            print(f"   总新闻源: {results['total_sources']}")
            print(f"   成功: {results['success_count']}")
            print(f"   失败: {results['error_count']}")
            print(f"   新文章: {results['new_articles']}")
        
        # 显示采集到的文章详情
        print("\n📰 采集到的文章详情:")
        articles = repo.get_articles(limit=20, order_by='created_at DESC')
        for article in articles:
            content_length = len(article.original_content) if article.original_content else 0
            print(f"   ID: {article.id}")
            print(f"   标题: {article.original_title}")
            print(f"   来源: {article.source_name}")
            print(f"   内容长度: {content_length} 字符")
            if content_length > 0:
                content_preview = article.original_content[:100] + "..." if content_length > 100 else article.original_content
                print(f"   内容预览: {content_preview}")
            else:
                print(f"   内容预览: [无内容]")
            print("-" * 50)
        
        # 统计内容长度分布
        print("\n📈 内容长度统计:")
        short_articles = [a for a in articles if len(a.original_content or '') < 100]
        medium_articles = [a for a in articles if 100 <= len(a.original_content or '') < 500]
        long_articles = [a for a in articles if len(a.original_content or '') >= 500]
        
        print(f"   短文章 (<100字符): {len(short_articles)} 篇")
        print(f"   中等文章 (100-500字符): {len(medium_articles)} 篇")
        print(f"   长文章 (≥500字符): {len(long_articles)} 篇")
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    """主函数"""
    print("🚀 改进的内容爬虫")
    print("=" * 50)
    
    # 运行抓取
    asyncio.run(crawl_with_full_content())
    
    print("\n✅ 抓取完成！")


if __name__ == "__main__":
    main() 