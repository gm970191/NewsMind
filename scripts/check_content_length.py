#!/usr/bin/env python3
"""
检查数据库中文章的内容长度
"""
import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import get_db
from app.models.news import NewsArticle

def check_content_length():
    """检查文章内容长度"""
    print("📊 检查文章内容长度...")
    
    db = next(get_db())
    
    try:
        # 获取最新20篇文章
        articles = db.query(NewsArticle).order_by(NewsArticle.created_at.desc()).limit(20).all()
        
        print(f"\n最新{len(articles)}篇文章的内容长度:")
        print("-" * 80)
        
        short_count = 0
        medium_count = 0
        long_count = 0
        
        for article in articles:
            content_length = len(article.original_content or "")
            print(f"ID {article.id:3d}: {content_length:4d} 字符 - {article.original_title[:60]}...")
            
            if content_length < 100:
                short_count += 1
            elif content_length < 500:
                medium_count += 1
            else:
                long_count += 1
        
        print("-" * 80)
        print(f"📈 内容长度统计:")
        print(f"   短文章 (<100字符): {short_count} 篇")
        print(f"   中等文章 (100-500字符): {medium_count} 篇")
        print(f"   长文章 (≥500字符): {long_count} 篇")
        print(f"   总计: {len(articles)} 篇")
        
        # 显示一些有内容的文章示例
        print(f"\n📰 有内容的文章示例:")
        content_articles = [a for a in articles if len(a.original_content or "") > 200]
        for article in content_articles[:3]:
            print(f"\nID {article.id}: {article.original_title}")
            print(f"内容长度: {len(article.original_content)} 字符")
            print(f"内容预览: {article.original_content[:200]}...")
            print("-" * 50)
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_content_length() 