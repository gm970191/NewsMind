#!/usr/bin/env python3
"""
检查处理内容脚本
"""
import sqlite3

def check_processed_content():
    """检查处理内容"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 获取最新的处理内容
        cursor.execute("""
            SELECT pc.article_id, na.title, pc.summary_zh, pc.detailed_summary_zh, 
                   pc.original_content_zh, pc.summary_length, pc.detailed_summary_length, pc.original_content_length
            FROM processed_content pc
            JOIN news_articles na ON pc.article_id = na.id
            ORDER BY pc.created_at DESC
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        
        print("📊 最新处理内容检查:")
        print("=" * 60)
        
        for row in results:
            article_id, title, summary_zh, detailed_summary_zh, original_content_zh, summary_length, detailed_summary_length, original_content_length = row
            
            print(f"\n📰 文章ID: {article_id}")
            print(f"标题: {title}")
            print(f"概要长度: {summary_length} 字符")
            print(f"详细总结长度: {detailed_summary_length} 字符")
            print(f"原文长度: {original_content_length} 字符")
            
            if detailed_summary_zh:
                print(f"详细总结预览: {detailed_summary_zh[:100]}...")
            else:
                print("详细总结: 无")
                
            if original_content_zh:
                print(f"原文预览: {original_content_zh[:100]}...")
            else:
                print("原文: 无")
            
            print("-" * 40)
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_processed_content() 