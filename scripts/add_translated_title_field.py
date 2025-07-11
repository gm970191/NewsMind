#!/usr/bin/env python3
"""
添加translated_title字段到processed_content表
"""
import sqlite3

def add_translated_title_field():
    """添加translated_title字段"""
    print("🔧 添加translated_title字段到processed_content表...")
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(processed_content)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'translated_title' not in columns:
            # 添加translated_title字段
            cursor.execute("ALTER TABLE processed_content ADD COLUMN translated_title TEXT")
            print("✅ 成功添加translated_title字段")
        else:
            print("ℹ️  translated_title字段已存在")
        
        # 检查字段是否添加成功
        cursor.execute("PRAGMA table_info(processed_content)")
        columns = cursor.fetchall()
        print("\n📋 processed_content表字段:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ 添加字段失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_translated_title_field() 