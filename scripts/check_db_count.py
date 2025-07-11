#!/usr/bin/env python3
import sqlite3
import os

def check_count(db_path):
    print(f"\n数据库: {os.path.abspath(db_path)}")
    if not os.path.exists(db_path):
        print("❌ 文件不存在")
        return
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        count = cursor.fetchone()[0]
        print(f"news_articles 表数据量: {count}")
        conn.close()
    except Exception as e:
        print(f"❌ 查询失败: {e}")

if __name__ == "__main__":
    check_count("newsmind.db")
    check_count("backend/newsmind.db") 