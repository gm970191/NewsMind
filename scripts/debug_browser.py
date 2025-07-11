#!/usr/bin/env python3
"""
调试浏览器启动和内容提取
"""
import sys
import asyncio
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.services.crawler import WebCrawler
from app.services.news_service import NewsRepository
from app.core.database import SessionLocal

async def debug_browser():
    """调试浏览器启动"""
    print("🔍 调试浏览器启动...")
    
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        # 创建爬虫实例
        crawler = WebCrawler(repo)
        print(f"✅ 爬虫创建成功")
        print(f"   Playwright Available: {crawler._playwright_available}")
        print(f"   Browser: {crawler.browser}")
        print(f"   Page: {crawler.page}")
        
        # 启动浏览器
        print("\n🚀 启动浏览器...")
        await crawler.start_browser()
        print(f"✅ 浏览器启动完成")
        print(f"   Playwright Available: {crawler._playwright_available}")
        print(f"   Browser: {crawler.browser}")
        print(f"   Page: {crawler.page}")
        
        if crawler.page:
            print("\n🔗 测试页面访问...")
            try:
                # 使用一个更简单的网站进行测试
                await crawler.page.goto('https://httpbin.org/html', timeout=30000)
                title = await crawler.page.title()
                print(f"✅ 页面访问成功，标题: {title}")
                
                # 测试内容提取
                print("\n📄 测试内容提取...")
                content = await crawler._get_full_content('https://httpbin.org/html')
                if content:
                    print(f"✅ 内容提取成功")
                    print(f"   内容长度: {len(content)} 字符")
                    print(f"   内容预览: {content[:200]}...")
                else:
                    print("❌ 内容提取失败")
                    
            except Exception as e:
                print(f"❌ 页面访问失败: {e}")
        else:
            print("❌ 浏览器页面未创建")
        
        # 关闭浏览器
        await crawler.close_browser()
        print("\n✅ 浏览器已关闭")
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(debug_browser()) 