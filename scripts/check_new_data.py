#!/usr/bin/env python3
"""
检查新数据
"""
import sqlite3

def check_new_data():
    """检查新数据"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 获取最新文章
        cursor.execute("""
            SELECT id, title, source_name, category, language, content_length, created_at
            FROM news_articles 
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        articles = cursor.fetchall()
        
        print("📊 最新文章数据:")
        print("=" * 60)
        
        for article in articles:
            article_id, title, source_name, category, language, content_length, created_at = article
            print(f"\n📰 文章ID: {article_id}")
            print(f"标题: {title}")
            print(f"来源: {source_name}")
            print(f"分类: {category}")
            print(f"语言: {language}")
            print(f"内容长度: {content_length} 字符")
            print(f"创建时间: {created_at}")
            print("-" * 40)
        
        print(f"\n✅ 总共 {len(articles)} 篇文章")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_new_data() 