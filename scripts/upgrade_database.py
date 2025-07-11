#!/usr/bin/env python3
"""
数据库升级脚本：确保 news_articles 表有 category 字段
"""
import sqlite3
import os

def ensure_category_column(db_path):
    print(f"升级数据库: {db_path}")
    if not os.path.exists(db_path):
        print(f"❌ 未找到数据库文件: {db_path}")
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # 检查是否有 category 字段
        cursor.execute("PRAGMA table_info(news_articles)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'category' not in columns:
            cursor.execute("ALTER TABLE news_articles ADD COLUMN category TEXT")
            print("✅ 已添加 category 字段")
        else:
            print("✅ 已存在 category 字段")

        # 检查并添加 translated_title 字段
        cursor.execute("PRAGMA table_info(news_articles)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'translated_title' not in columns:
            print("🔧 添加 translated_title 字段...")
            cursor.execute("ALTER TABLE news_articles ADD COLUMN translated_title VARCHAR(500)")
            print("✅ 已添加 translated_title 字段")
        else:
            print("✅ 已存在 translated_title 字段")
        conn.commit()
    except Exception as e:
        print(f"❌ 升级失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    ensure_category_column("backend/newsmind.db") 