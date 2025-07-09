"""
Database initialization script
"""
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import create_tables, SessionLocal
from app.services.news_service import NewsRepository
from app.models.news import NewsSource


def init_default_sources():
    """初始化默认新闻源"""
    db = SessionLocal()
    repo = NewsRepository(db)
    
    # 默认新闻源配置（RSS）
    default_sources = [
        {
            "name": "CNN",
            "url": "http://rss.cnn.com/rss/edition.rss",
            "type": "rss",
            "category": "国际",
            "weight": 1.0
        },
        {
            "name": "BBC News",
            "url": "http://feeds.bbci.co.uk/news/rss.xml",
            "type": "rss",
            "category": "国际",
            "weight": 1.0
        },
        {
            "name": "Reuters",
            "url": "http://feeds.reuters.com/reuters/topNews",
            "type": "rss",
            "category": "国际",
            "weight": 1.0
        },
        {
            "name": "TechCrunch",
            "url": "http://feeds.feedburner.com/TechCrunch/",
            "type": "rss",
            "category": "科技",
            "weight": 1.0
        },
        {
            "name": "Bloomberg",
            "url": "https://www.bloomberg.com/feed/podcast/etf-report.xml",
            "type": "rss",
            "category": "财经",
            "weight": 1.0
        }
    ]
    
    # 检查并创建新闻源
    for source_data in default_sources:
        existing = repo.get_source_by_url(source_data["url"])
        if not existing:
            repo.create_source(source_data)
            print(f"Created news source: {source_data['name']}")
        else:
            print(f"News source already exists: {source_data['name']}")
    
    db.close()


def main():
    """主函数"""
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully!")
    
    print("Initializing default news sources...")
    init_default_sources()
    print("Default news sources initialized!")
    
    print("Database initialization completed!")


if __name__ == "__main__":
    main() 