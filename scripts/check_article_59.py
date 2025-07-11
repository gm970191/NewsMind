#!/usr/bin/env python3
import sqlite3
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_article_59():
    """检查文章59的详细信息"""
    try:
        conn = sqlite3.connect('backend/newsmind.db')
        cursor = conn.cursor()
        
        # 先检查数据库结构
        cursor.execute('PRAGMA table_info(news_articles)')
        columns = cursor.fetchall()
        print("📋 数据库字段:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 检查文章59是否存在
        cursor.execute('SELECT * FROM news_articles WHERE id = 59')
        result = cursor.fetchone()
        
        if result:
            print(f"\n📰 文章59详情:")
            print(f"ID: {result[0]}")
            print(f"标题: {result[1]}")
            print(f"内容长度: {len(result[2]) if result[2] else 0}")
            print(f"URL: {result[3]}")
            print(f"来源: {result[4]}")
            print(f"分类: {result[5]}")
            print(f"发布时间: {result[6]}")
            print(f"原始内容长度: {len(result[7]) if result[7] else 0}")
            print(f"翻译内容长度: {len(result[8]) if result[8] else 0}")
            
            # 检查是否有AI处理记录
            cursor.execute('SELECT * FROM processed_content WHERE article_id = 59')
            ai_result = cursor.fetchone()
            if ai_result:
                print("✅ 有AI处理记录")
            else:
                print("❌ 无AI处理记录")
                
        else:
            print("❌ 文章59不存在")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_article_59() 