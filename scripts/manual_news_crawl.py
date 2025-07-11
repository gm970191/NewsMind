#!/usr/bin/env python3
"""
手动新闻采集脚本
用于手动触发新闻采集，解决数据更新问题
"""
import sys
import asyncio
import os
from pathlib import Path
from datetime import datetime

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.services.news_service import NewsRepository
from app.services.crawler import WebCrawler


async def manual_news_crawl():
    """手动触发新闻采集"""
    print("🚀 开始手动新闻采集...")
    print("=" * 50)
    
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        # 获取当前文章数量
        current_articles = repo.get_articles(limit=1000)
        print(f"📊 采集前文章数量: {len(current_articles)}")
        
        # 获取活跃新闻源
        sources = repo.get_active_sources()
        print(f"📰 活跃新闻源数量: {len(sources)}")
        
        if not sources:
            print("❌ 没有找到活跃的新闻源")
            return
        
        # 显示新闻源信息
        print("\n📋 新闻源列表:")
        for source in sources:
            print(f"   - {source.name}: {source.url} ({source.type})")
        
        # 开始采集
        print(f"\n🔄 开始采集新闻...")
        start_time = datetime.now()
        
        async with WebCrawler(repo) as crawler:
            results = await crawler.crawl_news_sources()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 显示采集结果
        print(f"\n📊 采集结果:")
        print(f"   总新闻源: {results['total_sources']}")
        print(f"   成功: {results['success_count']}")
        print(f"   失败: {results['error_count']}")
        print(f"   新文章: {results['new_articles']}")
        print(f"   耗时: {duration:.2f} 秒")
        
        # 获取采集后的文章数量
        new_articles = repo.get_articles(limit=1000)
        print(f"📊 采集后文章数量: {len(new_articles)}")
        print(f"📈 新增文章: {len(new_articles) - len(current_articles)}")
        
        # 显示最新文章
        if results['new_articles'] > 0:
            print(f"\n📰 最新文章:")
            latest_articles = repo.get_articles(limit=5)
            for article in latest_articles:
                print(f"   - {article.title} ({article.source_name})")
                print(f"     时间: {article.created_at}")
                print(f"     内容长度: {len(article.content)} 字符")
                print()
        
        if results['new_articles'] > 0:
            print("✅ 新闻采集成功完成！")
        else:
            print("⚠️  没有采集到新文章")
            
    except Exception as e:
        print(f"❌ 新闻采集失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查是否禁用playwright
    if os.environ.get('DISABLE_PLAYWRIGHT') == '1':
        print("⚠️  Playwright已禁用，将使用简化模式")
        print("💡 建议启用Playwright以获得更好的采集效果")
    else:
        print("✅ Playwright可用")
    
    # 检查数据库连接
    try:
        db = SessionLocal()
        repo = NewsRepository(db)
        sources = repo.get_active_sources()
        print(f"✅ 数据库连接正常，找到 {len(sources)} 个活跃新闻源")
        db.close()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    return True


def main():
    """主函数"""
    print("📰 NewsMind 手动新闻采集工具")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败，请检查配置")
        return
    
    # 运行采集
    asyncio.run(manual_news_crawl())
    
    print("\n✅ 采集完成！")
    print("📍 现在可以访问前端页面查看最新新闻")


if __name__ == "__main__":
    main() 