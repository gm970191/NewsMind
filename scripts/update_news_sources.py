#!/usr/bin/env python3
"""
更新新闻源配置
删除无效新闻源，添加高质量真实新闻源
"""
import sqlite3
from datetime import datetime

def update_news_sources():
    """更新新闻源配置"""
    print("🔄 开始更新新闻源配置...")
    print("=" * 60)
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 清空现有新闻源
        cursor.execute("DELETE FROM news_sources")
        print("🗑️  已清空现有新闻源")
        
        # 定义高质量新闻源
        high_quality_sources = [
            # 英语类主流新闻网站
            ("BBC News", "https://feeds.bbci.co.uk/news/rss.xml", "rss", "国际", 1),
            ("CNN", "https://rsshub.app/cnn", "rss", "国际", 1),
            ("Reuters", "https://www.reutersagency.com/feed/", "rss", "国际", 1),
            ("The Guardian", "https://www.theguardian.com/world/rss", "rss", "国际", 1),
            ("NYTimes", "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", "rss", "国际", 1),
            ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", "rss", "国际", 1),
            ("The Washington Post", "https://feeds.washingtonpost.com/rss/world", "rss", "国际", 1),
            
            # 非英语新闻网站
            ("NHK News", "https://www3.nhk.or.jp/rss/news/cat0.xml", "rss", "国际", 1),
            ("朝日新闻", "https://www.asahi.com/rss/asahi/newsheadlines.rdf", "rss", "国际", 1),
            ("德国之声中文", "https://rss.dw.com/rdf/rss-chi-all", "rss", "国际", 1),
            ("Le Monde", "https://www.lemonde.fr/rss/une.xml", "rss", "国际", 1),
            ("RT News", "https://www.rt.com/rss/news/", "rss", "国际", 1),
            ("Sputnik", "https://sputniknews.com/export/rss2/index.xml", "rss", "国际", 1),
            ("联合国新闻", "https://news.un.org/feed/subscribe/zh/news/all/rss.xml", "rss", "国际", 1),
            
            # 高质量专题类
            ("Google News China", "https://news.google.com/rss/search?q=China", "rss", "国际", 1),
            ("TechCrunch", "https://techcrunch.com/feed/", "rss", "科技", 1),
            ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/", "rss", "科技", 1),
            ("Foreign Policy", "https://foreignpolicy.com/feed/", "rss", "政治", 1),
            ("Defense News", "https://www.defensenews.com/arc/outboundfeeds/rss/", "rss", "军事", 1),
        ]
        
        # 插入高质量新闻源
        for name, url, source_type, category, is_active in high_quality_sources:
            cursor.execute("""
                INSERT INTO news_sources (name, url, type, category, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, url, source_type, category, is_active, datetime.now().isoformat(), datetime.now().isoformat()))
            print(f"✅ 添加: {name} - {url}")
        
        conn.commit()
        print(f"\n📊 更新完成，共添加 {len(high_quality_sources)} 个高质量新闻源")
        
        # 显示更新后的新闻源
        cursor.execute("SELECT id, name, url, type, category FROM news_sources WHERE is_active=1 ORDER BY id")
        sources = cursor.fetchall()
        print(f"\n📋 当前活跃新闻源列表:")
        print("-" * 60)
        for source_id, name, url, source_type, category in sources:
            print(f"ID: {source_id:2d} | {name:20s} | {category:6s} | {source_type:4s} | {url}")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    update_news_sources() 