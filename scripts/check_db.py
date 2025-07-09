#!/usr/bin/env python3
"""
检查数据库中的新闻数据
"""
import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.services.news_service import NewsRepository


def check_database():
    """检查数据库内容"""
    print("=== 检查数据库内容 ===")
    
    db = SessionLocal()
    repo = NewsRepository(db)
    
    try:
        # 检查新闻源
        sources = repo.get_active_sources()
        print(f"新闻源数量: {len(sources)}")
        for source in sources:
            print(f"  - {source.name} ({source.type}): {source.url}")
        
        print()
        
        # 检查文章
        articles = repo.get_articles(limit=10)
        print(f"文章总数: {len(articles)}")
        print("最新文章:")
        for i, article in enumerate(articles[:5], 1):
            print(f"  {i}. {article.title}")
            print(f"     来源: {article.source_name}")
            print(f"     分类: {article.category}")
            print(f"     时间: {article.created_at}")
            print(f"     链接: {article.source_url}")
            print()
        
        # 检查统计信息
        stats = repo.get_statistics()
        print("统计信息:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"检查数据库时出错: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    check_database() 