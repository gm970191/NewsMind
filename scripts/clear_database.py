#!/usr/bin/env python3
"""
清空 backend/newsmind.db 的新闻相关表（历史+模拟数据）
"""
import sqlite3
import os

def clear_all_news_tables(db_path):
    print(f"⚠️  即将彻底清空 {db_path} 的新闻相关表...")
    if not os.path.exists(db_path):
        print(f"❌ 未找到数据库文件: {db_path}")
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        for table in ["news_articles", "processed_content"]:
            cursor.execute(f"DELETE FROM {table}")
            print(f"✅ 已清空 {table} 表")
        conn.commit()
        for table in ["news_articles", "processed_content"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table} 剩余数据量: {count}")
    except Exception as e:
        print(f"❌ 清空失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clear_all_news_tables("backend/newsmind.db") 