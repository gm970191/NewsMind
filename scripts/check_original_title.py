#!/usr/bin/env python3
"""
检查original_title字段
"""
import sqlite3

def check_original_title():
    """检查original_title字段"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 检查文章62的original_title
        cursor.execute("""
            SELECT id, title, original_title
            FROM news_articles 
            WHERE id = 62
        """)
        
        row = cursor.fetchone()
        if row:
            article_id, title, original_title = row
            print(f"文章ID: {article_id}")
            print(f"标题: {title}")
            print(f"原文标题: {original_title}")
        else:
            print("文章62不存在")
        
    except Exception as e:
        print(f"检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_original_title() 