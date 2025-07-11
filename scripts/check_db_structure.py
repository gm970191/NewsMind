#!/usr/bin/env python3
"""
检查数据库结构脚本
"""
import sqlite3
import os

def check_db_structure():
    """检查数据库结构"""
    db_path = "backend/newsmind.db"
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📊 数据库表结构:")
        for table in tables:
            table_name = table[0]
            print(f"\n📋 表: {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"   {col_name} ({col_type})")
        
        # 检查文章数量
        for table in tables:
            table_name = table[0]
            if 'article' in table_name.lower() or 'news' in table_name.lower():
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"\n📈 {table_name} 表记录数: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查数据库结构失败: {e}")

if __name__ == "__main__":
    check_db_structure() 