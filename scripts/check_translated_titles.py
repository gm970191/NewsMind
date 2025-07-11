#!/usr/bin/env python3
"""
检查翻译后的标题
"""
import sqlite3

def check_translated_titles():
    """检查翻译后的标题"""
    print("📊 检查翻译后的标题...")
    print("=" * 60)
    
    conn = sqlite3.connect("backend/newsmind.db")
    cursor = conn.cursor()
    
    try:
        # 获取有翻译标题的文章
        cursor.execute("""
            SELECT na.id, na.title, na.language, na.source_name, 
                   pc.translated_title, pc.summary_zh
            FROM news_articles na
            JOIN processed_content pc ON na.id = pc.article_id
            WHERE pc.translated_title IS NOT NULL
            ORDER BY na.created_at DESC
            LIMIT 10
        """)
        
        articles = cursor.fetchall()
        
        print(f"📰 有翻译标题的文章 (共{len(articles)}篇):")
        for article in articles:
            article_id, original_title, language, source_name, translated_title, summary_zh = article
            
            print(f"\n   📝 文章ID: {article_id}")
            print(f"      原文标题: {original_title}")
            print(f"      翻译标题: {translated_title}")
            print(f"      语言: {language}")
            print(f"      来源: {source_name}")
            
            if summary_zh:
                print(f"      中文摘要: {summary_zh[:100]}...")
            else:
                print(f"      中文摘要: 无")
        
        # 统计翻译标题的数量
        cursor.execute("""
            SELECT COUNT(*) 
            FROM processed_content 
            WHERE translated_title IS NOT NULL
        """)
        translated_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM processed_content")
        total_count = cursor.fetchone()[0]
        
        print(f"\n📈 翻译标题统计:")
        print(f"   有翻译标题: {translated_count} 篇")
        print(f"   总处理文章: {total_count} 篇")
        print(f"   翻译率: {translated_count/total_count*100:.1f}%")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_translated_titles() 