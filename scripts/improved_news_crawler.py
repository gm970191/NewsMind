#!/usr/bin/env python3
"""
改进的新闻采集测试脚本
用于测试真实新闻源的采集和内容获取
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


async def test_real_news_crawling():
    """测试真实新闻采集"""
    print("🔍 测试真实新闻采集...")
    
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        # 创建一些真实的新闻源进行测试
        test_sources = [
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
            }
        ]
        
        # 添加测试新闻源
        for source_data in test_sources:
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
        
        # 测试新闻采集
        print("\n🚀 开始新闻采集测试...")
        async with WebCrawler(repo) as crawler:
            results = await crawler.crawl_news_sources()
            
            print(f"\n📊 采集结果:")
            print(f"   总新闻源: {results['total_sources']}")
            print(f"   成功: {results['success_count']}")
            print(f"   失败: {results['error_count']}")
            print(f"   新文章: {results['new_articles']}")
        
        # 显示采集到的文章
        print("\n📰 采集到的文章:")
        articles = repo.get_articles(limit=10)
        for article in articles:
            content_preview = article.content[:100] + "..." if len(article.content) > 100 else article.content
            print(f"   ID: {article.id}")
            print(f"   标题: {article.title}")
            print(f"   来源: {article.source_name}")
            print(f"   链接: {article.source_url}")
            print(f"   内容预览: {content_preview}")
            print(f"   内容长度: {len(article.content)} 字符")
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        db.close()


async def test_content_extraction():
    """测试内容提取功能"""
    print("\n🔍 测试内容提取功能...")
    
    # 测试URL列表
    test_urls = [
        'https://www.bbc.com/news/world-us-canada-68835600',
        'https://techcrunch.com/2024/01/15/ai-startup-funding-2024/',
        'https://www.reuters.com/technology/ai-regulation-2024-01-15/'
    ]
    
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        async with WebCrawler(repo) as crawler:
            for url in test_urls:
                print(f"\n🔗 测试URL: {url}")
                try:
                    content = await crawler._get_full_content(url)
                    if content:
                        print(f"   ✓ 成功提取内容")
                        print(f"   内容长度: {len(content)} 字符")
                        print(f"   内容预览: {content[:200]}...")
                    else:
                        print(f"   ✗ 提取失败")
                except Exception as e:
                    print(f"   ✗ 提取错误: {e}")
    
    except Exception as e:
        print(f"❌ 内容提取测试失败: {e}")
    finally:
        db.close()


def main():
    """主函数"""
    print("🚀 改进的新闻采集测试")
    print("=" * 50)
    
    # 检查环境
    if os.environ.get('DISABLE_PLAYWRIGHT') == '1':
        print("⚠️  Playwright已禁用，将使用简化模式")
    else:
        print("✅ Playwright可用，将使用完整模式")
    
    # 运行测试
    asyncio.run(test_real_news_crawling())
    asyncio.run(test_content_extraction())
    
    print("\n✅ 测试完成！")


if __name__ == "__main__":
    main() 