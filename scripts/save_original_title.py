#!/usr/bin/env python3
"""
保存原文标题
"""
import sqlite3
from datetime import datetime

def save_original_title():
    """保存原文标题"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 为文章62保存原文标题
        original_title = "Trump: 'Very good chance' of Gaza ceasefire this week or next"
        
        # 更新文章，添加原文标题字段
        cursor.execute("""
            UPDATE news_articles 
            SET original_title = ?, updated_at = ?
            WHERE id = 62
        """, (original_title, datetime.now().isoformat()))
        
        conn.commit()
        print(f"✅ 已保存原文标题: {original_title}")
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    save_original_title() 