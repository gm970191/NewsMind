#!/usr/bin/env python3
"""
检查文章54的数据库数据
"""
import sqlite3

def check_article_54_db():
    """检查文章54的数据库数据"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 检查文章54
        cursor.execute("""
            SELECT id, title, content, language, is_processed
            FROM news_articles 
            WHERE id = 54
        """)
        
        row = cursor.fetchone()
        if row:
            article_id, title, content, language, is_processed = row
            print(f"文章ID: {article_id}")
            print(f"标题: {title}")
            print(f"语言: {language}")
            print(f"是否已处理: {is_processed}")
            print(f"内容长度: {len(content)} 字符")
            print(f"内容预览: {content[:100]}...")
        else:
            print("文章54不存在")
            return
        
        # 检查处理内容
        cursor.execute("""
            SELECT summary_zh, detailed_summary_zh, original_content_zh,
                   summary_length, detailed_summary_length, original_content_length
            FROM processed_content 
            WHERE article_id = 54
        """)
        
        row = cursor.fetchone()
        if row:
            summary_zh, detailed_summary_zh, original_content_zh, summary_len, detailed_len, original_len = row
            print(f"\n处理内容:")
            print(f"概要: {'有' if summary_zh else '无'}")
            print(f"详细总结: {'有' if detailed_summary_zh else '无'}")
            print(f"原始内容: {'有' if original_content_zh else '无'}")
            print(f"概要长度: {summary_len} 字符")
            print(f"详细总结长度: {detailed_len} 字符")
            print(f"原始内容长度: {original_len} 字符")
            
            if summary_zh:
                print(f"概要预览: {summary_zh[:100]}...")
            if detailed_summary_zh:
                print(f"详细总结预览: {detailed_summary_zh[:100]}...")
            if original_content_zh:
                print(f"原始内容预览: {original_content_zh[:100]}...")
        else:
            print("无处理内容")
        
    except Exception as e:
        print(f"检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_article_54_db() 