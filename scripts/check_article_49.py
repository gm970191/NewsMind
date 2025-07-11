#!/usr/bin/env python3
"""
检查文章49状态
"""
import sqlite3

def check_article_49():
    """检查文章49的状态"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 检查文章49
        cursor.execute("""
            SELECT id, title, content, language, is_processed
            FROM news_articles 
            WHERE id = 49
        """)
        
        article = cursor.fetchone()
        if article:
            article_id, title, content, language, is_processed = article
            print(f"文章ID: {article_id}")
            print(f"标题: {title}")
            print(f"语言: {language}")
            print(f"是否已处理: {is_processed}")
            print(f"内容长度: {len(content)} 字符")
            print(f"内容预览: {content[:100]}...")
        else:
            print("文章49不存在")
            return
        
        # 检查处理内容
        cursor.execute("""
            SELECT summary_zh, detailed_summary_zh, original_content_zh
            FROM processed_content 
            WHERE article_id = 49
        """)
        
        processed = cursor.fetchone()
        if processed:
            summary_zh, detailed_summary_zh, original_content_zh = processed
            print(f"\n处理内容:")
            print(f"概要: {'有' if summary_zh else '无'}")
            print(f"详细总结: {'有' if detailed_summary_zh else '无'}")
            print(f"原文: {'有' if original_content_zh else '无'}")
            
            if detailed_summary_zh:
                print(f"详细总结长度: {len(detailed_summary_zh)} 字符")
                print(f"详细总结预览: {detailed_summary_zh[:100]}...")
            else:
                print("详细总结为空")
        else:
            print("\n无处理内容记录")
        
    except Exception as e:
        print(f"检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_article_49() 