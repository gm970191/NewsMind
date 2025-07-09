#!/usr/bin/env python3
"""
检查文章分布
"""
import sqlite3

def check_articles():
    conn = sqlite3.connect("newsmind.db")
    cursor = conn.cursor()
    
    print("📊 文章来源分布:")
    print("-" * 40)
    
    cursor.execute("""
        SELECT source_name, COUNT(*) as count 
        FROM news_articles 
        GROUP BY source_name 
        ORDER BY count DESC
    """)
    
    for source, count in cursor.fetchall():
        print(f"{source}: {count}篇")
    
    print("\n🌍 国外新闻源文章:")
    print("-" * 40)
    
    cursor.execute("""
        SELECT title, source_name, language 
        FROM news_articles 
        WHERE source_name IN ('CNN', 'BBC News', 'Reuters', 'TechCrunch', 'Bloomberg')
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    articles = cursor.fetchall()
    if articles:
        for title, source, lang in articles:
            print(f"[{source}] {title} ({lang})")
    else:
        print("暂无国外新闻源文章")
    
    conn.close()

if __name__ == "__main__":
    check_articles() 