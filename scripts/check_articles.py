#!/usr/bin/env python3
"""
检查数据库中的文章数量
"""
import sqlite3

def check_articles():
    """检查文章数量"""
    print("📊 检查数据库文章数量...")
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 检查文章总数
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        total_count = cursor.fetchone()[0]
        print(f"📰 文章总数: {total_count}")
        
        # 检查最新文章
        cursor.execute("""
            SELECT title, source_name, created_at 
            FROM news_articles 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        latest_articles = cursor.fetchall()
        
        print(f"\n📰 最新文章:")
        for title, source_name, created_at in latest_articles:
            print(f"   - {title[:50]}... ({source_name})")
            print(f"     时间: {created_at}")
        
        # 按来源统计
        cursor.execute("""
            SELECT source_name, COUNT(*) as count 
            FROM news_articles 
            GROUP BY source_name 
            ORDER BY count DESC
        """)
        source_stats = cursor.fetchall()
        
        print(f"\n📊 按来源统计:")
        for source_name, count in source_stats:
            print(f"   {source_name}: {count} 篇")
        
        # 按分类统计
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM news_articles 
            GROUP BY category 
            ORDER BY count DESC
        """)
        category_stats = cursor.fetchall()
        
        print(f"\n📊 按分类统计:")
        for category, count in category_stats:
            print(f"   {category}: {count} 篇")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_articles() 