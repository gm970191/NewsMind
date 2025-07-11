#!/usr/bin/env python3
"""
添加original_title字段
"""
import sqlite3

def add_original_title_field():
    """添加original_title字段"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 添加original_title字段
        cursor.execute("ALTER TABLE news_articles ADD COLUMN original_title TEXT")
        print("✅ 已添加original_title字段")
        
        # 为文章62设置原文标题
        original_title = "Trump: 'Very good chance' of Gaza ceasefire this week or next"
        cursor.execute("""
            UPDATE news_articles 
            SET original_title = ?
            WHERE id = 62
        """, (original_title,))
        
        conn.commit()
        print(f"✅ 已为文章62设置原文标题: {original_title}")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_original_title_field() 