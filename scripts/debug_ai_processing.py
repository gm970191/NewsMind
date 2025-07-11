#!/usr/bin/env python3
"""
调试AI处理数据
"""
import sqlite3

def debug_ai_processing():
    """调试AI处理数据"""
    print("🔍 调试AI处理数据...")
    print("=" * 60)
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 检查最新的处理记录
        cursor.execute("""
            SELECT na.id, na.title, na.language, na.is_processed,
                   pc.summary_zh, pc.translated_title, pc.detailed_summary_zh
            FROM news_articles na
            LEFT JOIN processed_content pc ON na.id = pc.article_id
            WHERE na.is_processed = 1
            ORDER BY na.created_at DESC
            LIMIT 5
        """)
        
        articles = cursor.fetchall()
        
        print(f"📰 最新处理记录:")
        for article in articles:
            article_id, title, language, is_processed, summary_zh, translated_title, detailed_summary_zh = article
            
            print(f"\n   📝 文章ID: {article_id}")
            print(f"      原文标题: {title}")
            print(f"      语言: {language}")
            print(f"      已处理: {is_processed}")
            print(f"      中文摘要: {summary_zh[:50] if summary_zh else '无'}...")
            print(f"      翻译标题: {translated_title if translated_title else '无'}")
            print(f"      详细总结: {detailed_summary_zh[:50] if detailed_summary_zh else '无'}...")
        
        # 检查processed_content表结构
        cursor.execute("PRAGMA table_info(processed_content)")
        columns = cursor.fetchall()
        print(f"\n📋 processed_content表字段:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 检查是否有translated_title数据
        cursor.execute("""
            SELECT COUNT(*) 
            FROM processed_content 
            WHERE translated_title IS NOT NULL AND translated_title != ''
        """)
        translated_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM processed_content")
        total_count = cursor.fetchone()[0]
        
        print(f"\n📈 翻译标题统计:")
        print(f"   有翻译标题: {translated_count} 篇")
        print(f"   总处理文章: {total_count} 篇")
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_ai_processing() 