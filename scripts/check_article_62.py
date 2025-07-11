#!/usr/bin/env python3
"""
检查文章62状态
"""
import sqlite3

def check_article_62():
    """检查文章62的状态"""
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 检查文章62
        cursor.execute("""
            SELECT id, title, content, language, is_processed
            FROM news_articles 
            WHERE id = 62
        """)
        
        article = cursor.fetchone()
        if article:
            article_id, title, content, language, is_processed = article
            print(f"文章ID: {article_id}")
            print(f"标题: {title}")
            print(f"语言: {language}")
            print(f"是否已处理: {is_processed}")
            print(f"内容长度: {len(content)} 字符")
            print(f"内容预览: {content[:200]}...")
        else:
            print("文章62不存在")
            return
        
        # 检查处理内容
        cursor.execute("""
            SELECT summary_zh, detailed_summary_zh, original_content_zh
            FROM processed_content 
            WHERE article_id = 62
        """)
        
        processed = cursor.fetchone()
        if processed:
            summary_zh, detailed_summary_zh, original_content_zh = processed
            print(f"\n处理内容:")
            print(f"概要: {'有' if summary_zh else '无'}")
            print(f"详细总结: {'有' if detailed_summary_zh else '无'}")
            print(f"原文: {'有' if original_content_zh else '无'}")
            
            if summary_zh:
                print(f"概要预览: {summary_zh[:100]}...")
            if detailed_summary_zh:
                print(f"详细总结预览: {detailed_summary_zh[:100]}...")
        else:
            print("\n无处理内容记录")
        
    except Exception as e:
        print(f"检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_article_62() 