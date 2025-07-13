#!/usr/bin/env python3
"""
创建测试数据
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.news import NewsSource, NewsArticle
from datetime import datetime

def create_test_data():
    """创建测试数据"""
    db = SessionLocal()
    
    try:
        # 添加更多可靠的新闻源
        sources = [
            {
                'name': 'BBC News',
                'url': 'http://feeds.bbci.co.uk/news/rss.xml',
                'type': 'rss',
                'category': '国际'
            },
            {
                'name': 'CNN',
                'url': 'http://rss.cnn.com/rss/edition.rss',
                'type': 'rss',
                'category': '国际'
            },
            {
                'name': 'TechCrunch',
                'url': 'http://feeds.feedburner.com/TechCrunch/',
                'type': 'rss',
                'category': '科技'
            },
            {
                'name': 'Ars Technica',
                'url': 'http://feeds.arstechnica.com/arstechnica/index',
                'type': 'rss',
                'category': '科技'
            },
            {
                'name': 'The Verge',
                'url': 'https://www.theverge.com/rss/index.xml',
                'type': 'rss',
                'category': '科技'
            }
        ]
        
        for source_data in sources:
            # 检查是否已存在
            existing = db.query(NewsSource).filter(NewsSource.url == source_data['url']).first()
            if not existing:
                source = NewsSource(**source_data)
                db.add(source)
                print(f"添加新闻源: {source_data['name']}")
        
        # 添加一些测试文章
        test_articles = [
            {
                'original_title': 'AI Technology Advances in 2024',
                'original_content': 'Artificial intelligence has made significant progress this year with new breakthroughs in machine learning and natural language processing.',
                'original_language': 'en',
                'source_url': 'https://example.com/ai-advances-2024',
                'source_id': 1,
                'source_name': 'BBC News',
                'category': '科技',
                'is_processed': True,
                'summary_zh': '2024年人工智能技术取得重大进展，在机器学习和自然语言处理方面有新的突破。'
            },
            {
                'original_title': 'Global Economic Recovery Continues',
                'original_content': 'The global economy shows signs of continued recovery with improved GDP growth across major economies.',
                'original_language': 'en',
                'source_url': 'https://example.com/economic-recovery',
                'source_id': 1,
                'source_name': 'BBC News',
                'category': '财经',
                'is_processed': True,
                'summary_zh': '全球经济继续复苏，主要经济体GDP增长改善。'
            },
            {
                'original_title': 'New Space Exploration Mission Launched',
                'original_content': 'A new space exploration mission has been launched to study distant planets and search for signs of life.',
                'original_language': 'en',
                'source_url': 'https://example.com/space-mission',
                'source_id': 2,
                'source_name': 'CNN',
                'category': '科技',
                'is_processed': True,
                'summary_zh': '新的太空探索任务已启动，将研究遥远行星并寻找生命迹象。'
            }
        ]
        
        for article_data in test_articles:
            # 检查是否已存在
            existing = db.query(NewsArticle).filter(NewsArticle.source_url == article_data['source_url']).first()
            if not existing:
                article = NewsArticle(**article_data)
                db.add(article)
                print(f"添加测试文章: {article_data['original_title']}")
        
        db.commit()
        print("测试数据创建完成！")
        
    except Exception as e:
        print(f"创建测试数据时出错: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data() 